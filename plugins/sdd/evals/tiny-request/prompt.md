---
description: A typo fix. The orchestrator should say the full pipeline is overkill and offer a shortened path.
tags: [smoke]
runs: 2
max_turns: 20
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

/sdd:run fix the typo "recieve" in README.md
