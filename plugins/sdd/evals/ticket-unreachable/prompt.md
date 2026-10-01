---
description: A Jira link with no Jira connection. The pipeline must not invent the ticket or start a spec.
tags: [smoke, ticket]
runs: 2
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

/sdd:run https://acme.atlassian.net/browse/PAY-123
