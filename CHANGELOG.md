# Changelog

All notable changes to the `sdd` plugin. Versions follow semver and are tagged
`sdd--v<version>`.

## 1.1.1 (2026-10-01)

- Eval suite in `plugins/sdd/evals/` (3 cases): an unreachable ticket link must
  not produce invented content; a typo fix gets the shortened path; a pasted
  ticket with an injected instruction must stop at Checkpoint 1, use the
  project's `## SDD config`, never run the injected command, and flag it.
- `license: MIT` in `plugin.json`.
- Repo: GitHub Releases are created from this changelog on each `sdd--v*` tag;
  commits and tags are signed.

## 1.1.0 (2026-10-01)

- **Ticket intake:** `/sdd:run <ticket link or key>` fetches the ticket from
  Jira, Notion, Linear or GitHub Issues, using whichever connection is
  available, and writes it to `request.md`. Ticket content is treated as data,
  and missing acceptance criteria become Checkpoint 1 questions.
- **Project config:** an `## SDD config` section in `CLAUDE.md` sets tracker,
  ticket key, PR base branch, branch naming, commit format, test/lint commands,
  sensitive paths, stack threshold, and `On work start` / `On PR open` tracker
  steps. Resolved per run into `config.md`.
- New `CONFIGURING.md` with the template, key reference and examples.

## 1.0.0 (2026-10-01)

First plugin release, packaged from the copied `~/.claude` setup.

- `/sdd:run`: the SDD → TDD orchestrator (formerly the `/sdd` command), with
  extend mode, test policy, tiered review, Engram recall and stacked PRs
  (`--stack` / `--no-stack`).
- `/sdd:publish-stack`: pushes a stack and opens its PRs bottom-up.
- Ten agents, namespaced as `sdd:<name>`.
- Shared rules at `${CLAUDE_PLUGIN_ROOT}/PRINCIPLES.md`.
- Team-specific defaults (base branch, ticket naming, tracker updates) moved out
  of the pipeline into each repo's `CLAUDE.md`.
