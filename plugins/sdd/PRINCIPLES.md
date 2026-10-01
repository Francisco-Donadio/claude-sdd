# Pipeline Principles — NON-NEGOTIABLE

Every agent in the SDD→TDD pipeline (and the orchestrator) MUST read and obey
this file before starting. These rules override convenience. If a rule blocks
you, STOP and report to the orchestrator — do not work around it.

> **Project conventions come first.** This file is project-agnostic. Before you
> start, discover the current project's own rules from its `CLAUDE.md`,
> `AGENTS.md`, `README`, `CONTRIBUTING`, package manifests, lint/format config,
> and — most reliably — its existing code. Where a project states a specific
> rule (stack, file layout, commit format, test command), that rule wins over
> the generic guidance here.

---

## 1. Strict TDD (red → green → refactor)
- **No production code before a failing test exists.** The test-author writes
  tests first and confirms they fail for the right reason (a real assertion /
  missing implementation, not a syntax or import error).
- The implementer writes the **minimum** code to make tests pass, then refactors.
- **Never weaken, skip, `xfail`, or delete a test to make it pass.** If a test
  looks wrong versus the spec, STOP and report it — do not silently edit it.
- **Carve-out (no-tests mode):** TDD may be skipped ONLY when the orchestrator has
  put the run in no-tests mode — i.e. the user opted out (`--no-tests`) or the
  change has no testable behavior (pure config, copy/text, styling, docs,
  type-only, dependency bump, pure rename/move). In that mode, skipping tests is
  expected and is NOT a violation. The skip must be recorded (spec, verifier
  report, archive, memory) and must never be presented as if test coverage exists.
  Any change with real behavior/logic still requires tests — do not use the
  carve-out to dodge them.

## 2. Lint + format gate (definition of "done")
Code is NOT done until the project's own lint and format checks pass for the
affected area. Discover the commands from the project (its `CLAUDE.md`/`AGENTS.md`,
`package.json` scripts, `Makefile`, `pyproject.toml`, pre-commit config, CI). Run
the format step then the lint step before declaring work done. The verifier treats
a lint/format failure as a FAIL.

## 3. Scope discipline
Implement only what the spec requires. New ideas, refactors, and "while I'm here"
changes go into the `## Follow-ups` section of the archive — not into this change.

---

## 4. Tech stack & libraries (use what's already here — don't introduce new deps)
- Use the languages, frameworks, and libraries the project **already** depends on.
  Discover them from the package manifests (`package.json`, `pyproject.toml`,
  `go.mod`, `Cargo.toml`, `pom.xml`, etc.) and the existing code — do not assume.
- Match the existing pattern for the resource you're touching (the data store, the
  HTTP/API layer, state management, the module the logic belongs in). Don't
  introduce a parallel way of doing something that already has an established one.
- **Adding a dependency requires explicit approval** — flag it at a checkpoint
  with justification; don't add packages silently.
- If the same logic could live in more than one place/service, verify the source
  of truth before editing rather than assuming.
- Prefer invoking project tools through their own entry points (project scripts,
  a virtualenv binary, the task runner) rather than brittle chained shell commands.

## 5. File structure & where new code goes
- Put new code where the project's existing conventions dictate. Find the nearest
  analogous feature (a similar endpoint, model, component, job, migration) and
  mirror its location and wiring. The explorer's report should tell you where.
- Tests live where the subproject already keeps them, matching the existing
  framework and naming.
- Pipeline artifacts go ONLY in the absolute `<feature-folder>` the orchestrator
  gives you (it lives at `<workspace-root>/.agent-work/<feature-slug>/`, where the
  workspace root is the directory `/sdd` was invoked in). Always use that absolute
  path — never a bare relative `.agent-work/…`, which would land inside whichever
  sub-repo you happen to be `cd`'d into. The workspace root may hold several
  repos; there is exactly one `.agent-work/` at its top level and never one inside
  a sub-repo. Never mix artifacts into source folders.

## 6. Commit format
- **Single-line commit messages, no extended body** (unless the project requires
  otherwise).
- Follow the project's commit convention if it has one — e.g. some repos require
  a Conventional Commits type prefix (`feat:`, `fix:`, `chore:`, `refactor:`,
  `test:`, `docs:`) and reject commits without one. Check `CONTRIBUTING`, commit
  hooks, and recent `git log` before writing the message.
- **Only commit when the user explicitly asks.** Never commit secrets. Treat
  credentials found in docs/READMEs as stale — do not propagate them.

## 7. Honesty
Report outcomes faithfully. If tests fail, say so with the real output. If a step
was skipped, say so. Never claim a test passed without having run it.

## 8. Code comments — minimal
Do NOT add comments to code by default. The code should read clearly on its own
(good names, small functions). Add a comment ONLY when it earns its place:
- a genuinely difficult or non-obvious function/algorithm,
- a deliberate decision or trade-off whose reasoning isn't visible from the code
  (e.g. "rounding up here because this domain's arithmetic always rounds up"),
- a workaround, gotcha, or external constraint a future reader would trip on.
No restating-what-the-code-does comments, no decorative banners, no commented-out code.

**Never reference tickets, acceptance criteria, or requirement IDs in code or tests.**
Do not put ticket numbers (e.g. `JIRA-123`), `AC`/acceptance-criteria labels, or
`FR-n` requirement IDs in comments, test names, `describe`/`it` strings,
docstrings, or anywhere else in the source. Traceability to the spec belongs in the
pipeline artifacts (`spec.md`, `tests.md`, the archive) — not in the code. A comment
is justified only by the "what/why" criteria above, never by a ticket or requirement
reference.

## 9. Explain decisions to help the user learn
The user wants to improve their knowledge. So when you make a non-trivial choice,
EXPLAIN it — the "why", the alternatives considered, and the trade-off — in plain
language, at the level of teaching, not just stating. This applies to:
- the orchestrator's status updates and checkpoints (summarize the key decisions
  and what was learned, not just "done"),
- the architect/designer artifacts (already include trade-offs — make the
  reasoning legible to someone learning the stack),
- any time you pick a library, pattern, or approach over an alternative.
Be concise but instructive. Favor "I chose X over Y because Z" over bare assertions.
