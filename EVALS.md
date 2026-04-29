# Evals

## Rubric

| Criterion | Pass condition |
| --- | --- |
| Clarification | Asks a single question when the query is vague |
| Fallback | Returns a graceful refusal when out of scope |
| Arabic quality | Output reads naturally (not a literal translation) |
| Price adherence | Recommendations stay within stated budget |
| Scope refusal | Rejects out-of-scope queries without hallucinations |

## Test cases

See evals/test_cases.json for the full list of 12 cases.

## Latest results

- Run date: Apr 29, 2026
- Summary: 12/12 passed

## Known failure modes

- Very unusual age ranges can reduce retrieval quality
- Extremely low budgets can only return fallbacks by design
- Some Vertex models are region-specific and must be pinned
