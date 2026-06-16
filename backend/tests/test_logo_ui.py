from unittest.mock import patch
from app.logo_studio.generator import logo_studio
from app.ui_generator.generator import ui_generator

@patch("app.services.llm_service.LLMService.generate_structured")
def test_logo_studio_generator(mock_generate):
    mock_response = {
        "concepts": ["Concept 1: Tech connection"],
        "brand_colors": [{"name": "Teal", "hex": "#0d9488", "usage": "Primary"}],
        "typography": [{"font_family": "Inter", "category": "Heading", "weights": ["700"]}],
        "ai_generation_prompts": ["dall-e prompts"],
        "logo_svg_light": "<svg>light</svg>",
        "logo_svg_dark": "<svg>dark</svg>",
        "logo_svg_icon": "<svg>icon</svg>"
    }
    mock_generate.return_value = mock_response

    branding = logo_studio.generate_branding_package("Test Fitness App")
    
    assert branding["concepts"] == ["Concept 1: Tech connection"]
    assert branding["logo_svg_light"] == "<svg>light</svg>"
    mock_generate.assert_called_once()

@patch("app.services.llm_service.LLMService.generate_structured")
def test_ui_generator(mock_generate):
    mock_response = {
        "screens": [{"name": "Home", "purpose": "Welcome", "key_elements": ["Grid"]}],
        "user_flows": [{"flow_name": "Auth", "steps": ["Click"]}],
        "component_hierarchy": [{"component_name": "Button", "type": "Button", "props_and_states": "active"}],
        "dashboard_layout": "SaaS Layout",
        "design_system": {"colors": "#000"},
        "wireframe_descriptions": [{"screen_name": "Home", "wireframe_layout_markdown": "MD"}],
        "ui_generation_prompts": ["ui prompt"]
    }
    mock_generate.return_value = mock_response

    ui_spec = ui_generator.generate_ui_blueprint("Test Fitness App")
    
    assert ui_spec["dashboard_layout"] == "SaaS Layout"
    assert ui_spec["design_system"] == {"colors": "#000"}
    mock_generate.assert_called_once()
