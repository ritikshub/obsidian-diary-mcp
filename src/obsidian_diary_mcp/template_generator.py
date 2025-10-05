"""Template generation for diary entries."""

from datetime import datetime
from typing import Optional, List

from .config import RECENT_ENTRIES_COUNT
from .entry_manager import entry_manager
from .analysis import analysis_engine


class TemplateGenerator:
    """Generates diary entry templates with AI-powered prompts."""
    
    async def generate_template_content(
        self,
        entry_date: datetime,
        filename: str,
        focus: Optional[str] = None
    ) -> str:
        """Generate template content for a diary entry."""
        is_sunday = entry_date.weekday() == 6
        
        recent_count = 7 if is_sunday else RECENT_ENTRIES_COUNT
        
        recent_entries = entry_manager.get_all_entries()[:recent_count]
        recent_contents = [entry_manager.read_entry(path) for _, path in recent_entries]
        recent_text = "\n\n".join(recent_contents) if recent_contents else ""
        
        prompt_count = 5 if is_sunday else 3
        prompts = await analysis_engine.generate_reflection_prompts(
            recent_text, focus, prompt_count, is_sunday
        )
        
        if not prompts:
            prompts = self._get_fallback_prompts(is_sunday)

        return self._build_template(prompts, is_sunday)
    
    def _get_fallback_prompts(self, is_sunday: bool) -> List[str]:
        """Get fallback prompts when AI generation fails."""
        if is_sunday:
            return [
                "What patterns from this past week reveal deeper truths about your cognitive frameworks?",
                "How did your decision-making processes evolve throughout the week?",
                "What assumptions about progress and growth were challenged this week?",
                "Where do you need to realign your mental models for the upcoming week?",
                "What philosophical questions emerged from this week's experiences that deserve deeper exploration?"
            ]
        else:
            return [
                "What cognitive patterns or mental models shaped your thinking this period?",
                "How do your current challenges reflect deeper philosophical questions about identity and meaning?",
                "What assumptions about reality, success, or relationships are being tested right now?"
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
        template_parts.append("")
        template_parts.append("")
        template_parts.append("")
        template_parts.append("---")
        template_parts.append("")
        template_parts.append("## 🧠 Memory Links")
        template_parts.append("")
        template_parts.append("*Temporal connections and topic tags will be auto-generated when you complete the entry.*")

        return "\n".join(template_parts)


template_generator = TemplateGenerator()