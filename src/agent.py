import json
import os
from functools import lru_cache

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.prompts import CLARIFICATION_SYSTEM_PROMPT, MAIN_SYSTEM_PROMPT
from src.retriever import retrieve_products
from src.schema import GiftResponse

load_dotenv()

RETRIEVAL_K = 6


def clean_json(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    return text.strip()


@lru_cache(maxsize=1)
def _get_client() -> genai.Client:
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not project or not location or not credentials_path:
        raise RuntimeError(
            "Vertex AI settings are missing. Set GOOGLE_CLOUD_PROJECT, "
            "GOOGLE_CLOUD_LOCATION, and GOOGLE_APPLICATION_CREDENTIALS in .env."
        )
    if not os.path.exists(credentials_path):
        raise RuntimeError(
            f"Service account key file not found: {credentials_path}"
        )
    return genai.Client(vertexai=True, project=project, location=location)


def _parse_response(raw: str) -> GiftResponse:
    cleaned = clean_json(raw)
    data = json.loads(cleaned)
    return GiftResponse(**data)


def _should_force_assumption(user_query: str) -> bool:
    lowered = user_query.lower()
    age_keywords = [
        "newborn",
        "month",
        "months",
        "year",
        "years",
        "baby",
        "infant",
        "toddler",
        "child",
        "pregnant",
        "mom",
        "mother",
    ]
    if any(char.isdigit() for char in lowered):
        return True
    return any(keyword in lowered for keyword in age_keywords)


def _augment_query_with_budget(user_query: str) -> str:
    return f"{user_query} (No budget provided; assume 100-300 AED.)"


def _build_products_context(products: list[dict]) -> str:
    compact = []
    for item in products:
        compact.append(
            {
                "name": item.get("name"),
                "name_ar": item.get("name_ar"),
                "price_aed": item.get("price_aed"),
                "category": item.get("category"),
                "age_range": item.get("age_range"),
                "description": item.get("description"),
                "description_ar": item.get("description_ar"),
                "tags": item.get("tags"),
            }
        )
    return json.dumps(compact, ensure_ascii=False, indent=2)


def _run_agent_once(client: genai.Client, user_query: str) -> GiftResponse:
    retrieved = retrieve_products(user_query, top_k=RETRIEVAL_K)
    products_context = _build_products_context(retrieved)

    prompt = f"""
User query: "{user_query}"

Retrieved products from catalog (use ONLY these — do not invent products):
{products_context}

Now return your JSON gift recommendation.
"""

    response = client.models.generate_content(
        model="publishers/google/models/gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=MAIN_SYSTEM_PROMPT
        ),
    )
    return _parse_response(response.text)


def _error_response(message: str) -> GiftResponse:
    return GiftResponse(
        query_understood_en="Error processing request.",
        query_understood_ar="حدث خطأ أثناء معالجة الطلب.",
        products=[],
        needs_clarification=False,
        clarification_question_en=None,
        clarification_question_ar=None,
        fallback_message_en=message,
        fallback_message_ar="تعذر معالجة الطلب. يرجى المحاولة مرة أخرى.",
    )


def run_agent(user_query: str) -> GiftResponse:
    try:
        client = _get_client()
        query = (
            _augment_query_with_budget(user_query)
            if _should_force_assumption(user_query)
            else user_query
        )
        return _run_agent_once(client, query)
    except Exception as exc:
        return _error_response(f"Error: {exc}")


def run_agent_followup(original_query: str, clarification_reply: str) -> GiftResponse:
    try:
        client = _get_client()
        combined = f"{original_query} — {clarification_reply}"
        retrieved = retrieve_products(combined, top_k=RETRIEVAL_K)
        products_context = _build_products_context(retrieved)

        prompt = f"""
original_query: "{original_query}"
clarification_reply: "{clarification_reply}"

retrieved_products:
{products_context}

Now provide a confident gift recommendation in the required JSON format.
"""

        response = client.models.generate_content(
            model="publishers/google/models/gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=CLARIFICATION_SYSTEM_PROMPT
            ),
        )
        return _parse_response(response.text)
    except Exception as exc:
        return _error_response(f"Error: {exc}")
