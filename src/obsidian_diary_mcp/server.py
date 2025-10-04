import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
import re

from fastmcp import FastMCP, Context

# Initialize FastMCP server
mcp = FastMCP("obsidian-diary")

DIARY_PATH = Path(os.getenv("DIARY_PATH", str(Path.home() / "Documents" / "diary")))


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


async def extract_themes_and_topics(content: str, ctx: Optional[Context]) -> List[str]:
    content_without_links = re.sub(
        r"\*\*Related entries:\*\*.*$", "", content, flags=re.DOTALL
    )

    if len(content_without_links.strip()) < 20 or ctx is None:
        return []

    prompt = f"""Analyze this journal entry and identify 3-5 key themes, topics, or concepts. 
    
    Entry content:
    {content_without_links[:1000]}
    
    Return only the themes as a comma-separated list of single words or short phrases (2-3 words max). Focus on:
    - Main topics discussed
    - Emotions or feelings
    - Activities or experiences
    - People or relationships
    - Goals or challenges
    
    Example: work, anxiety, running, family, creativity"""

    response = await ctx.sample(
        messages=prompt,
        system_prompt="You are an expert at identifying key themes in personal writing. Extract the most meaningful concepts.",
        temperature=0.3,
        max_tokens=100,
    )

    # Extract text content from LLM response
    try:
        response_text = getattr(response, "text", str(response))
    except AttributeError:
        response_text = str(response)
    themes = [
        theme.strip().lower()
        for theme in response_text.strip().split(",")
        if theme.strip()
    ]
    return themes[:5]


async def find_related_entries(
    current_content: str,
    exclude_date: Optional[str] = None,
    max_related: int = 6,
    ctx: Optional[Context] = None,
) -> List[str]:
    current_themes = set(await extract_themes_and_topics(current_content, ctx))

    if not current_themes:
        return []

    entries = get_all_entries()
    similarity_scores = []

    for date, file_path in entries:
        if exclude_date and file_path.stem == exclude_date:
            continue

        entry_content = read_entry(file_path)
        entry_themes = set(await extract_themes_and_topics(entry_content, ctx))

        if entry_themes:
            similarity = len(current_themes & entry_themes) / len(
                current_themes | entry_themes
            )
            if similarity > 0.1:
                similarity_scores.append((similarity, file_path.stem))

    similarity_scores.sort(reverse=True, key=lambda x: x[0])
    return [f"[[{stem}]]" for _, stem in similarity_scores[:max_related]]


async def generate_reflection_prompts(
    recent_content: str, ctx: Optional[Context]
) -> List[str]:
    if len(recent_content.strip()) < 20 or ctx is None:
        return []

    prompt = f"""Based on this recent journal content, generate 3 thoughtful reflection questions that would help with deeper self-awareness and personal growth. 

    Recent content:
    {recent_content[:800]}
    
    Create questions that:
    - Are open-ended and thought-provoking
    - Connect to themes in the content
    - Encourage deeper reflection
    - Are personal and introspective
    
    Format as a simple numbered list:
    1. [question]
    2. [question]
    3. [question]"""

    response = await ctx.sample(
        messages=prompt,
        system_prompt="You are an expert at creating thoughtful, personalized reflection questions for journaling.",
        temperature=0.7,
        max_tokens=200,
    )

    # Extract text content from LLM response
    try:
        response_text = getattr(response, "text", str(response))
    except AttributeError:
        response_text = str(response)

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
    entry_date: datetime, filename: str, ctx: Optional[Context]
) -> str:
    recent_count = int(os.getenv("RECENT_ENTRIES_COUNT", "3"))
    recent_entries = get_all_entries()[:recent_count]
    recent_contents = [read_entry(path) for _, path in recent_entries]

    recent_text = "\n\n".join(recent_contents) if recent_contents else ""
    prompts = await generate_reflection_prompts(recent_text, ctx)

    template_parts = []

    day_name = entry_date.strftime("%A, %B %d, %Y")
    template_parts.append(f"# {day_name}")
    template_parts.append("")

    template_parts.append("## 🤔 Reflection Prompts")
    for i, prompt in enumerate(prompts, 1):
        template_parts.append(f"\n**{prompt}**\n")

    template_parts.append("\n## 💭 Brain Dump")
    template_parts.append("\nJust write whatever's on your mind...\n\n\n")

    template_parts.append("---")
    template_parts.append("**Related entries:** (will be auto-generated when you save)")

    return "\n".join(template_parts)


@mcp.tool()
async def create_diary_template(date: Optional[str] = None, ctx=None) -> str:
    """Create a new diary entry template with reflection prompts based on recent entries.

    Args:
        date: Date for the entry in YYYY-MM-DD format. If not provided, uses today's date.

    Returns:
        A formatted diary template with reflection prompts
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

    return await _generate_template_content(entry_date, filename, ctx)


@mcp.tool()
async def create_diary_entry_file(date: Optional[str] = None, ctx=None) -> str:
    """Create a new diary entry file with AI-generated reflection prompts.

    Args:
        date: Date for the entry in YYYY-MM-DD format. If not provided, uses today's date.

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

    template_content = await _generate_template_content(entry_date, filename, ctx)

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(template_content, encoding="utf-8")

        return f"✅ Created diary entry: {file_path}\n\nOpen it in Obsidian to start writing!"
    except (PermissionError, OSError) as e:
        return f"Error creating file: {e}"


@mcp.tool()
async def save_diary_entry(date: str, content: str, ctx=None) -> str:
    """Save diary entry with automatic backlinks to related entries.

    Args:
        date: Date for the entry in YYYY-MM-DD format
        content: The diary entry content

    Returns:
        Success message with the file path and auto-generated backlinks
    """
    try:
        entry_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Error: Date must be in YYYY-MM-DD format"

    filename = entry_date.strftime("%Y-%m-%d")
    file_path = DIARY_PATH / f"{filename}.md"

    related = await find_related_entries(content, exclude_date=filename, ctx=ctx)

    content = re.sub(r"---\n\*\*Related entries:\*\*.*$", "", content, flags=re.DOTALL)
    content = content.rstrip()

    if related:
        content += f"\n---\n**Related entries:** {', '.join(related)}"

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

        related_str = ", ".join(related) if related else "none found"
        return f"✅ Entry saved to {file_path}\n\n🔗 Auto-generated backlinks: {related_str}"
    except (PermissionError, OSError) as e:
        return f"Error saving entry: {e}"


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


@mcp.tool()
async def update_entry_backlinks(date: str, ctx=None) -> str:
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
    related = await find_related_entries(content, exclude_date=filename, ctx=ctx)

    content = re.sub(r"---\n\*\*Related entries:\*\*.*$", "", content, flags=re.DOTALL)
    content = content.rstrip()

    if related:
        content += f"\n---\n**Related entries:** {', '.join(related)}"

    try:
        file_path.write_text(content, encoding="utf-8")

        related_str = ", ".join(related) if related else "none found"
        return (
            f"✅ Backlinks updated for {filename}\n\n🔗 Related entries: {related_str}"
        )
    except (PermissionError, OSError) as e:
        return f"Error updating entry: {e}"


@mcp.tool()
async def refresh_all_backlinks(ctx=None) -> str:
    """Update backlinks for all diary entries.

    Returns:
        Success message with count of updated entries
    """
    entries = get_all_entries()

    if not entries:
        return "No diary entries found to update"

    updated_count = 0
    errors = []

    for date, file_path in entries:
        try:
            content = read_entry(file_path)

            if content.startswith("Error reading file"):
                errors.append(f"{file_path.stem}: {content}")
                continue

            related = await find_related_entries(
                content, exclude_date=file_path.stem, ctx=ctx
            )

            content = re.sub(
                r"---\n\*\*Related entries:\*\*.*$", "", content, flags=re.DOTALL
            )
            content = content.rstrip()

            if related:
                content += f"\n---\n**Related entries:** {', '.join(related)}"

            file_path.write_text(content, encoding="utf-8")

            updated_count += 1

        except Exception as e:
            errors.append(f"{file_path.stem}: {str(e)}")

    result = f"✅ Refreshed backlinks for {updated_count} entries"

    if errors:
        result += "\n\n⚠️ Errors encountered:\n" + "\n".join(errors)

    return result


if __name__ == "__main__":
    mcp.run()
