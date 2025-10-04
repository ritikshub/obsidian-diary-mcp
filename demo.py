#!/usr/bin/env python3
"""Demonstration of the Obsidian Diary MCP Server functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from obsidian_diary_mcp.server import (
    get_all_entries,
    read_entry,
    generate_reflection_prompts,
    find_related_entries,
)

def demo_template_creation():
    """Demonstrate template creation."""
    print("\n" + "="*70)
    print("🎯 DEMO: Creating a Diary Template")
    print("="*70)
    
    # Get recent entries
    recent_entries = get_all_entries()[:3]
    print(f"\n📚 Analyzing your last {len(recent_entries)} entries:")
    for date, path in recent_entries:
        print(f"   - {date.strftime('%Y-%m-%d')}")
    
    # Read their content
    recent_contents = [read_entry(path) for _, path in recent_entries]
    
    # Generate reflection prompts
    prompts = generate_reflection_prompts(recent_contents)
    
    print("\n🤔 Generated Reflection Prompts:")
    for i, prompt in enumerate(prompts, 1):
        print(f"   {i}. {prompt}")
    
    # Show template structure
    print("\n📝 Template Structure:")
    print("   ✓ Recent Reflections section with links to last 3 entries")
    print("   ✓ Contextual reflection prompts based on your themes")
    print("   ✓ Brain dump section for free writing")
    print("   ✓ Auto-generated backlinks placeholder")

def demo_auto_tagging():
    """Demonstrate auto-tagging functionality."""
    print("\n" + "="*70)
    print("🔗 DEMO: Auto-Tagging with Backlinks")
    print("="*70)
    
    # Use most recent entry
    entries = get_all_entries()
    if entries:
        date, path = entries[0]
        content = read_entry(path)
        
        print(f"\n📄 Analyzing entry from {date.strftime('%Y-%m-%d')}...")
        
        # Find related entries
        related = find_related_entries(content, exclude_date=date.strftime("%Y-%m-%d"))
        
        print(f"\n🎯 Found {len(related)} related entries:")
        for link in related:
            print(f"   {link}")
        
        print("\n💡 How it works:")
        print("   1. Extracts key themes from your entry")
        print("   2. Analyzes all past entries for similar themes")
        print("   3. Uses Jaccard similarity to find the best matches")
        print("   4. Automatically adds backlinks in Obsidian format")

def demo_theme_extraction():
    """Demonstrate theme extraction."""
    print("\n" + "="*70)
    print("🧠 DEMO: Intelligent Theme Detection")
    print("="*70)
    
    entries = get_all_entries()[:3]
    
    print("\n📊 Themes detected in your recent entries:\n")
    
    for date, path in entries:
        content = read_entry(path)
        from obsidian_diary_mcp.server import extract_themes_and_topics
        themes = extract_themes_and_topics(content)
        
        print(f"   {date.strftime('%Y-%m-%d')}:")
        print(f"   → {', '.join(themes[:10])}")
        print()

def main():
    print("\n" + "="*70)
    print("✨ Obsidian Diary MCP Server - Interactive Demo")
    print("="*70)
    print("\nThis demo shows how the MCP server helps you journal more effectively.")
    
    demo_theme_extraction()
    demo_template_creation()
    demo_auto_tagging()
    
    print("\n" + "="*70)
    print("🚀 Next Steps")
    print("="*70)
    print("\n1. Configure Claude Desktop using CLAUDE_CONFIG.md")
    print("2. Start using the tools through Claude:")
    print("   - Ask Claude to 'create a diary template for today'")
    print("   - Write your entry with Claude's help")
    print("   - Save it with auto-generated backlinks")
    print("\n3. Or test interactively with:")
    print("   uv run fastmcp dev src/obsidian_diary_mcp/server.py")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
