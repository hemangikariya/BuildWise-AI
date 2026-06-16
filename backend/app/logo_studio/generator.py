from typing import Dict, Any
from app.services.llm_service import LLMService

class LogoStudioManager:
    @classmethod
    def generate_branding_package(cls, idea: str) -> Dict[str, Any]:
        """Generates branding suggestions, color palettes, typography, and raw SVGs."""
        system_instruction = (
            "You are a Senior Creative Director and Brand Identity Designer.\n"
            "Given a project idea, generate a complete branding guide and logo suite.\n"
            "The logo must incorporate themes of AI, Software Engineering, Architecture, and Agentic Intelligence.\n"
            "Your output must be structured strictly as a JSON object containing:\n"
            "- 'concepts': list of strings detailing logo concepts and their meanings.\n"
            "- 'brand_colors': list of objects with 'name', 'hex', 'usage' (e.g. 'Primary', 'Background', 'Accent').\n"
            "- 'typography': list of objects with 'font_family', 'category' (e.g. 'Heading', 'Body'), 'weights' (list of strings).\n"
            "- 'ai_generation_prompts': list of strings with highly detailed text prompts for image generators like Midjourney/DALL-E.\n"
            "- 'logo_svg_light': string containing a raw, clean, responsive <svg> markup for light mode (using your brand colors).\n"
            "- 'logo_svg_dark': string containing a raw, clean, responsive <svg> markup for dark mode.\n"
            "- 'logo_svg_icon': string containing a raw, clean, responsive <svg> markup of the icon-only version.\n\n"
            "Ensure the SVG elements look modern, clean, premium, and are valid SVGs with correct viewboxes and vector paths (e.g., circles, polygons, curves representing tech, connectivity, or brackets)."
        )

        prompt = f"Branding guidelines and Logo Suite for: {idea}"
        return LLMService.generate_structured(prompt=prompt, system_instruction=system_instruction)

logo_studio = LogoStudioManager()
