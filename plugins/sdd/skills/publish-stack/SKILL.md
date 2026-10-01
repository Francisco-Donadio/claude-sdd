---
name: publish-stack
description: Push a stacked-PR plan built by /sdd:run and open its PRs bottom-up, each based on the previous slice's branch.
argument-hint: "[feature-slug]"
allowed-tools: Bash(git:*), Bash(gh:*)
disable-model-invocation: true
---

Publish a stack that `/sdd:run` already built as local branches and commits. Run
it from inside the repo the stack belongs to. Read the `## SDD config` section
of the repo's `CLAUDE.md` (and the workspace root's) for `PR base branch` and
`On PR open`. See the plugin's `CONFIGURING.md`.

User input (optional): $ARGUMENTS

## Steps

1. **Find the plan.** Locate `.agent-work/<slug>/stack.md` by walking up from the
   repo root (`git rev-parse --show-toplevel`) to the workspace root. Use the slug
   from `$ARGUMENTS`. If there's no slug, use the only `stack.md` that has
   slices not yet `pr-open`, and ask if several match. Use the table for THIS repo
   (match by repo name/path). If this repo has no table, stop and say which repos
   do. If `## Merge order` puts another repo's stack first, remind the user of it
   but don't block.
2. **Sanity check.** For each slice in order: the branch exists, its status is
   `committed` (or later), and its parent is an ancestor
   (`git merge-base --is-ancestor <parent> <branch>`). The working tree must be
   clean. If a check fails, stop and report it. Don't try to repair the stack.
3. **Confirm once.** Show the list (`k. <branch> → base <parent>: <commit
   subject>`) and ask for a go-ahead. Pushing and opening N PRs is outward-facing.
4. **Publish, bottom-up.** For each slice not yet `pr-open`:
   - `git push -u origin <branch>` → set status `pushed` in `stack.md`.
   - If a PR for the branch already exists (`gh pr view <branch>`), record its URL
     and move on. Don't create a duplicate.
   - Otherwise `gh pr create --base <parent> --head <branch>`. Title = the slice's
     commit subject. Body = a concise summary of the slice's diff
     (`git diff <parent>...<branch>`), a line `Stack: part k of N`, and the
     ticket URL from `stack.md` if there is one. Follow the repo's PR conventions
     (`CLAUDE.md`, PR template) if it has any.
     → set status `pr-open` and record the PR URL.
5. **Cross-link.** Once all PRs exist, `gh pr edit` each body to add a
   `### Stack` list of every PR in order, marking the current one (`👉`). Replace
   an existing `### Stack` section rather than appending a second one.
6. **Ticket status.** If the config defines `On PR open` (e.g. move the ticket
   to "In review"), do it **once** for the stack, not once per PR. If the
   tracker connection isn't available, say so and skip it.
7. **Report.** Print the ordered PR URLs and remind the user to merge
   **bottom-up**. After a slice is squash-merged, the next branch still carries
   the merged commits. Fix it with
   `git fetch && git rebase --onto origin/<base> <old slice-k branch tip> <slice-k+1 branch>`,
   then `git push --force-with-lease`, and set the PR's base to `<base>` if GitHub
   didn't retarget it. Update `stack.md` statuses to `merged` as slices land.
