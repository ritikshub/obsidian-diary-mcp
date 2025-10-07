"""Template generation for diary entries."""

from datetime import datetime
from typing import Optional, List

from .config import RECENT_ENTRIES_COUNT
from .entry_manager import entry_manager
from .analysis import analysis_engine
from .logger import template_logger as logger, log_section


class TemplateGenerator:
    """Generates diary entry templates with AI-powered prompts."""
    
    async def generate_template_content(
        self,
        entry_date: datetime,
        filename: str,
        focus: Optional[str] = None
    ) -> str:
        """Generate template content for a diary entry."""
        log_section(logger, f"Template Generation: {filename}")
        logger.info(f"Entry date: {entry_date.strftime('%A, %B %d, %Y')}")
        
        is_sunday = entry_date.weekday() == 6
        
        if is_sunday:
            # For Sunday: get entries from the past 7 calendar days (actual week)
            from datetime import timedelta
            week_start = entry_date - timedelta(days=7)
            all_entries = entry_manager.get_all_entries()
            recent_entries = [(date, path) for date, path in all_entries if week_start <= date < entry_date]
            logger.info(f"Sunday reflection: Analyzing {len(recent_entries)} entries from {week_start.strftime('%Y-%m-%d')} to {(entry_date - timedelta(days=1)).strftime('%Y-%m-%d')}")
        else:
            # For regular days: get last N entries
            recent_entries = entry_manager.get_all_entries()[:RECENT_ENTRIES_COUNT]
            logger.info(f"Regular day: Using last {len(recent_entries)} entries for context")
        
        # Build weighted context - most recent entry gets more emphasis
        context_parts = []
        for i, (date, path) in enumerate(recent_entries):
            content = entry_manager.read_entry(path)
            if i == 0:  # Most recent
                context_parts.append(f"## MOST RECENT ENTRY ({date.strftime('%Y-%m-%d')}):\n{content}")
            else:
                context_parts.append(f"## Earlier entry ({date.strftime('%Y-%m-%d')}):\n{content}")
        
        recent_text = "\n\n".join(context_parts) if context_parts else ""
        logger.info(f"Context: {len(recent_text):,} chars from {len(recent_entries)} entries (weighted by recency)")
        
        prompt_count = 5 if is_sunday else 3
        logger.info(f"Requesting {prompt_count} AI-generated prompts{' with focus: ' + focus if focus else ''}")
        
        prompts = await analysis_engine.generate_reflection_prompts(
            recent_text, focus, prompt_count, is_sunday
        )
        
        if not prompts:
            logger.warning("No AI prompts generated, using fallback prompts")
            prompts = self._get_fallback_prompts(is_sunday)
        else:
            logger.info(f"✓ Generated {len(prompts)} AI prompts successfully")

        return self._build_template(prompts, is_sunday)
    
    def _get_fallback_prompts(self, is_sunday: bool) -> List[str]:
        """Get fallback prompts when AI generation fails."""
        if is_sunday:
            return [
                "What went well this week, and what felt hard?",
                "What choices did you make that you want to remember?",
                "What do you want to do differently next week?",
                "What's one thing you learned about yourself?",
                "What are you looking forward to or worried about?"
            ]
        else:
            return [
                "What's on your mind right now?",
                "What choices are you thinking about?",
                "What felt good or difficult today?"
            ]
    
    def _build_template(self, prompts: List[str], is_sunday: bool) -> str:
        """Build the template structure with prompts."""
        template_parts = []
        
        if is_sunday:
            template_parts.append("## 🌅 Weekly Synthesis & Alignment")
            template_parts.append("\n*A deeper reflection on the past week and intentional focus for the week ahead*\n")
        else:
            template_parts.append("## 🧠 Reflection Prompts")
            template_parts.append("\n*Building on insights from previous entries*\n")

        for i, prompt in enumerate(prompts, 1):
            template_parts.append(f"**{i}. {prompt}**\n")
            template_parts.append("")
            template_parts.append("")
        
        template_parts.append("---")
        template_parts.append("")
        template_parts.append("## 🧠 Brain Dump")
        template_parts.append("")
        template_parts.append("*Your thoughts, experiences, and observations...*")

        return "\n".join(template_parts)


template_generator = TemplateGenerator()