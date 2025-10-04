"""Obsidian Diary MCP Server

A Model Context Protocol server for managing Obsidian diary entries with smart templates and auto-tagging.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
import re
from collections import Counter

from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("obsidian-diary")

# Configuration
DIARY_PATH = Path("/Users/gps/Documents/diary")


def get_all_entries() -> List[Tuple[datetime, Path]]:
    """Get all diary entries sorted by date."""
    entries = []
    for file in DIARY_PATH.glob("*.md"):
        if file.name.startswith("."):
            continue
        try:
            # Parse date from filename (format: YYYY-MM-DD.md)
            date_str = file.stem
            date = datetime.strptime(date_str, "%Y-%m-%d")
            entries.append((date, file))
        except ValueError:
            # Skip files that don't match the date format
            continue
    
    return sorted(entries, key=lambda x: x[0], reverse=True)


def read_entry(file_path: Path) -> str:
    """Read the content of a diary entry."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


def extract_themes_and_topics(content: str) -> List[str]:
    """Extract key themes and topics from diary content using keyword analysis."""
    # Remove the Related entries section to avoid counting those
    content_without_links = re.sub(r'\*\*Related entries:\*\*.*$', '', content, flags=re.DOTALL)
    
    # Common words to ignore
    stop_words = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'you', 'your', 'he', 'him', 'his', 'she',
        'it', 'its', 'they', 'them', 'their', 'what', 'which', 'who', 'this', 'that', 'these', 'those',
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'should', 'could', 'ought', 'im', 'ive', 'cant', 'dont', 'doesnt',
        'didnt', 'wont', 'wouldnt', 'shouldnt', 'couldnt', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
        'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
        'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
        'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
        'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
        'can', 'just', 'now', 'also', 'like', 'really', 'think', 'know', 'get', 'got', 'feel', 'felt',
        'going', 'go', 'went', 'still', 'well', 'need', 'want', 'even', 'much', 'make', 'made', 'day',
        'time', 'lot', 'bit', 'back', 'good', 'great', 'nice', 'ok', 'okay', 'yeah', 'yes', 'no'
    }
    
    # Extract words (2+ characters)
    words = re.findall(r'\b[a-z]{2,}\b', content_without_links.lower())
    
    # Count words excluding stop words
    word_freq = Counter([w for w in words if w not in stop_words])
    
    # Get top keywords
    top_words = [word for word, count in word_freq.most_common(15) if count > 1]
    
    return top_words


def find_related_entries(current_content: str, exclude_date: Optional[str] = None, max_related: int = 6) -> List[str]:
    """Find related entries based on content similarity.
    
    Args:
        current_content: Content to analyze for finding related entries
        exclude_date: Date string (YYYY-MM-DD) to exclude from results (typically the current entry)
        max_related: Maximum number of related entries to return
    """
    current_themes = set(extract_themes_and_topics(current_content))
    
    if not current_themes:
        return []
    
    entries = get_all_entries()
    similarity_scores = []
    
    for date, file_path in entries:
        # Skip the excluded date (current entry)
        if exclude_date and file_path.stem == exclude_date:
            continue
            
        entry_content = read_entry(file_path)
        entry_themes = set(extract_themes_and_topics(entry_content))
        
        # Calculate similarity (Jaccard similarity)
        if entry_themes:
            similarity = len(current_themes & entry_themes) / len(current_themes | entry_themes)
            if similarity > 0.1:  # Minimum threshold
                similarity_scores.append((similarity, file_path.stem))
    
    # Sort by similarity and return top matches
    similarity_scores.sort(reverse=True, key=lambda x: x[0])
    return [f"[[{stem}]]" for _, stem in similarity_scores[:max_related]]


def generate_reflection_prompts(recent_entries: List[str], current_date: Optional[str] = None) -> List[str]:
    """Generate dynamic reflection prompts based on recent entries' content and patterns."""
    if not recent_entries:
        return ["What's on your mind today?"]
    
    prompts = []
    
    # Analyze patterns across recent entries
    all_content = " ".join(recent_entries)
    themes = extract_themes_and_topics(all_content)
    
    # Generate prompts dynamically based on what appears frequently
    if themes:
        # Take the most frequent themes and create open-ended questions
        top_themes = themes[:3]  # Top 3 themes
        
        for theme in top_themes:
            # Create varied question formats to avoid repetition
            question_formats = [
                f"How did {theme} play out today?",
                f"What's different about {theme} compared to recent days?",
                f"What would you like to explore about {theme}?",
                f"How are you feeling about {theme} right now?"
            ]
            # Use hash of theme and date to get consistent but varied questions
            import hashlib
            seed = hashlib.md5(f"{theme}{current_date or ''}".encode()).hexdigest()
            prompt_index = int(seed[:2], 16) % len(question_formats)
            prompts.append(question_formats[prompt_index])
    
    # Add some varied general prompts based on day pattern
    general_prompts = [
        "What surprised you today?",
        "What would you tell a friend about today?",
        "What's something you noticed today that you usually don't?",
        "If today had a color, what would it be and why?",
        "What's one thing you'd do differently if you could replay today?",
        "What are you curious about right now?",
        "What made you smile or laugh recently?",
        "What's something you're avoiding thinking about?",
        "How did your body feel today?",
        "What story would today tell if it could speak?"
    ]
    
    # Select general prompts based on date to ensure variety
    if current_date:
        import hashlib
        seed = int(hashlib.md5(current_date.encode()).hexdigest()[:8], 16)
        selected_general = [general_prompts[i % len(general_prompts)] for i in range(seed, seed + 2)]
        prompts.extend(selected_general)
    else:
        prompts.extend(general_prompts[:2])
    
    # Ensure we have 3-5 unique prompts
    unique_prompts = list(dict.fromkeys(prompts))  # Remove duplicates while preserving order
    return unique_prompts[:5] if len(unique_prompts) >= 5 else unique_prompts[:3]


@mcp.tool()
def create_diary_template(date: Optional[str] = None) -> str:
    """Create a new diary entry template with reflection prompts based on recent entries.
    
    Args:
        date: Date for the entry in YYYY-MM-DD format. If not provided, uses today's date.
    
    Returns:
        A formatted diary template with reflection prompts
    """
    # Use provided date or today's date
    if date:
        try:
            entry_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Error: Date must be in YYYY-MM-DD format"
    else:
        entry_date = datetime.now()
    
    filename = entry_date.strftime("%Y-%m-%d")
    file_path = DIARY_PATH / f"{filename}.md"
    
    # Check if entry already exists
    if file_path.exists():
        return f"Entry for {filename} already exists. Use read_diary_entry to view it."
    
    # Get the 3 most recent entries
    recent_entries = get_all_entries()[:3]
    recent_contents = [read_entry(path) for _, path in recent_entries]
    
    # Generate reflection prompts
    prompts = generate_reflection_prompts(recent_contents, filename)
    
    # Create template
    template_parts = []
    
    # Title with current day
    day_name = entry_date.strftime("%A, %B %d, %Y")
    template_parts.append(f"# {day_name}")
    template_parts.append("")
    
    # Reflection prompts
    template_parts.append("## 🤔 Reflection Prompts")
    for i, prompt in enumerate(prompts, 1):
        template_parts.append(f"\n**{prompt}**\n")
    
    # Brain dump section
    template_parts.append("\n## 💭 Brain Dump")
    template_parts.append("\nJust write whatever's on your mind...\n\n\n")
    
    # Placeholder for auto-generated links
    template_parts.append("---")
    template_parts.append("**Related entries:** (will be auto-generated when you save)")
    
    return "\n".join(template_parts)


@mcp.tool()
def save_diary_entry(date: str, content: str) -> str:
    """Save a diary entry and automatically add relevant backlinks.
    
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
    
    # Find related entries (excluding current entry)
    related = find_related_entries(content, exclude_date=filename)
    
    # Remove existing related entries section if present
    content = re.sub(r'---\n\*\*Related entries:\*\*.*$', '', content, flags=re.DOTALL)
    content = content.rstrip()
    
    # Add related entries
    if related:
        content += f"\n---\n**Related entries:** {', '.join(related)}"
    
    # Save the entry
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        related_str = ', '.join(related) if related else 'none found'
        return f"✅ Entry saved to {file_path}\n\n🔗 Auto-generated backlinks: {related_str}"
    except Exception as e:
        return f"Error saving entry: {e}"


@mcp.tool()
def read_diary_entry(date: str) -> str:
    """Read an existing diary entry.
    
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
    """List recent diary entries.
    
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
        result.append(f"- {date.strftime('%Y-%m-%d')} ({date.strftime('%A, %B %d, %Y')})")
    
    return "\n".join(result)


@mcp.tool()
def update_entry_backlinks(date: str) -> str:
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
    
    # Read current content
    content = read_entry(file_path)
    
    # Find related entries (excluding current entry)
    related = find_related_entries(content, exclude_date=filename)
    
    # Remove existing related entries section
    content = re.sub(r'---\n\*\*Related entries:\*\*.*$', '', content, flags=re.DOTALL)
    content = content.rstrip()
    
    # Add updated related entries
    if related:
        content += f"\n---\n**Related entries:** {', '.join(related)}"
    
    # Save updated entry
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        related_str = ', '.join(related) if related else 'none found'
        return f"✅ Backlinks updated for {filename}\n\n🔗 Related entries: {related_str}"
    except Exception as e:
        return f"Error updating entry: {e}"


if __name__ == "__main__":
    mcp.run()
