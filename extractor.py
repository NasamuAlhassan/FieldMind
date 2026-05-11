import json
import os
from typing import Any, Dict

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gemini-2.0-flash"


def _get_model() -> genai.GenerativeModel:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please add it to your .env file.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(MODEL_NAME)


def _clean_json_text(response_text: str) -> str:
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[len("json") :].strip()
    return cleaned


def extract_field_report(report_text: str) -> Dict[str, Any]:
    model = _get_model()
    prompt = f"""
You are an enterprise field intelligence extractor.
Read informal reports from West African field agents. Reports may include broken English,
Pidgin, and local slang. Convert the input into structured enterprise intelligence.

Return ONLY a valid JSON object with exactly these fields:
- agent_name
- location
- client_name
- issue_type (example values: price_dispute, delivery_delay, stock_issue)
- sentiment (must be one of: positive, neutral, frustrated, angry)
- action_needed (boolean)
- urgency (must be one of: low, medium, high)
- summary (1-2 clean sentences)
- tags (array of short strings)
- raw_input

Do not include markdown, explanations, or extra keys.

Input report:
{report_text}
"""

    response = model.generate_content(prompt)
    response_text = response.text if response and response.text else "{}"
    cleaned = _clean_json_text(response_text)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse Gemini output as JSON: {response_text}") from exc

    parsed["raw_input"] = report_text
    return parsed


if __name__ == "__main__":
    sample = "Me I be Kojo from Accra. Client Ama dey vex say price too high and delivery late two days."
    try:
        result = extract_field_report(sample)
        print(json.dumps(result, indent=2))
    except Exception as error:
        print(f"Extraction failed: {error}")
