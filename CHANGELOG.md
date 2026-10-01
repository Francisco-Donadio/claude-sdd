# Changelog

All notable changes to the `sdd` plugin. Versions follow semver and are tagged
`sdd--v<version>`.

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
