# Security policy

## What counts as a security issue here

This plugin is Markdown: skills and agent prompts that Claude Code runs with
the permissions of the person using it. A security issue is anything that could
make the pipeline act against its user, for example:

- instructions in a skill or agent that run commands, push code, or change
  settings without the checkpoints the pipeline promises;
- ticket or repository content being able to steer the agents (prompt
  injection) past those checkpoints;
- anything that leaks secrets or local files into commits, PRs, tickets or
  external services.

## Reporting

Please report privately through GitHub: **Security → Report a vulnerability**
on this repository. Don't open a public issue for security problems.

You can expect a first reply within a week. Fixes ship as a new plugin version
and are noted in `CHANGELOG.md`.

## Supported versions

Only the latest released version (the newest `sdd--v*` tag) gets fixes.
