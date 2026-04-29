# Tradeoffs

## Why this problem

Gift Finder is a direct GMV driver and matches the brief: retrieval, structured output,
multilingual output, and uncertainty handling in a single demo.

## Why Vertex AI

- Uses the free tier where possible
- Consistent model access in a single project
- Supports both Gemini generation and embeddings

## Why text-multilingual-embedding-002

- Strong multilingual performance for EN/AR
- Works well for short product descriptions and tags

## Why ChromaDB

- Local persistent store with zero infrastructure
- Fast enough for a small catalog

## What I cut

- Multi-turn memory in the UI (could be added with session history)
- Images or scraping (explicitly avoided)
- Structured output via response_schema (kept raw JSON for portability)

## What I would build next

- Metadata filters in retrieval (price range, category)
- Feedback loop (thumbs up/down for fine-tuning)
- Multi-turn context with clarification history
