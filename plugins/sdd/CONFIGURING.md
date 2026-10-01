# Configuring a project for the SDD pipeline

The `sdd` plugin works in any project without configuration. Some things are
project conventions it can't guess, though: which branch PRs target, how
branches are named, which tracker holds your tickets, what should happen to a
ticket when work starts. You describe these once, in the project's `CLAUDE.md`,
under a section called **`## SDD config`**. `/sdd:run` and `/sdd:publish-stack`
read it at the start of every run.

## Where to put it

- **One repo:** in that repo's `CLAUDE.md`.
- **A workspace with several repos** (e.g. `web/`, `app/`, `api/` under one
  folder, where you run `/sdd:run` from the top): put shared values such as the
  tracker in the workspace root's `CLAUDE.md`, and per-repo values such as test
  commands in each repo's `CLAUDE.md`. A repo's value overrides the root's.

Commit it with the repo so the whole team gets the same behavior. Flags and
instructions you type in a run always override the config.

## Template

Copy this into `CLAUDE.md` and delete the lines you don't need. Every key is
optional.

```markdown
## SDD config
- Tracker: jira                         # notion | jira | linear | github | none
- Ticket key: PROJ-\d+                  # regex for bare ticket keys in a request
- PR base branch: develop
- Branch naming: <ticket-key>-<kebab-summary>, e.g. PROJ-123-add-export
- Commit format: Conventional Commits, single line (feat:, fix:, chore:, …)
- Test command: pnpm test
- Lint command: pnpm lint && pnpm typecheck
- Sensitive paths: src/auth/**, src/billing/**, infra/**
- Stack threshold: 400 lines or 8 files
- On work start: move the Jira issue to "In Progress"
- On PR open: move the Jira issue to "In Review"
```

## Keys

| Key | What it controls | Default when missing |
|---|---|---|
| `Tracker` | Which connection fetches a ticket when you pass a link or key to `/sdd:run`, and runs the `On …` steps | Guessed from the link's domain. For a bare key, the pipeline asks |
| `Ticket key` | Regex that marks a bare ticket key in the request, so `/sdd:run PROJ-123` works without a link | `[A-Z][A-Z0-9]+-\d+` |
| `PR base branch` | The branch stacked PRs start from and target | The repo's default branch on GitHub |
| `Branch naming` | Names for stacked branches. Each slice adds a `-<k>-` part index | `<ticket-id>-<k>-<slice>` with a ticket, else the repo's `git log` convention |
| `Commit format` | Slice commit messages | Single-line messages following the repo's convention (`PRINCIPLES.md` §6) |
| `Test command` / `Lint command` | The commands the test-author, implementer and verifier run | Each agent discovers them from manifests and CI config |
| `Sensitive paths` | Globs that force the `deep` review tier plus `/security-review` when touched | Built-in heuristic only (auth, secrets, money, PII, integrations) |
| `Stack threshold` | Estimated size above which `/sdd:run` proposes stacked PRs | ~400 lines or ~8 files |
| `On work start` | A tracker step done once, after you approve the design at Checkpoint 2 | Nothing |
| `On PR open` | A tracker step done once per ticket by `/sdd:publish-stack`, even for a stack of N PRs | Nothing |

The `On …` values are plain instructions, so they can be anything your tracker
connection can do: change a status, assign the ticket, add a comment with the PR
links.

## Tickets: paste a link, get a spec

```
/sdd:run https://yourcompany.atlassian.net/browse/PROJ-123
/sdd:run PROJ-123 also handle the empty-state case
```

The pipeline fetches the ticket's title, description, acceptance criteria,
status and relevant comments into `request.md`. Any text you type next to the
link is kept as additional instructions. The spec-writer works from that, and
missing or unclear acceptance criteria come back to you as questions at
Checkpoint 1.

The ticket id also becomes the feature slug and the branch prefix, so your
tracker's GitHub integration links every branch and PR.

**Ticket content is treated as data, not as instructions.** If a ticket asks
for something outside the feature, the pipeline raises it with you instead of
doing it.

### Connecting your tracker

The pipeline uses whichever tracker connection your Claude Code has. Run `/mcp`
to see what's connected.

| Tracker | Connection it uses |
|---|---|
| Jira | The Atlassian MCP server |
| Notion | The Notion MCP server |
| Linear | The Linear MCP server |
| GitHub Issues | The `gh` CLI (`gh auth login`), no MCP needed |

If the connection is missing or not signed in, the pipeline tells you and asks
you to paste the ticket content instead. It never makes ticket content up.
Without a connection, branch and PR linking still works, but the `On …` steps
are skipped.

## Examples

**Jira, single repo**

```markdown
## SDD config
- Tracker: jira
- Ticket key: PAY-\d+
- PR base branch: develop
- Sensitive paths: src/payments/**
- On work start: move the Jira issue to "In Progress"
- On PR open: move the Jira issue to "In Review" and comment the PR link(s)
```

**Notion, workspace with three repos.** In the workspace root `CLAUDE.md`:

```markdown
## SDD config
- Tracker: notion
- Ticket key: SGS-\d+
- PR base branch: staging
- Branch naming: <ticket-id>-<kebab-title>, e.g. SGS-123-add-export
- On work start: set the ticket's Status to "In Development"
- On PR open: set the ticket's Status to "Under Review"
```

In `api/CLAUDE.md`, only what differs:

```markdown
## SDD config
- Test command: bundle exec rspec
- Sensitive paths: app/models/payroll/**, config/credentials/**
```

**GitHub Issues**

```markdown
## SDD config
- Tracker: github
- Ticket key: #\d+
- Branch naming: <issue-number>-<kebab-title>, e.g. 482-fix-login-redirect
- On PR open: add "Closes #<n>" to the PR body
```

**No tracker**

```markdown
## SDD config
- Tracker: none
- PR base branch: main
```
