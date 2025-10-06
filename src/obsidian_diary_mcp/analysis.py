"""AI-powered analysis for diary entries."""

import re
from typing import List, Optional

from .ollama_client import ollama_client
from .entry_manager import entry_manager
from .logger import analysis_logger as logger, log_section


class AnalysisEngine:
    """Handles AI-powered analysis of diary entries."""
    
    def __init__(self):
        self._theme_cache = {}
    
    def _extract_brain_dump(self, content: str) -> str:
        """Extract the Brain Dump section which contains actual reflections (not prompts)."""
        # Try to find Brain Dump section
        brain_dump_match = re.search(
            r'##\s*(?:💭\s*)?Brain Dump\s*\n+(.*?)(?=\n##|\Z)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if brain_dump_match:
            brain_dump = brain_dump_match.group(1).strip()
            # Remove placeholder text
            brain_dump = re.sub(
                r'\*Your thoughts, experiences, and observations\.\.\.\*',
                '',
                brain_dump
            ).strip()
            return brain_dump
        
        return ""
    
    async def extract_themes_and_topics(self, content: str) -> List[str]:
        """Extract key themes from diary entry content, prioritizing Brain Dump section."""
        # First, try to extract just the Brain Dump (actual reflections, not prompts)
        brain_dump = self._extract_brain_dump(content)
        
        # If we have substantial brain dump content, prioritize it
        if len(brain_dump) > 50:
            analysis_content = brain_dump
            logger.debug(f"Analyzing Brain Dump section ({len(brain_dump)} chars)")
        else:
            # Fallback to full content but remove links section
            analysis_content = re.sub(
                r"\*\*Related entries:\*\*.*$", "", content, flags=re.DOTALL
            )
            analysis_content = re.sub(
                r"##\s*🔗\s*Memory Links.*$", "", analysis_content, flags=re.DOTALL
            )
            logger.debug("No substantial Brain Dump found, analyzing full entry")

        if len(analysis_content.strip()) < 20:
            return []

        prompt = f"""Analyze this journal entry and extract 3-5 key themes or topics.

Entry content: {analysis_content}

Return ONLY the themes as a simple comma-separated list with no other text:
friendship, work-stress, creativity"""

        try:
            logger.debug("Extracting themes with Ollama...")
            response_text = await ollama_client.generate(
                prompt, 
                "You are an expert at identifying key themes in personal writing. Extract the most meaningful concepts."
            )
            logger.debug("Theme extraction successful")
        except Exception as e:
            logger.error(f"Theme extraction failed: {e}")
            return []
        
        themes = [
            theme.strip().lower()
            for theme in response_text.strip().split(",")
            if theme.strip()
        ]
        return themes[:5]
    
    async def get_themes_cached(self, content: str, file_stem: str) -> List[str]:
        """Get themes for content with caching to avoid redundant AI calls."""
        cache_key = f"{file_stem}_{len(content)}_{hash(content[:100])}"
        
        if cache_key in self._theme_cache:
            return self._theme_cache[cache_key]
        
        themes = await self.extract_themes_and_topics(content)
        self._theme_cache[cache_key] = themes
        return themes
    
    def generate_topic_tags(self, themes: List[str]) -> List[str]:
        """Convert themes to Obsidian-compatible topic tags."""
        if not themes:
            return []
        
        topic_tags = []
        for theme in themes:
            if 'key themes' in theme.lower() or 'extracted from' in theme.lower():
                parts = re.split(r'[:\n•\-]', theme)
                for part in parts:
                    clean_part = part.strip()
                    if clean_part and len(clean_part) < 50 and not any(skip in clean_part.lower() for skip in ['key themes', 'extracted', 'journal entry']):
                        clean_theme = re.sub(r'[^\w\s-]', '', clean_part.lower())
                        clean_theme = re.sub(r'\s+', '-', clean_theme.strip())
                        if clean_theme:
                            topic_tags.append(f'#{clean_theme}')
            else:
                clean_theme = re.sub(r'[^\w\s-]', '', theme.lower())
                clean_theme = re.sub(r'\s+', '-', clean_theme.strip())
                clean_theme = clean_theme.replace('/', '-')
                if clean_theme:
                    topic_tags.append(f'#{clean_theme}')
        
        return topic_tags
    
    async def find_related_entries(
        self,
        current_content: str,
        exclude_date: Optional[str] = None,
        max_related: int = 6,
    ) -> List[str]:
        """Find related entries using cached theme analysis (prioritizes Brain Dump content)."""
        current_themes = set(await self.get_themes_cached(current_content, exclude_date or "current"))

        if not current_themes:
            return []

        entries = entry_manager.get_all_entries()
        similarity_scores = []

        logger.info(f"Finding related entries based on themes: {', '.join(list(current_themes)[:3])}")
        logger.debug(f"Analyzing {len(entries)} entries for connections")
        
        for date, file_path in entries:
            if exclude_date and file_path.stem == exclude_date:
                continue

            entry_content = entry_manager.read_entry(file_path)
            if entry_content.startswith("Error reading file"):
                continue
                
            entry_themes = set(await self.get_themes_cached(entry_content, file_path.stem))

            if entry_themes:
                similarity = len(current_themes & entry_themes) / len(
                    current_themes | entry_themes
                )
                
                if similarity > 0.08:
                    similarity_scores.append((similarity, file_path.stem))

        similarity_scores.sort(reverse=True, key=lambda x: x[0])
        
        backlinks = [f"[[{stem}]]" for _, stem in similarity_scores[:max_related]]
        
        if backlinks:
            logger.info(f"✓ Found {len(backlinks)} cognitive connections")
        
        return backlinks
    
    async def generate_reflection_prompts(
        self, 
        recent_content: str, 
        focus: Optional[str] = None, 
        count: int = 3, 
        is_sunday: bool = False
    ) -> List[str]:
        """Generate reflection prompts based on recent content."""
        log_section(logger, "Generate Reflection Prompts")
        logger.info(f"Input: {len(recent_content):,} chars | Count: {count} | Sunday: {is_sunday} | Focus: {focus or 'None'}")
        
        if len(recent_content.strip()) < 20:
            logger.warning("Content too short (<20 chars), returning empty")
            return []

        focus_instruction = ""
        if focus:
            focus_instruction = f"\n\nFocus specifically on {focus} for all questions."
        
        weekly_instruction = ""
        if is_sunday:
            weekly_instruction = "\n\nThis is a Sunday reflection - synthesize the past week and set intentions for the week ahead."

        # Use full content - don't truncate (the AI can handle it and needs full context)
        prompt = f"""Read through these journal entries and generate {count} thoughtful reflection questions. Pay special attention to the MOST RECENT entry.{focus_instruction}{weekly_instruction}

Journal entries (most recent first):
{recent_content}

Your task:
- Focus primarily on themes and concerns from the MOST RECENT ENTRY
- Use earlier entries for context, but prioritize what's freshest on their mind
- Identify areas that seem unresolved, in transition, or worth exploring deeper
- Generate {count} questions about DIFFERENT topics - spread them across the variety of themes
- Write questions that are DIRECT, CONVERSATIONAL, and PERSONAL
  ✓ Good: "What's making you feel stuck with the Python role right now?"
  ✗ Bad: "The person is considering a role focused on GitHub Copilot..."
- Use "you" and "your" - speak directly to them
- Ask about specific situations and feelings, not summaries
- Each question should address a different area of their life

Format as numbered questions ONLY (no commentary, no summaries, just questions):
{chr(10).join([f"{i}. [question]" for i in range(1, count + 1)])}"""

        logger.debug(f"Prompt size: {len(prompt):,} chars | Preview: {prompt[:100]}...")
        
        try:
            logger.info("Calling Ollama API for prompt generation...")
            response_text = await ollama_client.generate(
                prompt, 
                "You are a perceptive journaling coach who asks direct, personal questions. Generate questions in second person (you/your), not third person summaries. Focus on the most recent entry while using older entries for context. Be conversational and specific - like a thoughtful friend asking about what's currently on their mind. CRITICAL: Output ONLY numbered questions, no other text."
            )
            logger.info(f"Received response: {len(response_text)} chars")
            logger.debug(f"Full response: {response_text}")
        except Exception as e:
            logger.error(f"Ollama call failed ({type(e).__name__}): {e}")
            logger.info("Tip: Install Ollama and run: ollama pull llama3.1")
            return []

        logger.debug("Parsing prompts from response...")
        prompts = []
        for line in response_text.split("\n"):
            line = line.strip()
            # Skip commentary/headers
            if any(skip in line.lower() for skip in ['unresolved', 'worth exploring', 'here are', '**', 'topics:', 'questions:']):
                continue
            
            if line and (
                line.startswith(("1.", "2.", "3.", "4.", "5.")) or line.startswith("-")
            ):
                clean_prompt = re.sub(r"^[\d\-\.\s]+", "", line).strip()
                # Only accept if it's a question or a clear statement
                if clean_prompt and (clean_prompt.endswith("?") or len(clean_prompt) > 20):
                    logger.debug(f"  ✓ {clean_prompt[:60]}...")
                    prompts.append(clean_prompt)

        logger.info(f"✓ Extracted {len(prompts)} prompts (returning first {count})")
        return prompts[:count]
    
    async def extract_todos(self, content: str) -> List[str]:
        """Extract action items and todos from diary entry content."""
        log_section(logger, "Extract Todos")
        logger.info(f"Analyzing content: {len(content):,} chars")
        
        if len(content.strip()) < 20:
            logger.warning("Content too short (<20 chars), returning empty")
            return []
        
        # Extract brain dump section for better context
        brain_dump = self._extract_brain_dump(content)
        analysis_content = brain_dump if len(brain_dump) > 50 else content
        
        prompt = f"""Analyze this journal entry and extract ALL action items, tasks, and todos mentioned.

Journal entry:
{analysis_content}

Your task:
- Identify any tasks, action items, or things the person needs/wants to do
- Include both explicit todos ("I need to...", "I should...") and implicit ones (unfinished work, intentions, goals)
- Be specific and actionable
- Extract the person's own words where possible
- If there are no clear action items, return "No action items found"

Format as a simple bulleted list with one action per line:
- [Action item 1]
- [Action item 2]
- [Action item 3]

IMPORTANT: Only output the bulleted list, no other text or commentary."""
        
        logger.debug(f"Prompt size: {len(prompt):,} chars")
        
        try:
            logger.info("Calling Ollama API for todo extraction...")
            response_text = await ollama_client.generate(
                prompt,
                "You are a helpful assistant that extracts action items from journal entries. Be thorough but focused on actionable tasks. Output ONLY a bulleted list of action items, nothing else."
            )
            logger.info(f"Received response: {len(response_text)} chars")
            logger.debug(f"Full response: {response_text}")
        except Exception as e:
            logger.error(f"Ollama call failed ({type(e).__name__}): {e}")
            return []
        
        # Check for "no action items" response
        if "no action items" in response_text.lower():
            logger.info("No action items found in entry")
            return []
        
        logger.debug("Parsing todos from response...")
        todos = []
        for line in response_text.split("\n"):
            line = line.strip()
            # Skip headers or meta-commentary
            if any(skip in line.lower() for skip in ['action items:', 'tasks:', 'todos:', 'here are']):
                continue
            
            if line and (line.startswith("-") or line.startswith("*") or line.startswith("•")):
                clean_todo = re.sub(r"^[\-\*•\s]+", "", line).strip()
                if clean_todo and len(clean_todo) > 3:
                    logger.debug(f"  ✓ {clean_todo[:60]}...")
                    todos.append(clean_todo)
        
        logger.info(f"✓ Extracted {len(todos)} action items")
        return todos


analysis_engine = AnalysisEngine()