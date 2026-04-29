import json
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

sys.path.append(".")

from src.agent import run_agent
from src.prompts import EVAL_JUDGE_PROMPT

load_dotenv()


def clean_json(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    return text.strip()


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


def llm_judge(query: str, response) -> dict:
    client = _get_client()

    prompt = f"""
USER QUERY:
"{query}"

SYSTEM RESPONSE:
{response.model_dump_json(indent=2)}

Please evaluate this response using the criteria provided.
"""

    result = client.models.generate_content(
        model="publishers/google/models/gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=EVAL_JUDGE_PROMPT),
    )
    raw = clean_json(result.text)
    return json.loads(raw)


with open("evals/test_cases.json", encoding="utf-8") as file:
    test_cases = json.load(file)

results = []
passed = 0

for tc in test_cases:
    print(f"\n🧪 Running {tc['id']}: {tc['input'][:60]}...")
    try:
        response = run_agent(tc["input"])

        clarify_ok = response.needs_clarification == tc["should_clarify"]
        fallback_ok = (response.fallback_message_en is not None) == tc["should_fallback"]
        has_ar = (
            all(p.name_ar and p.description_ar for p in response.products)
            if response.products
            else True
        )

        judge_result = llm_judge(tc["input"], response)
        judge_total = judge_result.get("total_score", 0)
        judge_pass = judge_total >= 8
        judge_required = not tc["should_fallback"]

        case_pass = all(
            [
                clarify_ok,
                fallback_ok,
                has_ar,
                (judge_pass if judge_required else True),
            ]
        )
        status = "✅ PASS" if case_pass else "❌ FAIL"
        if case_pass:
            passed += 1

        results.append(
            {
                "id": tc["id"],
                "status": status,
                "clarify_correct": clarify_ok,
                "fallback_correct": fallback_ok,
                "arabic_present": has_ar,
                "products_returned": len(response.products),
                "judge_total": judge_total,
                "judge_verdict": judge_result.get("overall_verdict"),
                "judge_required": judge_required,
                "judge_details": judge_result,
            }
        )
        print(f"  {status} | Judge: {judge_total}/12")
    except Exception as exc:
        results.append({"id": tc["id"], "status": "❌ ERROR", "error": str(exc)})
        print(f"  ❌ ERROR: {exc}")

print(f"\n{'=' * 50}")
print(f"📊 Results: {passed}/{len(test_cases)} passed")
print(json.dumps(results, indent=2))
