# Autonomy: what the run decides, what it asks

Back to [SKILL.md](../SKILL.md). The user hands over outcomes, not steps; their attention is the scarce resource. Decide what git can undo, note it in the ledger, and bring the user only what git cannot undo or evidence cannot settle.

## Levels

The level is `autonomy:` in CONDUCTOR.md, else `default_autonomy` in the user config, else L2. Levels govern only what the run decides alone: an explicit request from the user authorizes that action within its scope, at any level.

**Trust rule** (the one place it is defined): answer a trust dialog yourself for folders and worktrees the run created and for the repository the user started the run in or vouched for; any other folder goes to the user. The same rule governs `--trust-repository`.

| level | the run may, without asking |
| --- | --- |
| L0 | read and report only: no prompts, keys or closes |
| L1 | answer what the brief, the plan, the project docs or a Standing answer settles; reversible choices; restart a crashed agent once |
| L2 | everything inside the goal and its done-checks except the always-ask list: choose between sound approaches, retry, reshape the plan, answer agents' questions, answer trust dialogs under the trust rule, switch harness on quota per the routing, open PRs. Work beyond the goal needs an entry in "Allowed follow-up work" |
| L3 | L2 plus the actions listed under "Pre-authorized actions" in CONDUCTOR.md (for example: merge a PR whose review passed and whose checks are green; deploy to staging) |

**Always ask, at every level**: logins and 2FA, credentials and secrets, payments and spending, anything on the guard's list, deleting what the run did not create, product or taste decisions only the user can own, and every entry in "Escalate always". A pre-authorization never covers credentials, logins, payments or the guard's list.

## The lists in CONDUCTOR.md

- **Standing answers**: questions the user has settled, one per line with its answer. A question that matches is answered from it at L1 and above, and the reply names the entry.
- **Escalate always**: matters that go to the user at every level.
- **Allowed follow-up work**: work the run may start beyond the original goal at L2 and L3.
- **Pre-authorized actions**: irreversible actions L3 may take, each with its condition.

## Safety table

| action | enforced by | who may allow |
| --- | --- | --- |
| `herdr server …`, `herdr update`, `config reset-keys`, `channel set` | guard hook | the user (`! <cmd>` or `guard_allow`) |
| `machine add/remove/enable/disable/reconnect` | guard hook | the user |
| `session stop/delete/attach`, `agent attach`, `terminal attach/session`, bare `herdr`, `--remote` | guard hook (they hang or end sessions) | the user |
| `worktree remove --force`, `workspace close --group` | guard hook | the user |
| `pkill`/`killall` of herdr | guard hook | the user |
| approval-bypass arguments for agents (`--dangerously-*`, `--yolo`, `bypassPermissions`, `danger-full-access`) | guard hook | the user (`guard_allow`) |
| any of the above typed into a pane (`pane run`, `pane send-text`) | guard hook | the user |
| `--trust-repository` | the model | the trust rule |
| closing a workspace, tab, pane or session | the model | the run's own; others only when the user asked |
| merging or pushing to a default branch, deploying | the model | the user, or L3 with a matching pre-authorization |
| stopping a process or waiter | the model | the run's own, by ID; never by name pattern |

## Asking the user

- Investigate first: the ledger, the card, receipts on the machine (git status, commits, PRs), a read-only subagent for repository facts. Ask only what the evidence leaves open and what would change the brief: scope, architecture, rework, what "done" means.
- Use AskUserQuestion: one decision per question, two to four concrete options, the recommendation first and marked, each option saying what it leads to. Ask in dependency order; a question whose options hang on an unanswered one waits for it. Up to four independent questions fit one call.
- Input only the user can write (an idea, a text to paste) is asked plainly, and the turn stops for it.
- Not while agents work and other steps remain (references/waiting.md, questions while agents work). Headless or inside the `herdr-worker` subagent there is no one to ask: write the question under "Waiting on the user", finish the independent work, and report.
- With `notify: herdr`, a pending decision also raises a toast on the user's Herdr.

## Decision table

| situation | L0 | L1 | L2 and L3 |
| --- | --- | --- | --- |
| a turn finished | report | verify the receipts (files, git, PR, exit codes), then the next step if the plan says so | same |
| an agent asks (dialog or prose) | report | answer from the brief, plan, docs or a Standing answer; else ask | answer unless it is on the always-ask list or changes scope |
| trust dialog | report | answer under the trust rule | same; elsewhere ask |
| permission dialog | report | answer when inside the brief | same; never pick a "switch to auto/bypass" option |
| quota (agy and others) | report | report with the reset time; a one-shot cron to resume | resume in place, rotate with a configured `rotate_command`, or switch harness per routing (references/harness-agy.md) |
| login or auth failure | report | ask | ask (the user logs in) |
| crash or unexpected exit | report | restart once with the same scope | same; a second crash goes to the user |
| review FAIL | report | author fixes, reviewer again | up to `review_rounds`, then ask |
| no progress | read: a long build or test is not stuck | report | interrupt through the harness's task control, one follow-up; two equivalent failures end automatic retries |
| dirty worktree on removal | report | keep it, report | keep it, report; `--force` is the user's |
| `confirmation_required` | report | ask | ask; never confirm automatically |

Two equivalent failures (the same error, the same refusal, the same infrastructure fault) end automatic recovery at any level; a new session for the same attempt does not reset the count.

The guard reads the command line only: a command assembled inside a program (`python3 -c …`) is not seen, and a literal `$(…)` inside single quotes is denied although the shell would not run it. It is a fence against accidents, not a sandbox.
