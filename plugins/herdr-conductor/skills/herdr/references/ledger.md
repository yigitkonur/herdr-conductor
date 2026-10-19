# Session directory, configuration and the ledger

Back to [SKILL.md](../SKILL.md). Quick work needs none of this. A task or project run keeps its state in files, because attention fades over a long session and compaction drops detail.

## Two layers of configuration

- **User config** `~/.config/herdr-conductor/config.md`: YAML frontmatter plus free notes. Optional; every key has a default. Template: `${CLAUDE_PLUGIN_ROOT}/assets/templates/config.md` (`/herdr-conductor:setup` writes it).
- **Project card** `CONDUCTOR.md` in the session directory: what this project is and how much the run may decide alone. Template: `${CLAUDE_PLUGIN_ROOT}/assets/templates/CONDUCTOR.md`.

| key | layer | default | meaning |
| --- | --- | --- | --- |
| `projects_root` | user | none | where new session directories are created (one folder per project) |
| `default_autonomy` | user | `L2` | level used when a project card sets none (references/autonomy.md) |
| `routing` | user, project | empty | role → harness and agent arguments, e.g. `review: codex -- -s read-only`; the project's wins |
| `machines` | user | empty | per saved machine: `remote_drop` (folder for briefs and reports), `rotate_command` (account rotation, if any) |
| `guard_allow` | user only | empty | exact command prefixes the guard hook lets through, e.g. `herdr --session hc-test server stop` |
| `notify` | user, project | `none` | `herdr`: toast on the user's Herdr when a decision is needed |
| `research` | user, project | `subagents` | `herdr-only`: even fact finding goes to herdr agents |
| `review_rounds` | user, project | `3` | review → fix rounds before the user is asked |

## Finding the session directory

1. **Repository key**: the normalized remote URL (`git remote get-url origin`, scheme and `.git` removed, e.g. `github.com/owner/repo`); else the git common dir (`git rev-parse --path-format=absolute --git-common-dir`, shared by every worktree of the repo); else the directory itself when it is not a repo.
2. **Adopt** an existing project, in this order: a `CONDUCTOR.md` in the working directory or a parent, walking up no further than the repository root (or `projects_root`, or the home directory), whose `repos:` lists the key; then the pointer file `~/.local/state/herdr-conductor/projects.tsv` (two tab-separated columns: repository key, session directory); then, under `projects_root`, a folder whose `CONDUCTOR.md` lists the key. A working directory already inside `projects_root/<project>/` is that project.
3. **Create** one when nothing matched: `<projects_root>/<slug>/` when `projects_root` is set (slug from the repo name), else `<repo root>/.herdr-conductor/`, added to the repository's exclude file (`git rev-parse --git-path info/exclude`; in a linked worktree `.git` is a file) so it never dirties `git status` or rides along in `git add -A`. Write a CONDUCTOR.md (at least `repos:` with the key and `autonomy:`) for task runs too, since it is what the SessionStart hook and later sessions find, and a line into `projects.tsv` when the directory is outside the repository.
4. **Never create** at `~`, `/` or `projects_root` itself. Several candidates, or no repository and no card: ask with AskUserQuestion (candidates as options, recommendation first). Headless (no one to ask): use `~/.local/state/herdr-conductor/<key-hash>/` and say so in the report.
5. A project whose repository exists only on a saved machine still has its session directory here; `repos:` records the machine and path, and briefs travel by the drop folder (references/briefs.md).

## Layout of a session directory

```text
CONDUCTOR.md                          # the project card (template)
runs/<YYYYMMDD-HHMM>-<slug>/
  ledger.md                           # the run's memory
  briefs/<step>.md                    # long briefs (copied to the agent's machine when remote)
  reports/<step>.md                   # long handbacks
  research/<topic>.md                 # research notes, conclusions first, sources as URLs
```

## The ledger

Read the ledger before acting and update it whenever a state changes: write the intent before a command and the observed state after it. At the start of a turn read the ledger before the snapshot: the ledger says what you expect, the snapshot what is there, and a difference is news.

```markdown
# Goal: fix the login timeout in app (local)
scenario: project · autonomy: L2 · status: open · started: 2026-10-19 21:40 · session: <session dir>
owner_session: <session id from the herdr-conductor SessionStart line>

## Targets
local w6A:t2 w6A:p3  name fix-api  kind codex  cwd /src/app  branch fix/login

## Steps
| # | step | state | expect | ran | saw |
| 1 | plan → briefs/plan.md | verified | plan file, 6 steps | `test -s …/plan.md` | 212 lines |
| 2 | step 1 sent, marker LGN1-q7 | submitted | PR URL + marker | `agent prompt fix-api … --until working` | working |

## Waiters
local fix-api w6A:p3 task b8x2 started 21:52 marker LGN1-q7 last completion_seq 4

## Decided without asking
- vitest over jest: already in the repo

## Waiting on the user
- codex asks to run migrations (blocked; options y / n)

## Receipts
- PR #12 open, head 3f2c1a9 (gh pr view 12 --json state,headRefOid)
```

- **Step states**: `submitted` (the CLI accepted the prompt), `consumed` (the screen shows the agent working on it), `completed` (the agent's turn ended with the marker), `verified` (the machine shows the result). A step short of `completed` gets `agent get`, a visible read and a marker or `completion_seq` check before anything is sent again; never resend after `timeout` or `agent_prompt_stalled`.
- **Waiters** are keyed by agent name (pane IDs change when a pane moves). Each line: server, name, pane, background task id, started, marker, last `completion_seq`.
- When the Task tools are available, a short task list may mirror the steps for the user's view; the ledger stays the truth.
- `owner_session` lets the SessionStart hook tell this session's run from another session's after a resume or compaction. Leave it empty when the session id is unknown; the hook then treats the run as unowned.
- `status: closed` and the end time go in when the final report is written.

## Recovery after compaction, resume or a restart

After a herdr server restart or a reboot, the workspaces and panes come back but the agents do not: their panes read `unknown` with no agent, `agent get` says `agent_not_found`, and every Waiter is dead. A reboot also empties `/tmp`, so keep session directories, briefs and reports elsewhere (the defaults do). Treat each ledger Target as gone until `agent get` or the screen proves otherwise, and restart agents from the ledger's briefs and the work already on the machine (git state, files) instead of resending prompts.

The SessionStart hook prints the session directory and, after `resume` or `compact`, the open run's Waiters. Background waiters do not survive a resume: read the ledger, then for each Waiter `agent get <name>`, compare `completion_seq`, read the screen, and re-arm. A run that another session opened (the hook says "foreign") is adopted only after checking that no live session still drives it (its agents' states, the ledger's last write time), and the adoption is written into its ledger.
