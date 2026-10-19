# Parallel work in worktrees

Back to [SKILL.md](../SKILL.md). One worktree per parallel writer; each ends with a pushed branch and an open PR, which is its receipt. Independent read-only jobs may share a checkout in separate tabs; a coupled change stays with one writer even across many files.

## Commands

```text
worktree list   [--workspace ID | --cwd PATH] [--trust-repository]
worktree create [--workspace ID | --cwd PATH] [--branch NAME] [--base REF] [--path PATH]
                [--label TEXT] [--focus|--no-focus] [--trust-repository]
worktree open   [--workspace ID | --cwd PATH] (--path PATH | --branch NAME) [--label TEXT]
                [--focus|--no-focus] [--trust-repository]
worktree remove --workspace ID [--force] [--trust-repository]
```

`--workspace` and `--cwd` exclude each other: given both, `worktree list` exited 2 with the usage as plain text, not JSON.

## What a worktree is

- A worktree is a workspace. `create` checks the branch out under the configured worktree directory (`~/.herdr/worktrees/<repo>/<branch>` by default, not beside the repo; `--path` puts it exactly there, creating missing parent folders) and returns `type: worktree_created` with `.result.workspace.workspace_id`, `.result.root_pane.pane_id` (already in the checkout) and `.result.worktree.path`. An existing local branch is checked out; otherwise the branch is created from `--base`, or `HEAD`.
- With `--workspace`, verify first that it is the repository's own workspace (`workspace get` → `worktree.repo_root`); a pane's cwd does not establish it. Given `--cwd` instead, `create` and `open` also open a workspace for the repo's main checkout, labelled with the repo name, when none is open; it is the run's to close.
- A repository the run created needed no `--trust-repository`; the harness started inside still asked its own trust question.
- A shell's `cd` does not move a pane: after `cd` into a linked checkout, a pane of the main workspace kept its `workspace_id`, and that workspace still named the main checkout; only the pane's `cwd` changed. Start a worktree's agent in that worktree's own root pane.
- `worktree list` (`worktree_list`) shows the main checkout and each linked one with its `open_workspace_id`.

## Lifetimes

- `worktree remove --workspace <ws>` (`worktree_removed`) closed the workspace, ended the agent working in it without asking, deleted the checkout and kept the branch. Run it only after the PR is confirmed on the machine and the waiters on that agent are stopped.
- Untracked or modified files refuse it: `dirty_worktree_requires_force`, exit 1. That refusal is the safety; `--force` is the user's (the guard denies it). Ignored files are not in `git status`; look at them too before deciding a checkout holds nothing.
- Closing the main workspace while worktree workspaces exist returns `workspace_group_close_required`. `--group` closes them all and their agents but leaves the checkouts on disk; it is on the guard's list. Remove worktrees first; close the main workspace last.
- Closing the last tab of a workspace also closes the workspace; a tab close that would remove a whole worktree group can return `confirmation_required`. Never confirm automatically.
- An orphaned checkout comes back with `worktree open --cwd <repo> --branch <branch>` (`worktree_opened`) and can then be removed properly. On a checkout that is already open, `open` returned that same workspace, pane and terminal with `already_open: true`, and its `--label` renamed the workspace.

## Per parallel task

1. `worktree create --workspace <repo ws> --branch <branch> --base <base> --label <role-subject> --no-focus` (one source selector, an explicit new branch, a verified base).
2. Start the agent in its root pane, read the screen, answer the trust question (a worktree the run created).
3. Brief that ends "commit, push the branch, open a PR, reply with the PR URL and the marker".
4. One background wait per agent (references/waiting.md).
5. Confirm on the machine: `gh pr view <url> --json state,headRefOid`, no dirty files, nothing unpushed (`git status --porcelain`, `git log @{u}..`).
6. The review loop (references/scenarios.md), then `worktree remove` once it passes.

Run this way, two harnesses each delivered a PR in parallel from two worktrees of one repo *(seen 0.9.3)*.

## Before briefing a PR

- Check that the machine can push: `gh auth status` there.
- An invalid `GH_TOKEN` in the environment shadowed a valid `gh` login (`env -u GH_TOKEN gh …`).
- A global `credential.https://github.com.username` naming another account broke `git push` even with a valid login; a repo-local `git config credential.https://github.com.username <login>` fixed it.

## Cleanup order

Stop waiters → confirm PRs and pushed branches → `worktree remove` each worktree (clean ones only) → close the tabs the run opened → close the run's main workspace last → snapshot to confirm nothing of the run is left and the user's focus is where it was. Branch deletion is a separate decision (`git branch -d` only, never `-D`).
