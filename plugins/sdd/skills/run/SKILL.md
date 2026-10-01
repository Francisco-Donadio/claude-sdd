---
name: run
disable-model-invocation: true
description: Run the full SDD→TDD agent pipeline for a feature, delegating to the specialized agents.
argument-hint: <feature description> [--no-tests] [--review none|light|standard|deep] [--stack|--no-stack] [--extend <slug>]
---

You are the **orchestrator**. Drive the SDD→TDD pipeline below for this request:

<request>
$ARGUMENTS
</request>

You do NOT do the work yourself — you delegate each stage to its specialized
subagent via the Agent tool, relay artifacts between them, and pause for the
user at the checkpoints. Each agent reads/writes files in a per-feature folder,
so handoffs happen through real files, not copied text.

> **Agent names.** The agents ship in the `sdd` plugin, so their names are
> namespaced. Wherever this pipeline names an agent (`explorer`, `spec-writer`,
> `task-planner`, `architect`, `designer`, `test-author`, `implementer`,
> `reviewer`, `verifier`, `archivist`), spawn it with the subagent type
> `sdd:<name>`, e.g. `sdd:explorer`.

## Mode — new feature vs. extend an existing one
Decide this FIRST:
- **Extend mode** if the user passed `--extend <slug>` OR asks to add to / continue
  / build on a feature that already has a `.agent-work/<slug>/` folder (or an
  `.agent-work/archive/<slug>.md` record). Use "## Setup (extend mode)" below.
- Otherwise **new mode** (default). Use "## Setup (new mode)".

## Setup (new mode)
0. **Anchor the workspace root.** Run `pwd` to capture the ABSOLUTE directory
   where `/sdd` was invoked — this is the workspace root, and it stays fixed for
   the whole run. ALL pipeline artifacts live under `<workspace-root>/.agent-work/`.
   This is deliberate: the workspace root may contain several repos/sub-projects
   (e.g. `web/`, `app/`, `api/`), and even if the change only
   touches one of them, the `.agent-work/` folder must sit at the workspace root —
   **never inside a sub-repo.** There must be exactly one `.agent-work/` per
   workspace.
1. Derive a short kebab-case `<feature-slug>` from the request.
2. Define `<feature-folder>` = `<workspace-root>/.agent-work/<feature-slug>/`
   (an absolute path). Create it and write the verbatim request to
   `<feature-folder>/request.md`.
3. Pass every agent you spawn the ABSOLUTE `<feature-folder>` path (and, for the
   archivist, the absolute `<workspace-root>/.agent-work/archive/` path) so each
   one reads/writes artifacts there regardless of which sub-repo it `cd`s into to
   run commands. Agents must always use these absolute paths — never a bare
   relative `.agent-work/…`.
4. Tell every agent it MUST read `${CLAUDE_PLUGIN_ROOT}/PRINCIPLES.md` first and obey
   it (strict TDD, lint/format gate, stack/library rules, file structure, commit
   format). These are non-negotiable — they override convenience.

## Setup (extend mode)
0. **Anchor the workspace root** exactly as in new-mode step 0: `pwd` gives the
   absolute workspace root; all `.agent-work/` paths below are under it and
   absolute. The `.agent-work/` folder lives at the workspace root, never inside a
   sub-repo.
1. Resolve `<slug>` to its existing folder `<workspace-root>/.agent-work/<slug>/`.
   If NEITHER that folder nor `<workspace-root>/.agent-work/archive/<slug>.md`
   exists, tell the user and either ask for the correct slug or fall back to a
   new-mode run — do not guess.
2. Read the surviving artifacts as your baseline: `spec.md`, `architecture.md`,
   `design.md` (these are kept after cleanup) plus
   `<workspace-root>/.agent-work/archive/<slug>.md`. They replace a cold
   exploration — you already know the prior design and decisions.
3. Append the new ask to `<feature-folder>/request.md` under a dated
   `## Extension <date>` heading. Do NOT clobber the original request.
4. Run a FOCUSED explorer over ONLY the code the addition touches (the codebase
   may have changed since the feature shipped) — not a full re-recon.
5. Treat every downstream artifact as a DELTA, not a rewrite:
   - **spec-writer** appends the new requirements, continuing FR-n numbering and
     marking them as part of the extension.
   - **architect / designer** run ONLY if the addition needs design changes;
     otherwise record "no architecture/design change" and skip them.
   - **archivist** UPDATES the archive with a new `## Extension <date>` section
     rather than overwriting the existing record.
6. Same agent rules as new mode (steps 3–4 above): pass the folder path and require
   PRINCIPLES.md. Same checkpoints and Test policy apply.

## Recall prior memory — BEST-EFFORT, after Setup and before stage 1
The subagents run in isolated contexts and cannot call Engram themselves, so YOU
(the orchestrator, in the main session where the Engram tools live) do the recall
and hand it to them through a file:
1. Call the Engram **`mem_search`** tool with keywords drawn from the request —
   feature nouns, subsystem/module/file names, domain terms. In extend mode, also
   search the `<slug>` and the prior feature's themes. Widen or re-query once if
   the first pass is too narrow.
2. Keep only genuinely relevant hits: prior decisions, conventions, gotchas, or
   bugs in the SAME area that bear on this change. Discard unrelated noise. Use
   `mem_get_observation` to pull full text for a hit that looks important but is
   truncated.
3. Write a short digest to `<feature-folder>/memory.md` — a bulleted list of
   "prior fact → why it matters here", each tagged with the memory's title/id.
   If nothing relevant surfaced, write exactly `No relevant prior memory.` so the
   agents know recall ran and came up empty.
4. This file is how recall reaches the agents: tell the **explorer**,
   **spec-writer**, and **architect** to READ `<feature-folder>/memory.md` as an
   input (they already list it — just confirm the path when you spawn them).
5. BEST-EFFORT: if the Engram tools aren't available (MCP not connected) or the
   search errors, write `Memory recall unavailable this run.` to `memory.md` and
   continue. Recall NEVER blocks the pipeline and is never treated as a checkpoint.

## Test policy — decide BEFORE the pipeline runs
TDD is the default. Determine whether to run the test stages (`test-author` +
test execution in `verifier`) or skip them for this run:
- **Skip tests** if EITHER:
  (a) the user passed `--no-tests` (or `skip-tests` / "no tests") in the request, OR
  (b) the change has no meaningfully testable behavior — pure config, copy/text,
      styling/CSS, docs, type-only edits, dependency bumps, or a pure rename/move
      with no behavior change.
- For case (b) you must **propose** skipping at Checkpoint 1 and get the user's
  confirmation. **Never skip silently** — TDD is the default, skipping is a
  deliberate, recorded choice.
- If there is ANY behavior or logic change, do NOT skip — write the tests.
- When tests are skipped, record `tests: skipped (<reason>)` in `spec.md`, in the
  verifier's report, and in the archive (and in any Engram memory the session
  saves). Do not imply test coverage that doesn't exist (honesty, PRINCIPLES §7).

## Review policy — pick the review TIER for step 8
The post-implementation review (step 8) runs at one of four tiers. Cost climbs
sharply with the tier, so default cheap and escalate only when it's warranted.

- **`none`** — no code review. Auto-selected only when the run is in no-tests mode
  for a non-logic change (config/copy/styling/docs/type-only/rename) — there's
  nothing to review for correctness. Note it in the archive.
- **`light`** (DEFAULT) — one `reviewer` agent: a single focused pass over the
  diff, no fan-out. Cheap. Right for ordinary feature work.
- **`standard`** — the `/code-review` skill at **medium** effort (multi-lens,
  some adversarial verification). For larger or trickier diffs.
- **`deep`** — the `/code-review` skill at **high/max** effort (broad coverage,
  a verifier per finding). Most expensive; for high-risk or sprawling changes.

Selection precedence:
1. An explicit `--review <tier>` in the request wins outright.
2. Otherwise AUTO-escalate to **`deep`** if the change touches sensitive areas
   (auth/authorization, secrets/config, money/payroll, PII, external
   integrations) OR the diff is large (rough rule: >~400 changed lines or >~8
   files). These are where a single light pass is most likely to miss something.
3. Otherwise use **`none`** for the no-logic no-tests carve-out above, else the
   **`light`** default.

State the chosen tier (and why, if auto-selected) when you reach step 8. The
security pass is decided separately by its own heuristic — see step 8.

> **Which `/code-review`?** The `standard`/`deep` tiers mean the built-in
> `/code-review` **skill** that reviews the working-tree diff and takes an effort
> level — NOT any PR-based `/code-review` plugin command (that one needs an open
> PR and is the wrong shape mid-pipeline).

## Stack policy: single PR vs. stacked PRs
A large ticket can ship as a **stack**: ordered branches in one repo, each off the
previous one, each becoming its own small PR. The pipeline decides this after
planning, never upfront.

- `--no-stack` → always a single PR. Skip slicing entirely.
- `--stack` → tell the task-planner `stack: forced`; it slices regardless of size.
- Otherwise (default) → the task-planner proposes a stack when its estimate
  exceeds ~400 lines or ~8 files (the same threshold as the `deep` review tier).
- A tiny request (see Orchestration rules) never stacks.

The user approves or rejects the stack at **Checkpoint 2**. That approval counts
as the user's explicit request (PRINCIPLES §6) for YOU, the orchestrator, to
**create local branches and make one local commit per slice**. It does NOT
authorize pushing or opening PRs. That stays with `/sdd:publish-stack`, which the
user runs afterwards. Say this plainly in the Checkpoint 2 prompt.

On approval, write `<feature-folder>/stack.md`:

```
# Stack: <feature-slug>
ticket: <ticket id + URL, or none>

## <repo name>  (path: <abs repo path>; base: <PR base branch>)
| # | branch | parent | tasks | status | PR |
|---|--------|--------|-------|--------|----|
| 1 | ABC-123-1-schema | main | T1–T3 | planned | |
| 2 | ABC-123-2-service | ABC-123-1-schema | T4–T6 | planned | |

## Merge order
<repo A> stack before <repo B> (only when the change spans repos)
```

- **Branch names:** if the work is tied to a ticket (e.g. `ABC-123`) →
  `<ticket-id>-<k>-<kebab-slice-name>` on EVERY slice, so tracker integrations
  that key on the ticket id link every branch. If the repo's `CLAUDE.md` defines
  a branch-naming rule, it wins. Without a ticket → follow the repo's `git log` convention
  with a `-<k>-` part index (e.g. `feature/<slug>-1-schema`).
- **Base:** the repo's PR base branch. Use the one the repo's `CLAUDE.md` /
  `CONTRIBUTING` names (e.g. `staging`). Otherwise use the default branch
  (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`). If unsure,
  ask at Checkpoint 2.
- **Status values:** `planned` → `committed` → `pushed` → `pr-open` → `merged`.
- Cross-repo work gets one table per repo plus a `## Merge order`. Each repo's
  slices stack only within that repo.

## Pipeline (each step = one Agent call, in order)
> `<feature-slug>` below = the slug you derived (new mode) or resolved (extend mode).
> In **extend mode**, skip any stage whose artifact doesn't need to change per
> "Setup (extend mode)" — e.g. skip architect/designer when the addition needs no
> design change. Always keep the spec, implementer, and verifier stages.

1. **explorer** → writes `exploration.md` (focused on the addition in extend mode).
2. **spec-writer** → writes `spec.md`.
   🛑 **CHECKPOINT 1:** Show the user the spec summary + any BLOCKING QUESTIONS.
   Wait for approval/answers before continuing. Loop spec-writer if revisions needed.
3. **task-planner** → writes `tasks.md`, including the `## Slices` section
   (pass `stack: forced` if `--stack`; skip slicing if `--no-stack`).
4. **architect** → writes `architecture.md`.
5. **designer** → writes `design.md`.
   🛑 **CHECKPOINT 2:** Show the user the architecture approach + interfaces.
   If a stack is proposed, also show the slice plan (slices, tasks, size, why
   each is mergeable alone, the architect's seam verdict) and ask: **single PR or
   stack of N?** State that approving a stack lets you create local branches and
   commits, and that nothing is pushed. Wait for approval before writing any code.
   On a stack approval, write `stack.md` (see Stack policy) and run steps 6–9
   in **stacked mode** (below).
6. **test-author** → writes failing tests + `tests.md` (TDD red).
   - **SKIP this step entirely if the Test policy says to skip tests** for this run.
7. **implementer** → writes code, updates `tasks.md` + `implementation.md`. In
   normal mode this is the TDD green step (make the tests pass); in no-tests mode
   it just applies the change per the design.
8. **Review** — run the tier chosen per the **Review policy** above on the
   implementer's diff:
   - **`none`** → skip; record that no review ran and why.
   - **`light`** → spawn the **`reviewer`** agent (writes `review.md`).
   - **`standard`** → run the built-in **`/code-review`** skill at **medium**
     effort on the diff.
   - **`deep`** → run **`/code-review`** at **high** (or **max** for very
     high-risk) effort.
   Then, INDEPENDENT of the tier, apply the **security heuristic**: if the change
   touches sensitive areas (auth/authorization, secrets/config, money/payroll,
   PII, external integrations, or anything security-relevant), ALSO run
   **`/security-review`**. Relay all findings (review + security) back to the
   **implementer** to address before verification, then re-review if the fixes
   are substantial.
9. **verifier** → writes `verification.md` with a PASS/FAIL verdict.
   - If **FAIL**: relay the issues back to **implementer**, then re-run
     **verifier**. Repeat up to 3 cycles; if still failing, stop and report to
     the user with the blockers.
   - **In no-tests mode:** the verifier does NOT run a test suite. It still runs
     lint/format, type-checks where relevant, manually checks the change against
     the spec's acceptance criteria, and states clearly that tests were skipped
     and why. Existing unrelated tests should still pass — run them if cheap.
   **Stacked mode — steps 6–9 run once per slice, in order.** Before slice 1,
   confirm the repo's working tree is clean (stop and ask if not) and that the
   base branch is up to date with origin. Then for slice k:
   a. `git checkout -b <slice-k branch>` off slice k-1's branch (slice 1 off the
      base branch). Update `stack.md`.
   b. Spawn **test-author**, **implementer**, the **review** tier, and
      **verifier**. Scope each one to slice k: pass the slice id and its task
      ids, and tell them to touch only those tasks. The review tier and the
      security heuristic are judged on **this slice's diff** (usually `light`).
      The verifier checks the FRs covered by slices 1..k and runs the full
      suite. Everything must be green with only slices 1..k applied. The same
      3-cycle FAIL loop applies per slice.
   c. On PASS, stage the slice's changes (never `.agent-work/`) and make ONE
      local commit with a single-line Conventional Commits subject (PRINCIPLES
      §6). Set the slice's status to `committed` in `stack.md`.
   d. Relay one status line (`slice k/N committed on <branch>`) and continue to
      k+1 without a checkpoint. If a slice fails after 3 cycles, stop: earlier
      slices stay committed and untouched, and you report the blocker.
   e. If a later slice needs a change in an earlier slice, do NOT rewrite
      history on your own. Surface it to the user, who decides between
      amending (with `git rebase --update-refs`) and putting the change in the
      current slice.
10. 🛑 **CHECKPOINT 3:** Offer to run the project's app-launch skill (e.g. **`/verify`** or **`/run`**, if one is available) to launch the app
    and observe the feature actually working (not just tests). Skip if the user
    declines or it's not applicable.
11. **archivist** → writes `<workspace-root>/.agent-work/archive/<feature-slug>.md`,
    then show the user the closeout summary.
    - In stacked mode, the archive records the slice list, branches, and the
      fact that PRs are opened via `/sdd:publish-stack`. Then tell the user: "run
      `/sdd:publish-stack <feature-slug>` from `<repo>` to push the stack and open
      the PRs."
    - No separate scripted Engram save — the session's always-active memory
      protocol captures decisions/discoveries on its own.
12. **Clean up scratch (only after a SUCCESSFUL closeout).** The archive is the
    durable record, so remove the process scratch from `<feature-folder>`:
    delete `request.md`, `memory.md`, `exploration.md`, `tasks.md`, `tests.md`,
    `implementation.md`, `review.md`, and `verification.md`. **KEEP** `spec.md`,
    `architecture.md`, `design.md`, `stack.md` (if any; `/sdd:publish-stack` needs
    it), and the
    `<workspace-root>/.agent-work/archive/<feature-slug>.md` record.
    - Delete those named files only — never `rm -rf` the folder, and never touch
      `<workspace-root>/.agent-work/archive/`.
    - If the run FAILED or was abandoned, skip cleanup entirely — leave all
      artifacts in place for debugging.
    - Tell the user which files were removed and which were kept.

## Orchestration rules
- Spawn ONE agent at a time in pipeline order (each depends on the prior's output).
- When you spawn an agent, pass: the feature-folder path, which artifact(s) to
  read, and what to produce. Keep your own commentary minimal — the agents have
  their own instructions.
- After each agent returns, relay a brief status line to the user, then proceed
  (or pause at a checkpoint).
- If an agent reports a blocker or contradiction, stop and surface it rather
  than pushing forward.
- Never skip the test-author before the implementer UNLESS the Test policy above
  says to skip tests for this run — in normal mode, tests come first (TDD).
- Stacking never changes the order of stages inside a slice. It only repeats
  steps 6–9 per slice. Don't run slices in parallel: each branches off the last.
- If the request is tiny (a one-line fix), tell the user the full pipeline is
  overkill and offer a shortened path — e.g. explorer→test-author→implementer→
  verifier, or in no-tests mode explorer→implementer→verifier.
