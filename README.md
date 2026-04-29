# Mumzworld AI Gift Finder

AI-powered gift recommendation engine for Mumzworld with bilingual (EN/AR) output.

## Quick start (under 5 minutes)

1. Install dependencies
   pip install -r requirements.txt

2. Configure Vertex AI credentials
   cp .env.example .env
   # Edit .env and set GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION,
   # and GOOGLE_APPLICATION_CREDENTIALS (path to your service account JSON)

3. Enable Vertex AI API and billing (one-time)
   https://console.cloud.google.com/apis/api/aiplatform.googleapis.com

4. Ingest the catalog (one-time)
   python src/embed.py

5. Run the app
   streamlit run app.py

## How it works

- Data: 98-product synthetic catalog in data/catalog.json
- Embeddings: publishers/google/models/text-multilingual-embedding-002
- Retrieval: ChromaDB persistent store at ./chroma_db
- LLM: publishers/google/models/gemini-2.5-flash
- Validation: all responses parsed via Pydantic GiftResponse
- Clarification: prompt rules + post-processing to avoid over-clarification

## Evals

- Run: python evals/run_evals.py
- Latest: 12/12 passed (Apr 29, 2026)
- Details: EVALS.md

## Tradeoffs

See TRADEOFFS.md

## Tooling

| Tool | Role |
| --- | --- |
| Vertex AI Gemini | Agent reasoning, structured JSON output, Arabic generation |
| Vertex AI Embeddings | Embedding product catalog and user queries |
| ChromaDB | Local vector store for retrieval |
| Streamlit | UI with bilingual output cards |
| Pydantic v2 | Output schema validation |
| pytest / custom runner | Eval harness across 12 test cases |

How I used AI tools:
- Used an LLM to generate the synthetic product catalog (98 products, EN/AR)
- Prompts were written and iterated manually and kept in src/prompts.py
- LLM-as-judge eval prompt used in evals/run_evals.py

What worked:
- Vertex embeddings with RETRIEVAL_QUERY/RETRIEVAL_DOCUMENT improved recall
- Explicit prompt examples improved reasoning specificity

What did not:
- Models vary by Vertex project and region; exact model names were pinned

## Project layout

- data/catalog.json
- src/
- evals/
- app.py
