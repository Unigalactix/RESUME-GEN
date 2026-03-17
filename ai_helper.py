import json
import os

from dotenv import load_dotenv
import google.generativeai as genai


DEFAULT_MODEL_NAME = "gemini-2.5-flash"

load_dotenv()

_api_key = os.getenv("GEMINI_API_KEY", "").strip()
if _api_key:
    genai.configure(api_key=_api_key)


def is_ai_configured():
    return bool(_api_key)


def get_ai_status():
    return {
        "configured": is_ai_configured(),
        "message": "Gemini API key detected." if is_ai_configured() else "Missing GEMINI_API_KEY. AI features will fall back to basic behavior.",
    }


def strip_code_fences(text):
    cleaned = (text or "").strip()
    if cleaned.startswith("```json"):
        return cleaned[7:-3].strip()
    if cleaned.startswith("```"):
        return cleaned[3:-3].strip()
    return cleaned


def parse_json_response(text):
    cleaned = strip_code_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        first_object = cleaned.find("{")
        last_object = cleaned.rfind("}")
        if first_object != -1 and last_object != -1 and last_object > first_object:
            return json.loads(cleaned[first_object:last_object + 1])

        first_array = cleaned.find("[")
        last_array = cleaned.rfind("]")
        if first_array != -1 and last_array != -1 and last_array > first_array:
            return json.loads(cleaned[first_array:last_array + 1])

        raise


def generate_json(prompt, system_instruction=None, fallback=None, model_name=DEFAULT_MODEL_NAME):
    if not is_ai_configured():
        return fallback

    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction,
        generation_config={"response_mime_type": "application/json"},
    )
    response = model.generate_content(prompt)
    return parse_json_response(response.text)


def generate_text(prompt, system_instruction=None, model_name=DEFAULT_MODEL_NAME):
    if not is_ai_configured():
        raise RuntimeError("Gemini API key not configured.")

    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction,
    )
    response = model.generate_content(prompt)
    return (response.text or "").strip()