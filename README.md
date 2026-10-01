# claude-sdd: SDD → TDD pipeline for Claude Code

A Claude Code plugin. Install it, then run `/sdd:run <feature>`.

## Install

```
/plugin marketplace add Francisco-Donadio/claude-sdd
/plugin install sdd@claude-sdd
```

Choose **user scope** to get it in every project. Check it worked by typing `/`
and looking for `/sdd:run`.

**Update:** `/plugin marketplace update claude-sdd`, then `/reload-plugins`.
Auto-update is off by default for this marketplace. You can turn it on in
`/plugin` → **Marketplaces**.

**Pin a version:** `/plugin marketplace add Francisco-Donadio/claude-sdd#sdd--v1.0.0`.

**Migrating from the copied-files setup?** Remove the old copies from
`~/.claude/agents/` (the ten agents + `PRINCIPLES.md`) and
`~/.claude/commands/sdd.md`. Otherwise you'll have both `architect` and
`sdd:architect` and two pipelines.

## Pipeline overview

A main-session **orchestrator** (the `/sdd:run` skill) delegates to ten specialized subagents that
follow Spec-Driven Development (SDD) then Test-Driven Development (TDD). You only
ever talk to the orchestrator; it relays work between agents through shared
artifact files. Plugin agents are namespaced: `sdd:explorer`, `sdd:architect`, …

## How it works

```
YOU ──▶ MAIN SESSION (orchestrator, has the Agent tool)
                │  spawns one agent per stage, in order, relaying artifacts
                ▼
 explorer → spec-writer → task-planner → architect → designer
          → test-author → implementer → REVIEW (tiered, +/security-review)
          → verifier → [/verify] → archivist

 stacked mode: test-author → implementer → REVIEW → verifier → local commit
               repeats once per slice, each on a branch off the previous slice
```

All agents obey the non-negotiable rules in **`PRINCIPLES.md`** (strict TDD,
lint/format gate, tech-stack & library rules, file structure, commit format).
The orchestrator also runs a post-implementation **review** (tiered — see below)
and, when the change touches sensitive areas (auth/authorization, secrets/config,
money/PII, external integrations), the `/security-review` skill on top. It offers
`/verify` at closeout.

Subagents run in isolated contexts and **cannot call each other** — the
orchestrator passes each one's output file to the next. That is why every agent
reads/writes files in a per-feature folder instead of messaging peers.

**Memory recall.** Before stage 1, the orchestrator searches Engram
(`mem_search`) for prior decisions/conventions/gotchas relevant to the request and
writes a short digest to `memory.md`. The explorer, spec-writer, and architect
read that file — it's how long-term memory reaches them, since the agents can't
call Engram themselves. Recall is best-effort: if Engram is unavailable the run
continues normally. (Saving back to memory still happens in the main session's
always-active protocol, not inside the agents.)

## Usage

```
/sdd:run add a CSV export button to the report page
```

This runs the whole pipeline with approval checkpoints after the **spec**, after
the **design** (before any code), and at **closeout**. For a trivial change the
orchestrator will offer a shortened path.

### Skipping tests

TDD is the default, but some changes have no testable logic (config, copy, CSS,
docs, type-only edits, dependency bumps, pure renames). For those, opt out:

```
/sdd:run --no-tests bump the chart library to v5 and adjust the import path
```

In no-tests mode the `test-author` stage is skipped and the `verifier` runs
lint/format + a manual acceptance check instead of a suite. The skip is **always
recorded** (spec, verification, archive, memory) and never presented as coverage.
For an obviously-untestable change the orchestrator will also *propose* skipping
at Checkpoint 1 — but it won't skip silently. Anything with real behavior still
gets tests.

### Choosing the review depth

After the implementer, the pipeline reviews the diff at one of four **tiers** —
cost climbs sharply, so it defaults cheap and escalates only when warranted:

| Tier | What runs | Cost |
| --- | --- | --- |
| `none` | nothing (auto only for no-logic no-tests changes) | free |
| `light` (default) | the **`reviewer`** agent — one focused pass, no fan-out | ~1 agent |
| `standard` | the `/code-review` skill at **medium** effort | multi-lens |
| `deep` | the `/code-review` skill at **high/max** effort | a verifier per finding |

Override the tier explicitly:

```
/sdd:run --review deep rework the auth token refresh logic
/sdd:run --review none fix a typo in the onboarding copy
```

Without a flag, the orchestrator auto-picks: **`deep`** if the change touches
sensitive areas (auth, secrets, money, PII, integrations) or the diff is large;
otherwise **`light`**. The `/security-review` pass is decided separately by its
own sensitive-area heuristic and can stack on top of any tier.

### Stacked PRs for big tickets

When a ticket is too big for one reviewable PR, the pipeline can deliver it as a
**stack**: ordered branches in one repo, each branched off the previous one, each
becoming its own small PR against the repo's PR base branch.

| Flag | Behavior |
| --- | --- |
| *(none, default)* | The task-planner estimates the size and proposes slices only above about **400 lines or 8 files**. Otherwise it recommends a single PR. |
| `--stack` | Always propose slices, whatever the size. Useful when the estimate is probably low, or for a natural "refactor, then feature" split. |
| `--no-stack` | Never slice. Always one PR. |

```
/sdd:run --stack ABC-123 migrate report exports to the new jobs service
```

How it runs:

1. **task-planner** groups tasks into slices. Each slice passes tests and lint on
   its own, is safe to merge alone (unfinished parts stay hidden or behind a
   flag), and stays in one repo.
2. **architect** checks that each slice boundary is a real split point in the
   design, and corrects the slicing if not.
3. **Checkpoint 2** asks: *single PR or stack of N?* You can always decline.
   Approving a stack lets the orchestrator create **local** branches and one
   commit per slice. Nothing is pushed.
4. Steps 6–9 (tests, implement, review, verify) run **once per slice**, limited
   to that slice's tasks. The full suite must be green with slices 1..k applied.
5. At closeout, run `/sdd:publish-stack <slug>` from the repo. It pushes the branches,
   opens the PRs bottom-up (each PR's base is the previous slice's branch), adds
   a `### Stack` list linking every PR, and runs any ticket-status step your
   repo's `CLAUDE.md` defines, once for the whole stack.

Notes:
- **Branch names** keep the ticket prefix on every slice
  (`ABC-123-1-schema`, `ABC-123-2-service`, …) so tracker integrations link
  them all.
- **Work spanning several repos is not one stack.** Each repo gets its own stack
  plus a merge order in `stack.md` (e.g. API before app).
- **Merge bottom-up.** After a slice is squash-merged, rebase the next branch
  with `git rebase --onto origin/<base> <old slice tip> <next branch>` and
  force-push with lease. `/sdd:publish-stack` prints this reminder.
  Restacking is manual for now.
- A tiny request never stacks.

### Extending a finished feature

A finished `/sdd` run is a hard stop — the agents are one-shot and nothing keeps
running. To add to a feature you already shipped without starting cold, use
extend mode:

```
/sdd:run --extend health-check-endpoint also add a /api/ready readiness probe
```

(Or pass the slug in plain words: `/sdd:run extend the <slug> feature: …`.) Extend mode reuses the surviving
`spec.md` / `architecture.md` / `design.md` + the archive as its baseline instead
of re-exploring, appends the new requirements as a delta, **skips** stages the
addition doesn't need (e.g. architect/designer when there's no design change), and
**updates** the archive + memory rather than duplicating them. If the slug doesn't
exist, it tells you instead of guessing.

A plain `/sdd:run …` (no `--extend`) always starts a **brand-new** feature folder from
stage 1.

You can also invoke any single agent directly, e.g. `@agent-sdd:explorer map
how the auth flow works` — handy when you don't need the full pipeline.

The orchestrator lives in `plugins/sdd/skills/run/SKILL.md`.

## Artifacts

Each run creates `<workspace-root>/.agent-work/<feature-slug>/`, where the
workspace root is the directory you invoked `/sdd` in. If that directory holds
several repos (e.g. `web/`, `app/`, `api/`), the single
`.agent-work/` folder sits at the top level — never inside a sub-repo — so all
artifacts for a run stay in one place regardless of which repo the change touches:

| File | Author |
| --- | --- |
| `request.md` | orchestrator |
| `memory.md` | orchestrator (Engram recall) |
| `exploration.md` | explorer |
| `spec.md` | spec-writer |
| `tasks.md` | task-planner (checked off by implementer), incl. `## Slices` |
| `architecture.md` | architect |
| `design.md` | designer |
| `stack.md` | orchestrator (stacked mode only; statuses updated by `/sdd:publish-stack`) |
| `tests.md` + test files | test-author |
| `implementation.md` + code | implementer |
| `review.md` | reviewer (light tier only) |
| `verification.md` | verifier |
| `archive/<slug>.md` | archivist |

**At a successful closeout the orchestrator** cleans up scratch: deletes
`request.md`, `memory.md`, `exploration.md`, `tasks.md`, `tests.md`,
`implementation.md`, `review.md`, `verification.md`. It **keeps** `spec.md`, `architecture.md`,
`design.md`, `stack.md` (if any, since `/sdd:publish-stack` needs it), and
`archive/<slug>.md` (self-contained record). If a run FAILS or is
abandoned, nothing is deleted — everything stays for debugging.

Saving to Engram is **not** a scripted pipeline step — the session's always-active
memory protocol captures decisions and discoveries on its own.

Consider adding `.agent-work/` to `.gitignore` if you don't want artifacts committed.

## The agents

| Agent | Model | Role |
| --- | --- | --- |
| explorer | haiku | read-only codebase recon |
| spec-writer | opus | SDD — testable spec (what/why) |
| task-planner | sonnet | ordered, dependency-aware tasks + size estimate / slice plan |
| architect | opus | technical shape, data flow, trade-offs, slice-seam check |
| designer | opus | exact interfaces, schemas, errors |
| test-author | sonnet | TDD red — failing tests first |
| implementer | sonnet | TDD green — code to pass tests |
| reviewer | sonnet | light-tier diff review (one pass, no fan-out) |
| verifier | sonnet | independent PASS/FAIL gate with evidence |
| archivist | haiku | durable closeout record |

## Project conventions

The plugin carries no project-specific stack knowledge. Each agent discovers the
current repo's stack, structure, and conventions from its own `CLAUDE.md` /
`AGENTS.md` / `README` / manifests and existing code. Team-specific rules belong
in the repo's `CLAUDE.md`, for example:

- the PR base branch (e.g. `staging`); otherwise the default branch is used;
- a branch-naming rule (e.g. ticket-id prefix);
- what to do when a PR opens (e.g. move the ticket to "In review").

**Optional: Engram memory.** If the Engram MCP is connected, the orchestrator
recalls prior decisions before stage 1. Without it the pipeline runs normally.

## Customizing

- **Change a model or tools:** edit the `model:` / `tools:` line in that agent's
  file under `plugins/sdd/agents/`, bump the version, and release (see below).
- **Override for one project only:** add a same-named agent or skill in that
  repo's `.claude/agents/` or `.claude/skills/`. Project definitions don't
  replace namespaced plugin ones, so name them distinctly and say in the repo's
  `CLAUDE.md` when to use them.
- **Adjust the pipeline / checkpoints:** edit `plugins/sdd/skills/run/SKILL.md`.
- **Change the non-negotiable rules** (TDD, lint gate, commits, structure, what
  counts as "done"): edit `plugins/sdd/PRINCIPLES.md`. Every agent reads it.
- **Try changes locally before releasing:** `claude --plugin-dir ./plugins/sdd`,
  or `/plugin marketplace add ./` from the repo root.

## Releasing a new version

1. Make the change, then run `claude plugin validate ./plugins/sdd`.
2. Bump `version` in `plugins/sdd/.claude-plugin/plugin.json` (semver: patch for
   wording fixes, minor for new options, major for changed flags or behavior).
3. Add an entry to `CHANGELOG.md`.
4. Commit, tag `sdd--v<version>`, push the tag: `git tag sdd--v1.1.0 && git push --tags`.

Users get it on their next `/plugin marketplace update claude-sdd`. The
`version` field is what tells Claude Code there's an update, so a change without
a bump won't reach anyone.
