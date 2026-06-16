import json
import time
import requests
from typing import Any, Dict, Optional
from app.core.config import settings
from app.core.logging import system_logger

class LLMService:
    @classmethod
    def call_gemini(cls, prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
        """Call Gemini API directly via REST."""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        
        contents = []
        if system_instruction:
            contents.append({
                "role": "user",
                "parts": [{"text": f"System Instructions: {system_instruction}\n\nUser Input: {prompt}"}]
            })
        else:
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {}
        }

        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        # Retry logic
        for attempt in range(3):
            try:
                response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
                if response.status_code == 200:
                    res_json = response.json()
                    text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    return text
                else:
                    system_logger.warning(
                        f"Gemini API returned status {response.status_code}: {response.text}. Attempt {attempt + 1}/3"
                    )
            except Exception as e:
                system_logger.warning(f"Error calling Gemini: {str(e)}. Attempt {attempt + 1}/3")
            time.sleep(2 ** attempt)

        raise RuntimeError("Failed to get response from Gemini after 3 attempts.")

    @classmethod
    def call_openai(cls, prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
        """Call OpenAI Chat Completions API via REST."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not configured.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
        }

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": "gpt-4-turbo" if settings.LLM_MODEL.startswith("gemini") else settings.LLM_MODEL,
            "messages": messages
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        # Retry logic
        for attempt in range(3):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=60)
                if response.status_code == 200:
                    res_json = response.json()
                    return res_json["choices"][0]["message"]["content"]
                else:
                    system_logger.warning(
                        f"OpenAI API returned status {response.status_code}: {response.text}. Attempt {attempt + 1}/3"
                    )
            except Exception as e:
                system_logger.warning(f"Error calling OpenAI: {str(e)}. Attempt {attempt + 1}/3")
            time.sleep(2 ** attempt)

        raise RuntimeError("Failed to get response from OpenAI after 3 attempts.")

    @classmethod
    def generate(cls, prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
        """Main LLM dispatcher."""
        if settings.LLM_PROVIDER.lower() == "openai":
            return cls.call_openai(prompt, system_instruction, json_mode)
        else:
            return cls.call_gemini(prompt, system_instruction, json_mode)

    @classmethod
    def generate_structured(cls, prompt: str, system_instruction: str = None) -> Dict[str, Any]:
        """Ensures the response is valid JSON before returning."""
        for attempt in range(2):
            raw_response = cls.generate(prompt, system_instruction, json_mode=True)
            try:
                parsed = json.loads(raw_response)
                return parsed
            except json.JSONDecodeError as e:
                system_logger.warning(f"Failed to parse JSON on attempt {attempt + 1}. Raw: {raw_response}")
                if attempt == 0:
                    # Instruct LLM to fix the formatting
                    prompt = f"Previous response failed JSON decoding with error: {str(e)}.\nPlease output valid JSON only.\n\nOriginal prompt:\n{prompt}"
        raise ValueError("LLM generated output that could not be parsed as valid JSON.")
