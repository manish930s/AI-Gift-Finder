# Loom Script (3 minutes)

0:00 - 0:20  Intro
"I built a bilingual AI Gift Finder for Mumzworld using Vertex AI, RAG, and a
synthetic catalog. It returns structured EN/AR recommendations with uncertainty handling."

0:20 - 1:00  Demo 1: Normal query
Input: "gift for a 6-month-old under 200 AED"
Show bilingual cards, reasoning, and confidence. Mention catalog grounding and price fit.

1:00 - 1:25  Demo 2: Vague query
Input: "something nice"
Show clarification question in both English and Arabic.

1:25 - 1:50  Demo 3: Arabic query
Input: "هدية لطفل عمره سنة"
Show Arabic-first reasoning and bilingual output.

1:50 - 2:10  Demo 4: Out-of-scope
Input: "buy me an iPhone"
Show graceful fallback in both languages.

2:10 - 2:40  Evals
Run: python evals/run_evals.py
Highlight "12/12 passed" in the output.

2:40 - 3:00  Wrap
Quickly point to README, EVALS.md, and TRADEOFFS.md.
Mention Vertex models used: text-multilingual-embedding-002 and gemini-2.5-flash.
