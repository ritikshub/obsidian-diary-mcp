import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
import re

from fastmcp import FastMCP
import httpx

# Initialize FastMCP server
mcp = FastMCP("obsidian-diary")

# Test Ollama availability on startup
try:
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:latest")  # Use available model
    httpx.get(f"{ollama_url}/api/tags", timeout=2)
    print(f"✅ Ollama available at {ollama_url} with model {ollama_model}")
except Exception as e:
    print(f"Warning: Ollama not available: {e}")
    print("💡 Install Ollama and run: ollama pull llama3.1")

DIARY_PATH = Path(os.getenv("DIARY_PATH", str(Path.home() / "Documents" / "diary")))


async def call_ollama(prompt: str, system_prompt: str = "") -> str:
    """Call Ollama API for text generation."""
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ollama_url}/api/generate",
            json={
                "model": ollama_model,
                "prompt": f"{system_prompt}\n\n{prompt}",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 200,
                }
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")


def get_all_entries() -> List[Tuple[datetime, Path]]:
    entries = []
    for file in DIARY_PATH.glob("*.md"):
        if file.name.startswith("."):
            continue
        try:
            date_str = file.stem
            date = datetime.strptime(date_str, "%Y-%m-%d")
            entries.append((date, file))
        except ValueError:
            continue

    return sorted(entries, key=lambda x: x[0], reverse=True)


def read_entry(file_path: Path) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, PermissionError, OSError) as e:
        return f"Error reading file: {e}"


async def extract_themes_and_topics(content: str) -> List[str]:
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
        response_text = await call_ollama(prompt, "You are an expert at identifying key themes in personal writing. Extract the most meaningful concepts.")
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


# Global theme cache to avoid redundant AI analysis
_theme_cache = {}

async def get_themes_cached(content: str, file_stem: str) -> List[str]:
    """Get themes for content with caching to avoid redundant AI calls."""
    # Simple cache key based on content length and first 100 chars
    cache_key = f"{file_stem}_{len(content)}_{hash(content[:100])}"
    
    if cache_key in _theme_cache:
        return _theme_cache[cache_key]
    
    themes = await extract_themes_and_topics(content)
    _theme_cache[cache_key] = themes
    return themes

def generate_topic_tags(themes: List[str]) -> List[str]:
    """Convert themes to Obsidian-compatible topic tags."""
    if not themes:
        return []
    
    topic_tags = []
    for theme in themes:
        # Skip preamble text and extract actual themes
        if 'key themes' in theme.lower() or 'extracted from' in theme.lower():
            # Split on common delimiters to find actual themes
            parts = re.split(r'[:\n•\-]', theme)
            for part in parts:
                clean_part = part.strip()
                if clean_part and len(clean_part) < 50 and not any(skip in clean_part.lower() for skip in ['key themes', 'extracted', 'journal entry']):
                    clean_theme = re.sub(r'[^\w\s-]', '', clean_part.lower())
                    clean_theme = re.sub(r'\s+', '-', clean_theme.strip())
                    if clean_theme:
                        topic_tags.append(f'#{clean_theme}')
        else:
            # Clean and format theme as hashtag
            clean_theme = re.sub(r'[^\w\s-]', '', theme.lower())
            clean_theme = re.sub(r'\s+', '-', clean_theme.strip())
            # Handle slashes by converting to dashes
            clean_theme = clean_theme.replace('/', '-')
            if clean_theme:
                topic_tags.append(f'#{clean_theme}')
    
    return topic_tags


async def find_related_entries(
    current_content: str,
    exclude_date: Optional[str] = None,
    max_related: int = 6,
) -> List[str]:
    """Find related entries using cached theme analysis - much faster!"""
    # Get themes for current content
    current_themes = set(await get_themes_cached(current_content, exclude_date or "current"))

    if not current_themes:
        return []

    entries = get_all_entries()
    similarity_scores = []

    print(f"🔍 Analyzing {len(entries)} entries with cached themes...")
    
    for date, file_path in entries:
        if exclude_date and file_path.stem == exclude_date:
            continue

        entry_content = read_entry(file_path)
        if entry_content.startswith("Error reading file"):
            continue
            
        # Use cached theme extraction
        entry_themes = set(await get_themes_cached(entry_content, file_path.stem))

        if entry_themes:
            # Calculate Jaccard similarity for thematic overlap
            similarity = len(current_themes & entry_themes) / len(
                current_themes | entry_themes
            )
            
            # Lower threshold for more connections
            if similarity > 0.08:
                similarity_scores.append((similarity, file_path.stem))

    # Sort by similarity and take top matches
    similarity_scores.sort(reverse=True, key=lambda x: x[0])
    
    # Return Obsidian-compatible backlinks
    backlinks = [f"[[{stem}]]" for _, stem in similarity_scores[:max_related]]
    
    if backlinks:
        print(f"✅ Found {len(backlinks)} cognitive connections")
    
    return backlinks


async def generate_reflection_prompts(recent_content: str, focus: Optional[str] = None) -> List[str]:
    if len(recent_content.strip()) < 20:
        return []

    focus_instruction = ""
    if focus:
        focus_instruction = f"\n\nSPECIAL FOCUS: Generate questions specifically related to {focus}. Tailor the questions to help explore this area deeply."

    prompt = f"""Based on this recent journal content, generate 3 intellectually rigorous questions for deep cognitive exploration. These should be the kind of questions a philosopher, or systems thinker would ask.{focus_instruction}

    Recent content:
    {recent_content[:800]}
    
    Create questions that:
    - Probe underlying assumptions, mental models, and cognitive patterns
    - Explore systems, interconnections, and deeper mechanisms
    - Challenge surface-level thinking with analytical depth
    - Connect personal experience to broader philosophical concepts
    - Encourage meta-cognitive awareness and intellectual rigor
    
    Format as numbered questions without additional text:
    1. [sophisticated analytical question]
    2. [sophisticated analytical question] 
    3. [sophisticated analytical question]"""

    try:
        print("🤖 Attempting LLM generation with Ollama...")
        response_text = await call_ollama(prompt, "You are an expert philosopher and cognitive scientist. Generate intellectually rigorous questions that probe deep patterns, assumptions, and cognitive mechanisms.")
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

    return prompts[:3]


async def _generate_template_content(
    entry_date: datetime, filename: str, focus: Optional[str] = None
) -> str:
    recent_count = int(os.getenv("RECENT_ENTRIES_COUNT", "3"))
    recent_entries = get_all_entries()[:recent_count]
    recent_contents = [read_entry(path) for _, path in recent_entries]

    recent_text = "\n\n".join(recent_contents) if recent_contents else ""
    prompts = await generate_reflection_prompts(recent_text, focus)
    
    # Fallback sophisticated prompts if AI generation fails
    if not prompts:
        prompts = [
            "What cognitive patterns or mental models shaped your thinking this period?",
            "How do your current challenges reflect deeper philosophical questions about identity and meaning?",
            "What assumptions about reality, success, or relationships are being tested right now?"
        ]

    template_parts = []

    # Use filename as title for Obsidian compatibility
    template_parts.append(f"# {filename}")
    template_parts.append("")

    template_parts.append("## 🧠 Cognitive Analysis Prompts")
    for i, prompt in enumerate(prompts, 1):
        template_parts.append(f"\n**{prompt}**\n")
        template_parts.append("*Explore underlying mechanisms, patterns, and implications...*\n")

    template_parts.append("\n## 💭 Deep Reflection")
    template_parts.append("\nAnalyze, synthesize, explore connections and deeper meanings...\n\n\n")

    template_parts.append("## 🔍 Meta-Cognitive Notes")
    template_parts.append("\n*How did this analysis change your understanding? What new questions emerged?*\n\n")
    
    template_parts.append("---")
    template_parts.append("")
    template_parts.append("## 🔗 Memory Links")
    template_parts.append("")
    template_parts.append("*Temporal connections and topic tags will be auto-generated when you complete the entry.*")

    return "\n".join(template_parts)


@mcp.tool()
async def create_diary_template(date: Optional[str] = None, focus: Optional[str] = None) -> str:
    """Create a sophisticated diary template with intellectually rigorous prompts for deep cognitive exploration.

    Args:
        date: Date for the entry in YYYY-MM-DD format. If not provided, uses today's date.
        focus: Optional focus area for analysis (e.g., "current struggles", "cognitive patterns", "decision frameworks")

    Returns:
        A formatted template with sophisticated analytical prompts
    """
    if date:
        try:
            entry_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Error: Date must be in YYYY-MM-DD format"
    else:
        entry_date = datetime.now()

    filename = entry_date.strftime("%Y-%m-%d")
    file_path = DIARY_PATH / f"{filename}.md"

    if file_path.exists():
        return f"Entry for {filename} already exists. Use read_diary_entry to view it."

    return await _generate_template_content(entry_date, filename, focus)


@mcp.tool()
async def create_diary_entry_file(date: Optional[str] = None, focus: Optional[str] = None) -> str:
    """Create a sophisticated diary entry file with AI-generated analytical prompts for deep intellectual exploration.

    Args:
        date: Date for the entry in YYYY-MM-DD format. If not provided, uses today's date.
        focus: Optional focus area for analysis (e.g., "current struggles", "cognitive patterns", "philosophical questions")

    Returns:
        Success message with file path
    """
    if date:
        try:
            entry_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Error: Date must be in YYYY-MM-DD format"
    else:
        entry_date = datetime.now()

    filename = entry_date.strftime("%Y-%m-%d")
    file_path = DIARY_PATH / f"{filename}.md"

    if file_path.exists():
        return f"Entry for {filename} already exists at {file_path}"

    template_content = await _generate_template_content(entry_date, filename, focus)

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(template_content, encoding="utf-8")

        return f"🧠 Created intellectual diary entry: {file_path}\n\nExplore the prompts, then use 'complete_diary_entry' when done to auto-generate memory links!"
    except (PermissionError, OSError) as e:
        return f"Error creating file: {e}"


@mcp.tool()
async def complete_diary_entry(date: Optional[str] = None) -> str:
    """Complete your diary entry - automatically generates Obsidian-compatible memory links and provides cognitive analysis.
    Use this when you're done writing. Creates [[YYYY-MM-DD]] backlinks that integrate with Obsidian's backlink system.

    Args:
        date: Date for the entry in YYYY-MM-DD format. If not provided, uses today's date.

    Returns:
        Success message with auto-generated memory links and cognitive network analysis
    """
    if date:
        try:
            entry_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Error: Date must be in YYYY-MM-DD format"
    else:
        entry_date = datetime.now()

    filename = entry_date.strftime("%Y-%m-%d")
    file_path = DIARY_PATH / f"{filename}.md"

    if not file_path.exists():
        return f"No entry found for {filename}. Create an entry first."

    content = read_entry(file_path)
    related = await find_related_entries(content, exclude_date=filename)

    # Remove existing backlinks sections (handle both formats)
    content = re.sub(r"---\n\*\*Related entries:\*\*.*$", "", content, flags=re.DOTALL)
    content = re.sub(r"---\n\*\*Memory links:\*\*.*$", "", content, flags=re.DOTALL)
    content = content.rstrip()

    # Generate topic tags from themes
    themes = await extract_themes_and_topics(content)
    topic_tags = generate_topic_tags(themes)
    
    # Add sophisticated memory links section for Obsidian
    memory_section = "\n\n---\n\n## 🔗 Memory Links\n\n"
    
    if related:
        memory_section += f"**Temporal connections:** {' • '.join(related)}\n\n"
    
    if topic_tags:
        memory_section += f"**Topic tags:** {' '.join(topic_tags)}\n\n"
    
    if related or topic_tags:
        memory_section += "*Explore these connections in Obsidian's Backlinks panel and Graph view.*"
    else:
        memory_section += "*No connections found - this represents novel cognitive territory.*"
    
    content += memory_section

    try:
        file_path.write_text(content, encoding="utf-8")
        
        # Generate sophisticated cognitive analysis for summary
        themes = await extract_themes_and_topics(content)
        themes_str = ", ".join(themes[:5]) if themes else "philosophical inquiry"
        
        # Count total entries for context
        total_entries = len(get_all_entries())
        connection_percentage = (len(related) / max(total_entries - 1, 1)) * 100 if related else 0
        
        # Calculate comprehensive connection stats
        total_connections = len(related) + len(topic_tags)
        connection_parts = []
        if related:
            connection_parts.append(f"{len(related)} temporal")
        if topic_tags:
            connection_parts.append(f"{len(topic_tags)} topics")
        
        connections_desc = " + ".join(connection_parts) if connection_parts else "novel territory"
        
        return f"🧠 **Cognitive trace completed** for {filename}\n\n🔍 **Analytical themes:** {themes_str}\n🔗 **Memory network:** {connections_desc} ({connection_percentage:.1f}% temporal coverage)\n\n📚 **Integration status:** Your exploration is now woven into Obsidian's knowledge graph!\n\n💡 **Discover more:** Backlinks panel (temporal), Tags panel (topics), Graph view (visual network)"
    except (PermissionError, OSError) as e:
        return f"Error completing entry: {e}"


@mcp.tool()
async def update_entry_backlinks(date: str) -> str:
    """Update the backlinks for an existing diary entry based on its current content.

    Args:
        date: Date of the entry in YYYY-MM-DD format

    Returns:
        Success message with updated backlinks
    """
    try:
        entry_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Error: Date must be in YYYY-MM-DD format"

    filename = entry_date.strftime("%Y-%m-%d")
    file_path = DIARY_PATH / f"{filename}.md"

    if not file_path.exists():
        return f"No entry found for {filename}"

    content = read_entry(file_path)
    related = await find_related_entries(content, exclude_date=filename)

    # Remove existing backlinks sections
    content = re.sub(r"---\n\*\*Related entries:\*\*.*$", "", content, flags=re.DOTALL)
    content = re.sub(r"---\n\*\*Memory links:\*\*.*$", "", content, flags=re.DOTALL)
    content = content.rstrip()

    # Generate topic tags from current content
    themes = await extract_themes_and_topics(content)
    topic_tags = generate_topic_tags(themes)
    
    # Add updated memory links with both dates and topics
    memory_section = "\n\n---\n\n## 🔗 Memory Links\n\n"
    
    if related:
        memory_section += f"**Temporal connections:** {' • '.join(related)}\n\n"
    
    if topic_tags:
        memory_section += f"**Topic tags:** {' '.join(topic_tags)}\n\n"
    
    if related or topic_tags:
        memory_section += "*These entries share thematic resonance with your exploration.*"
    else:
        memory_section += "*No thematic connections found.*"
    
    content += memory_section

    try:
        file_path.write_text(content, encoding="utf-8")

        connection_count = len(related) + len(topic_tags)
        connection_types = []
        if related:
            connection_types.append(f"{len(related)} temporal")
        if topic_tags:
            connection_types.append(f"{len(topic_tags)} topic tags")
        
        connections_str = " + ".join(connection_types) if connection_types else "none found"
        
        return (
            f"✅ **Memory links updated** for {filename}\n\n🔗 **Connections:** {connections_str}\n\n💡 **Obsidian power:** Use Backlinks panel for temporal connections, Tags panel for topics, Graph view for visual exploration!"
        )
    except (PermissionError, OSError) as e:
        return f"Error updating entry: {e}"


@mcp.tool()
async def refresh_recent_backlinks(days: int = 30) -> str:
    """Update backlinks for recent diary entries only - much faster than full refresh.

    Args:
        days: Number of recent days to update (default: 30)

    Returns:
        Success message with count of updated entries
    """
    from datetime import timedelta
    
    entries = get_all_entries()
    if not entries:
        return "No diary entries found to update"

    # Filter to recent entries only
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_entries = [(date, path) for date, path in entries if date >= cutoff_date]
    
    if not recent_entries:
        return f"No entries found in the last {days} days"
    
    print(f"🔄 Refreshing backlinks for {len(recent_entries)} entries from last {days} days...")
    
    updated_count = 0
    errors = []
    
    for date, file_path in recent_entries:
        try:
            content = read_entry(file_path)
            
            if content.startswith("Error reading file"):
                errors.append(f"{file_path.stem}: {content}")
                continue
                
            related = await find_related_entries(content, exclude_date=file_path.stem)
            
            # Remove existing backlinks sections
            content = re.sub(r"---\n\*\*Related entries:\*\*.*$", "", content, flags=re.DOTALL)
            content = re.sub(r"---\n\*\*Memory links:\*\*.*$", "", content, flags=re.DOTALL)
            content = content.rstrip()
            
            # Generate topic tags and add comprehensive memory links
            themes = await extract_themes_and_topics(content)
            topic_tags = generate_topic_tags(themes)
            
            memory_section = "\n\n---\n\n## 🔗 Memory Links\n\n"
            
            if related:
                memory_section += f"**Temporal connections:** {' • '.join(related)}\n\n"
            
            if topic_tags:
                memory_section += f"**Topic tags:** {' '.join(topic_tags)}\n\n"
            
            if related or topic_tags:
                memory_section += "*Thematic resonance with your broader explorations.*"
            
            content += memory_section
            
            file_path.write_text(content, encoding="utf-8")
            updated_count += 1
            print(f"✅ Updated {file_path.stem} ({len(related)} connections)")
            
        except Exception as e:
            errors.append(f"{file_path.stem}: {str(e)}")
            print(f"❌ Error: {file_path.stem}: {e}")
    
    result = f"🧠 **Recent backlinks refreshed!**\n\n✅ **Updated:** {updated_count} entries from last {days} days"
    
    if errors:
        result += f"\n\n⚠️ **Errors:** {len(errors)} entries had issues"
    
    result += "\n\n💡 **Tip:** This is much faster than refreshing all entries!"
    return result


# Basic required tools for reading entries
@mcp.tool()
def read_diary_entry(date: str) -> str:
    """Read a specific diary entry by date.

    Args:
        date: Date of the entry in YYYY-MM-DD format

    Returns:
        The diary entry content
    """
    try:
        entry_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Error: Date must be in YYYY-MM-DD format"

    filename = entry_date.strftime("%Y-%m-%d")
    file_path = DIARY_PATH / f"{filename}.md"

    if not file_path.exists():
        return f"No entry found for {filename}"

    return read_entry(file_path)


@mcp.tool()
def list_recent_entries(count: int = 10) -> str:
    """List your most recent diary entries.

    Args:
        count: Number of recent entries to list (default: 10)

    Returns:
        A list of recent entry dates
    """
    entries = get_all_entries()[:count]

    if not entries:
        return "No diary entries found"

    result = [f"📅 Your {len(entries)} most recent entries:\n"]
    for date, path in entries:
        result.append(
            f"- {date.strftime('%Y-%m-%d')} ({date.strftime('%A, %B %d, %Y')})"
        )

    return "\n".join(result)


if __name__ == "__main__":
    mcp.run()