"""AI-powered analysis for diary entries."""

import re
from typing import List, Optional

from .ollama_client import ollama_client
from .entry_manager import entry_manager


class AnalysisEngine:
    """Handles AI-powered analysis of diary entries."""
    
    def __init__(self):
        self._theme_cache = {}
    
    async def extract_themes_and_topics(self, content: str) -> List[str]:
        """Extract key themes from diary entry content."""
        content_without_links = re.sub(
            r"\*\*Related entries:\*\*.*$", "", content, flags=re.DOTALL
        )

        if len(content_without_links.strip()) < 20:
            return []

        prompt = f"""Analyze this journal entry and extract 3-5 key themes or topics.

Entry content: {content}

Return ONLY the themes as a simple comma-separated list with no other text:
friendship, work-stress, creativity"""

        try:
            print("🤖 Attempting theme extraction with Ollama...")
            response_text = await ollama_client.generate(
                prompt, 
                "You are an expert at identifying key themes in personal writing. Extract the most meaningful concepts."
            )
            print("✅ Ollama theme extraction successful!")
        except Exception as e:
            print(f"❌ Ollama theme extraction failed: {e}")
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
        """Find related entries using cached theme analysis."""
        current_themes = set(await self.get_themes_cached(current_content, exclude_date or "current"))

        if not current_themes:
            return []

        entries = entry_manager.get_all_entries()
        similarity_scores = []

        print(f"🔍 Analyzing {len(entries)} entries with cached themes...")
        
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
            print(f"✅ Found {len(backlinks)} cognitive connections")
        
        return backlinks
    
    async def generate_reflection_prompts(
        self, 
        recent_content: str, 
        focus: Optional[str] = None, 
        count: int = 3, 
        is_sunday: bool = False
    ) -> List[str]:
        """Generate reflection prompts based on recent content."""
        if len(recent_content.strip()) < 20:
            return []

        focus_instruction = ""
        if focus:
            focus_instruction = f"\n\nSPECIAL FOCUS: Generate questions specifically related to {focus}. Tailor the questions to help explore this area deeply."
        
        weekly_instruction = ""
        if is_sunday:
            weekly_instruction = "\n\nThis is a Sunday reflection - focus on synthesizing insights from the past week and setting intentions for alignment and refocusing in the upcoming week."

        prompt = f"""Based on this recent journal content, generate {count} intellectually rigorous questions for deep cognitive exploration. These should be the kind of questions a philosopher, or systems thinker would ask.{focus_instruction}{weekly_instruction}

        Recent content:
        {recent_content[:800]}
        
        Create questions that:
        - Probe underlying assumptions, mental models, and cognitive patterns
        - Explore systems, interconnections, and deeper mechanisms
        - Challenge surface-level thinking with analytical depth
        - Connect personal experience to broader philosophical concepts
        - Encourage meta-cognitive awareness and intellectual rigor
        {"- Focus on weekly synthesis and upcoming alignment (Sunday reflection)" if is_sunday else ""}
        
        Format as numbered questions without additional text:
        {chr(10).join([f"{i}. [sophisticated analytical question]" for i in range(1, count + 1)])}"""

        try:
            print("🤖 Attempting LLM generation with Ollama...")
            response_text = await ollama_client.generate(
                prompt, 
                "You are an expert philosopher and cognitive scientist. Generate intellectually rigorous questions that probe deep patterns, assumptions, and cognitive mechanisms."
            )
            print("✅ Ollama generation successful!")
        except Exception as e:
            print(f"❌ Ollama generation failed: {e}")
            print("💡 Tip: Install Ollama and run: ollama pull llama3.1")
            return []

        prompts = []
        for line in response_text.split("\n"):
            line = line.strip()
            if line and (
                line.startswith(("1.", "2.", "3.", "4.", "5.")) or line.startswith("-")
            ):
                clean_prompt = re.sub(r"^[\d\-\.\s]+", "", line).strip()
                if clean_prompt:
                    prompts.append(clean_prompt)

        return prompts[:count]


analysis_engine = AnalysisEngine()