from typing import Dict, Any
from app.services.llm_service import LLMService

class UIGeneratorManager:
    @classmethod
    def generate_ui_blueprint(cls, idea: str) -> Dict[str, Any]:
        """Generates screen list, user flows, component hierarchy, design systems, and wireframe specs."""
        system_instruction = (
            "You are a Senior Product UI/UX Designer and Frontend Architect.\n"
            "Given a project idea, generate a complete UI design blueprint and frontend design system.\n"
            "Your output must be structured strictly as a JSON object containing:\n"
            "- 'screens': list of objects with 'name', 'purpose', 'key_elements' (list of strings).\n"
            "- 'user_flows': list of objects with 'flow_name', 'steps' (list of strings).\n"
            "- 'component_hierarchy': list of objects with 'component_name', 'type' (e.g. 'Button', 'Card', 'Sidebar'), 'props_and_states' (string description).\n"
            "- 'dashboard_layout': string describing the layouts, layout grids, columns, sidebar configurations.\n"
            "- 'design_system': object with 'colors' (hexes), 'spacing_scale' (e.g. padding details), 'border_radius' (e.g. rounded sizes), 'shadows' (standard styles).\n"
            "- 'wireframe_descriptions': list of objects with 'screen_name', 'wireframe_layout_markdown' (a clean text layout/visual description of where headers, cards, tables sit).\n"
            "- 'ui_generation_prompts': list of strings with detailed prompts for generative image models to generate UI mockups."
        )

        prompt = f"UI blueprint and design guidelines for: {idea}"
        return LLMService.generate_structured(prompt=prompt, system_instruction=system_instruction)

ui_generator = UIGeneratorManager()
