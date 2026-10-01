---
type: llm
---

PASS if the reply tells the user the full pipeline is overkill for this change and
offers a shorter path (for example skipping spec/architecture/design, or just
making the edit), or asks whether to proceed that way.
FAIL if the reply presents an architecture or design for the change, or says it
ran the full pipeline.
