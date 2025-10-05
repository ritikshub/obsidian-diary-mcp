"""Generate comprehensive Memory Trace documents from diary entries."""

from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Set
from collections import Counter
import re


async def generate_memory_trace(
    entries: List[Tuple[datetime, Path]],
    analysis_engine,
    entry_manager
) -> str:
    """Generate a comprehensive memory trace document."""
    
    # Sort entries by date (oldest first for chronological analysis)
    sorted_entries = sorted(entries, key=lambda x: x[0])
    
    # Collect all entry data
    entry_data = []
    all_themes = []
    theme_by_entry = {}
    content_by_date = {}
    
    print("📚 Reading and analyzing entries...")
    for date, path in sorted_entries:
        content = entry_manager.read_entry(path)
        if content.startswith("Error"):
            continue
        
        themes = await analysis_engine.get_themes_cached(content, path.stem)
        entry_data.append({
            'date': date,
            'path': path,
            'content': content,
            'themes': themes
        })
        
        all_themes.extend(themes)
        theme_by_entry[date] = themes
        content_by_date[date] = content
    
    if not entry_data:
        return "No valid entries found to analyze."
    
    # Calculate statistics
    date_range_start = sorted_entries[0][0].strftime("%B %Y")
    date_range_end = sorted_entries[-1][0].strftime("%B %Y")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Build the memory trace document
    trace = []
    
    # Header
    trace.append("# Memory Trace")
    trace.append(f"*Generated: {today}*")
    trace.append("")
    trace.append(f"A visualization of themes, patterns, and connections across your diary entries from {date_range_start} to {date_range_end}.")
    trace.append("")
    trace.append("---")
    trace.append("")
    
    # Timeline Overview
    timeline = await _generate_timeline_overview(entry_data, analysis_engine)
    trace.append(timeline)
    trace.append("")
    
    # Core Themes
    core_themes = await _generate_core_themes(entry_data, analysis_engine, entry_manager)
    trace.append(core_themes)
    trace.append("")
    
    # Recurring Patterns
    patterns = _generate_recurring_patterns(entry_data, all_themes)
    trace.append(patterns)
    trace.append("")
    
    # Key Relationships Map (if relationships detected)
    relationships = _generate_relationships_map(entry_data)
    if relationships:
        trace.append(relationships)
        trace.append("")
    
    # Growth Trajectory
    growth = _generate_growth_trajectory(entry_data)
    trace.append(growth)
    trace.append("")
    
    # Wisdom Extracted
    wisdom = await _generate_wisdom_extracted(entry_data, analysis_engine)
    trace.append(wisdom)
    trace.append("")
    
    # Timeline of Significant Moments
    timeline_moments = _generate_timeline_moments(entry_data)
    trace.append(timeline_moments)
    trace.append("")
    
    # Entry Emotional Overview
    emotional_overview = _generate_emotional_overview(entry_data)
    trace.append(emotional_overview)
    trace.append("")
    
    # Footer
    trace.append("---")
    trace.append("")
    trace.append("*This memory trace serves as a living document of your journey. Update it periodically to track your evolution.*")
    
    return "\n".join(trace)


async def _generate_timeline_overview(entry_data: List[Dict], analysis_engine) -> str:
    """Generate ASCII timeline with key themes."""
    timeline = ["## Timeline Overview", ""]
    
    if len(entry_data) <= 10:
        # Simple timeline for fewer entries
        timeline.append("```")
        for i, entry in enumerate(entry_data):
            date_str = entry['date'].strftime("%Y-%m-%d")
            themes_str = " & ".join(entry['themes'][:2]) if entry['themes'] else "Reflection"
            
            if i < len(entry_data) - 1:
                timeline.append(f"{date_str} ─────► ")
            else:
                timeline.append(f"{date_str}")
            timeline.append(f"   │")
            timeline.append(f"   ▼")
            timeline.append(f"{themes_str}")
            if i < len(entry_data) - 1:
                timeline.append(f"   │")
                timeline.append("")
        timeline.append("```")
    else:
        # Condensed timeline for many entries
        timeline.append("```")
        # Sample key entries (first, middle points, last)
        key_indices = [0, len(entry_data)//3, 2*len(entry_data)//3, len(entry_data)-1]
        
        for i, idx in enumerate(key_indices):
            entry = entry_data[idx]
            date_str = entry['date'].strftime("%Y-%m-%d")
            themes_str = " & ".join(entry['themes'][:2]) if entry['themes'] else "Reflection"
            
            if i < len(key_indices) - 1:
                timeline.append(f"{date_str} ─────► {key_indices[i+1] - idx} entries ─────► ")
            else:
                timeline.append(f"{date_str}")
            timeline.append(f"   │")
            timeline.append(f"   ▼")
            timeline.append(f"{themes_str.title()}")
            if i < len(key_indices) - 1:
                timeline.append(f"   │")
                timeline.append("")
        timeline.append("```")
    
    timeline.append("")
    timeline.append("---")
    
    return "\n".join(timeline)


async def _generate_core_themes(entry_data: List[Dict], analysis_engine, entry_manager) -> str:
    """Generate core themes section with evolution."""
    themes_section = ["## Core Themes", ""]
    
    # Count theme frequency
    all_themes = []
    for entry in entry_data:
        all_themes.extend(entry['themes'])
    
    theme_counts = Counter(all_themes)
    top_themes = theme_counts.most_common(8)
    
    if not top_themes:
        return "## Core Themes\n\n*No major themes identified across entries.*"
    
    print(f"🎯 Analyzing top {len(top_themes)} themes in detail...")
    
    for theme, count in top_themes:
        # Find entries with this theme
        theme_entries = [e for e in entry_data if theme in e['themes']]
        
        if not theme_entries:
            continue
        
        # Get date range for this theme
        first_date = theme_entries[0]['date'].strftime("%B %Y")
        last_date = theme_entries[-1]['date'].strftime("%B %Y")
        
        percentage = (count / len(entry_data)) * 100
        
        # Create theme header with emoji (simple heuristic)
        emoji = _get_theme_emoji(theme)
        themes_section.append(f"### {emoji} {theme.title().replace('-', ' ')}")
        themes_section.append(f"**Frequency:** {count} entries ({percentage:.0f}% of period) | **Active:** {first_date} → {last_date}")
        themes_section.append("")
        
        # Evolution summary
        if len(theme_entries) >= 3:
            early_entry = theme_entries[0]
            mid_entry = theme_entries[len(theme_entries)//2]
            late_entry = theme_entries[-1]
            
            themes_section.append(f"**Early ({early_entry['date'].strftime('%B %Y')})**: {_extract_snippet(early_entry['content'], 100)}")
            themes_section.append("")
            themes_section.append(f"**Middle ({mid_entry['date'].strftime('%B %Y')})**: {_extract_snippet(mid_entry['content'], 100)}")
            themes_section.append("")
            themes_section.append(f"**Recent ({late_entry['date'].strftime('%B %Y')})**: {_extract_snippet(late_entry['content'], 100)}")
            themes_section.append("")
        else:
            # Just show latest
            latest = theme_entries[-1]
            themes_section.append(f"**Context:** {_extract_snippet(latest['content'], 150)}")
            themes_section.append("")
        
        themes_section.append("")
    
    themes_section.append("---")
    
    return "\n".join(themes_section)


def _generate_recurring_patterns(entry_data: List[Dict], all_themes: List[str]) -> str:
    """Identify recurring patterns and cycles."""
    patterns_section = ["## Recurring Patterns", ""]
    
    # Theme co-occurrence analysis
    theme_pairs = Counter()
    for entry in entry_data:
        themes = entry['themes']
        for i, theme1 in enumerate(themes):
            for theme2 in themes[i+1:]:
                pair = tuple(sorted([theme1, theme2]))
                theme_pairs[pair] += 1
    
    # Find most common patterns
    common_pairs = theme_pairs.most_common(5)
    
    if common_pairs:
        patterns_section.append("### 🔄 Theme Connections")
        patterns_section.append("")
        for (theme1, theme2), count in common_pairs:
            patterns_section.append(f"- **{theme1.replace('-', ' ').title()}** ↔ **{theme2.replace('-', ' ').title()}** (co-occurred {count}× times)")
        patterns_section.append("")
    
    # Weekly patterns (if we have day-of-week data)
    day_themes = {}
    for entry in entry_data:
        day = entry['date'].strftime("%A")
        if day not in day_themes:
            day_themes[day] = []
        day_themes[day].extend(entry['themes'])
    
    if len(day_themes) >= 3:
        patterns_section.append("### 📅 Temporal Patterns")
        patterns_section.append("")
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            if day in day_themes and day_themes[day]:
                top_day_themes = Counter(day_themes[day]).most_common(2)
                themes_str = ", ".join([t[0].replace('-', ' ') for t in top_day_themes])
                patterns_section.append(f"- **{day}s**: {themes_str}")
        patterns_section.append("")
    
    patterns_section.append("---")
    
    return "\n".join(patterns_section)


def _generate_relationships_map(entry_data: List[Dict]) -> str:
    """Generate relationship map if people are mentioned."""
    # Simple name detection (capitalized words that appear multiple times)
    potential_names = Counter()
    
    for entry in entry_data:
        content = entry['content']
        # Find capitalized words (potential names)
        words = re.findall(r'\b[A-Z][a-z]+\b', content)
        # Filter out common non-names
        filtered = [w for w in words if w not in {'The', 'I', 'My', 'A', 'An', 'This', 'That', 'These', 'Those', 'When', 'Where', 'Why', 'How', 'What', 'Memory', 'Links', 'Brain', 'Dump', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'}]
        potential_names.update(filtered)
    
    # Only include names that appear 3+ times
    significant_names = [(name, count) for name, count in potential_names.most_common(10) if count >= 3]
    
    if not significant_names or len(significant_names) < 2:
        return ""
    
    relationships = ["## Key Relationships Map", ""]
    relationships.append("```")
    relationships.append("        YOUR NETWORK")
    relationships.append("              │")
    relationships.append("    ┌─────────┴─────────┐")
    
    # Split into categories (simple heuristic based on frequency)
    high_freq = [n for n, c in significant_names if c >= len(entry_data) * 0.3]
    med_freq = [n for n, c in significant_names if len(entry_data) * 0.1 <= c < len(entry_data) * 0.3]
    
    if high_freq:
        relationships.append(f"    │                 │")
        relationships.append(f" Close Circle    Extended Network")
        for name in high_freq[:3]:
            count = potential_names[name]
            relationships.append(f"   {name} ({count}×)")
    
    if med_freq:
        relationships.append(f"                     │")
        for name in med_freq[:4]:
            count = potential_names[name]
            relationships.append(f"                  {name} ({count}×)")
    
    relationships.append("```")
    relationships.append("")
    relationships.append("---")
    
    return "\n".join(relationships)


def _generate_growth_trajectory(entry_data: List[Dict]) -> str:
    """Generate growth trajectory visualization."""
    growth = ["## Growth Trajectory", ""]
    
    # Simple sentiment/growth heuristic based on positive/negative words
    positive_words = {'great', 'good', 'excellent', 'amazing', 'wonderful', 'love', 'happy', 'excited', 'grateful', 'proud', 'success', 'achieved', 'progress', 'better', 'improved', 'growth', 'win'}
    negative_words = {'bad', 'terrible', 'awful', 'sad', 'angry', 'frustrated', 'worried', 'anxious', 'stressed', 'failed', 'struggling', 'difficult', 'hard', 'tired', 'exhausted'}
    
    # Analyze sentiment over time
    sentiment_scores = []
    for entry in entry_data:
        content_lower = entry['content'].lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        # Calculate net sentiment
        if positive_count + negative_count > 0:
            score = (positive_count - negative_count) / (positive_count + negative_count)
        else:
            score = 0
        
        sentiment_scores.append(score)
    
    # Create ASCII visualization
    growth.append("```")
    
    # Divide into segments
    segment_size = max(1, len(sentiment_scores) // 5)
    segments = []
    for i in range(0, len(sentiment_scores), segment_size):
        segment = sentiment_scores[i:i+segment_size]
        avg = sum(segment) / len(segment) if segment else 0
        segments.append(avg)
    
    # Draw trajectory
    for i, score in enumerate(segments):
        date = entry_data[i * segment_size]['date'].strftime("%Y-%m")
        
        if score > 0.2:
            arrow = "↗ ↗ ↗"
        elif score > 0:
            arrow = "↗"
        elif score < -0.2:
            arrow = "↘ ↘"
        elif score < 0:
            arrow = "↘"
        else:
            arrow = "→"
        
        if i < len(segments) - 1:
            growth.append(f"{date} ─────► ")
        else:
            growth.append(f"{date}")
        growth.append(f"  {arrow}")
    
    growth.append("")
    growth.append("Legend: ↗ = positive trajectory, → = stable, ↘ = challenges")
    growth.append("```")
    growth.append("")
    growth.append("---")
    
    return "\n".join(growth)


async def _generate_wisdom_extracted(entry_data: List[Dict], analysis_engine) -> str:
    """Extract key insights and wisdom."""
    wisdom = ["## Wisdom Extracted", ""]
    wisdom.append("Key insights discovered throughout your entries:")
    wisdom.append("")
    
    # Look for explicit reflective statements
    insight_patterns = [
        r'"([^"]{20,150})"',  # Quoted text
        r'learned that ([^.!?]{20,150})[.!?]',
        r'realized ([^.!?]{20,150})[.!?]',
        r'understood ([^.!?]{20,150})[.!?]',
        r'important to ([^.!?]{20,150})[.!?]',
    ]
    
    insights = []
    for entry in entry_data:
        content = entry['content']
        for pattern in insight_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                insight = match.group(1).strip()
                if len(insight) >= 20 and insight not in insights:
                    insights.append(insight)
                    if len(insights) >= 8:
                        break
            if len(insights) >= 8:
                break
        if len(insights) >= 8:
            break
    
    if insights:
        for insight in insights[:8]:
            wisdom.append(f"> {insight}")
            wisdom.append("")
    else:
        wisdom.append("*Wisdom accumulates with each entry. Continue your practice to surface deeper insights.*")
        wisdom.append("")
    
    wisdom.append("---")
    
    return "\n".join(wisdom)


def _generate_timeline_moments(entry_data: List[Dict]) -> str:
    """Generate timeline of significant moments."""
    timeline = ["## Timeline of Significant Moments", ""]
    
    # Select key entries (start, end, and some in between)
    if len(entry_data) <= 5:
        key_entries = entry_data
    else:
        indices = [0, len(entry_data)//4, len(entry_data)//2, 3*len(entry_data)//4, len(entry_data)-1]
        key_entries = [entry_data[i] for i in indices]
    
    for entry in key_entries:
        date_str = entry['date'].strftime("%B %d, %Y")
        themes_str = ", ".join(entry['themes'][:3]) if entry['themes'] else "reflection"
        snippet = _extract_snippet(entry['content'], 80)
        
        timeline.append(f"**{date_str}** - {themes_str.title().replace('-', ' ')}")
        timeline.append(f"  ↳ {snippet}")
        timeline.append("")
    
    timeline.append("---")
    
    return "\n".join(timeline)


def _generate_emotional_overview(entry_data: List[Dict]) -> str:
    """Generate quick reference of entry tones."""
    overview = ["## Quick Reference: Entry Overview", ""]
    
    # Just list dates with primary themes
    for entry in entry_data[-15:]:  # Last 15 entries
        date_str = entry['date'].strftime("%Y-%m-%d")
        themes_str = ", ".join(entry['themes'][:2]) if entry['themes'] else "general reflection"
        overview.append(f"- **{date_str}**: {themes_str.replace('-', ' ')}")
    
    if len(entry_data) > 15:
        overview.append("")
        overview.append(f"*...and {len(entry_data) - 15} earlier entries*")
    
    overview.append("")
    overview.append("---")
    
    return "\n".join(overview)


def _extract_snippet(content: str, max_length: int = 100) -> str:
    """Extract a meaningful snippet from content."""
    # Remove markdown headers and links
    clean = re.sub(r'#+ ', '', content)
    clean = re.sub(r'\[\[.*?\]\]', '', clean)
    clean = re.sub(r'\*\*.*?\*\*:', '', clean)
    
    # Get first substantial sentence
    sentences = re.split(r'[.!?]+', clean)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) >= 20:
            if len(sentence) > max_length:
                return sentence[:max_length] + "..."
            return sentence
    
    # Fallback: just return first max_length characters
    clean = clean.strip()
    if len(clean) > max_length:
        return clean[:max_length] + "..."
    return clean if clean else "..."


def _get_theme_emoji(theme: str) -> str:
    """Get appropriate emoji for theme (simple heuristic)."""
    theme_lower = theme.lower()
    
    emoji_map = {
        'work': '💼', 'career': '💼', 'job': '💼', 'professional': '💼',
        'health': '🏋️', 'fitness': '🏋️', 'exercise': '🏋️', 'wellness': '🏋️',
        'relationship': '💝', 'love': '💝', 'partner': '💝', 'dating': '💝',
        'friend': '👥', 'social': '👥', 'community': '👥',
        'learn': '📚', 'study': '📚', 'education': '📚', 'knowledge': '📚',
        'creative': '🎨', 'art': '🎨', 'music': '🎨', 'writing': '🎨',
        'tech': '💻', 'coding': '💻', 'programming': '💻', 'software': '💻',
        'mental': '🧠', 'mind': '🧠', 'psychology': '🧠', 'thinking': '🧠',
        'spiritual': '🙏', 'faith': '🙏', 'belief': '🙏', 'meditation': '🙏',
        'family': '👨‍👩‍👧', 'parent': '👨‍👩‍👧', 'sibling': '👨‍👩‍👧',
        'money': '💰', 'finance': '💰', 'financial': '💰', 'budget': '💰',
        'goal': '🎯', 'achievement': '🎯', 'success': '🎯', 'progress': '🎯',
        'content': '🎥', 'video': '🎥', 'youtube': '🎥', 'stream': '🎥',
        'project': '🔧', 'build': '🔧', 'create': '🔧', 'develop': '🔧',
    }
    
    for keyword, emoji in emoji_map.items():
        if keyword in theme_lower:
            return emoji
    
    return '📝'  # Default
