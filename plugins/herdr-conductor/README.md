# herdr-conductor

A Claude Code plugin for driving [herdr](https://herdr.dev) (workspaces, tabs, panes, worktrees and the coding agents in them) from a Claude Code session. Claude Code becomes the conductor: it starts claude, codex, agy or any other harness herdr supports in herdr panes, hands each one a small brief, waits for it in the background, answers or escalates its dialogs, checks the result on the machine, and has the work reviewed by an agent that did not write it. It runs from inside a herdr pane or from any terminal outside herdr, locally or on saved SSH machines (`herdr --machine`).

The knowledge in it comes from many live runs against herdr: how agent states really behave (`idle`, `done`, `blocked`, `working`, `unknown`, `completion_seq`), what `agent wait` and `agent prompt --wait` actually match, trust and question dialogs per harness, quota that hides behind any status, worktree lifetimes, and the traps that make an agent get lost.

## Requirements

- herdr 0.9.5 or newer on every machine it drives (`herdr --version`, `herdr status server --json`).
- Claude Code with plugin support (tested with 2.1.302). `python3` for the hooks and `herdr-snapshot`.
- The harness CLIs you want to run (claude, codex, agy, …) installed and logged in on their machines.

## Install

```text
/plugin marketplace add yigitkonur/herdr-conductor
/plugin install herdr-conductor@herdr-conductor
```

For development, load a checkout directly: `claude --plugin-dir ./plugins/herdr-conductor`.

Then run `/herdr-conductor:setup` once: it checks herdr, the server, integrations, saved machines and harnesses (read-only), and writes the optional config.

## What is in it

| component | what it does |
| --- | --- |
| skill `herdr` | The entry point, loaded when a request involves herdr. Stance, traps, a scenario router, the core mechanics, and references loaded on demand (states, waiting, CLI, dialogs, one file per harness, briefs, ledger, autonomy, scenarios, worktrees, machines). |
| `/herdr-conductor:conduct <goal>` | Runs a goal end to end as a task or a project. |
| `/herdr-conductor:watch [local\|<machine>\|all] [--every <min>]` | A compact table of every agent with flags for blocked, quota, finished; optional recurring sweep. |
| `/herdr-conductor:setup [doctor\|config\|project]` | Doctor, user config, project card. |
| agent `herdr-worker` | A subagent that runs one task through one herdr agent and returns a fixed report with receipts. It never asks the user; a decision it cannot take comes back as `needs_decision`. |
| hook PreToolUse(Bash) | The guard: denies herdr commands that stop or replace the server, change machines or sessions, open interactive clients, force-remove worktrees, close worktree groups, kill herdr, or pass approval-bypass flags to agents. Quoted brief text and heredocs are data and pass. |
| hook SessionStart | One context line, only inside a herdr pane or in a project with a session directory: herdr versions, which pane is this session, the session directory, and after a resume or compaction the open run's waiters to re-arm. |
| `bin/herdr-snapshot` | On the Bash PATH while the plugin is enabled: `herdr api snapshot` as one row per agent with workspace and tab labels, status and `completion_seq`. |

## Scenarios

The skill routes a request; nobody has to pick a mode.

| scenario | when | what happens |
| --- | --- | --- |
| quick | one herdr action or one short turn | direct; no ledger, no questions |
| task | one agent produces something to check | a run ledger, one agent (or `herdr-worker`), verification on the machine |
| project | a plan file, several agents or waves | upfront questions (design-tree rounds through AskUserQuestion), CONDUCTOR.md, plan → waves → one step per brief, review loop, autonomy |
| watch | what is running where | snapshot tables and flags |
| review | judge a PR, commit or diff | a reviewer that is not the author, another harness when available |

## Waiting

`herdr agent wait` runs as a Claude Code background task, one per agent. When it ends, the session wakes with a task notification, reads the agent's screen and continues, so a turn can end while agents work. Short turns use `agent prompt --wait` in the foreground. Team runs whose leader reads `idle` while workers run (agy, grok) are awaited on a marker with `pane wait-output`. `/loop` and one-shot cron jobs are fallbacks; polling is never used.

## Configuration (optional)

User config `~/.config/herdr-conductor/config.md` (template in `assets/templates/config.md`):

| key | default | meaning |
| --- | --- | --- |
| `projects_root` | none | where project session directories are created; unset keeps them in the repo as `.herdr-conductor/` (git-excluded) |
| `default_autonomy` | `L2` | L0 report · L1 answer from docs · L2 autonomous within the goal · L3 plus pre-authorized actions |
| `routing` | empty | role → harness and arguments (`plan`, `exec`, `review`, `research`); empty means the harness named in the request, or one question |
| `machines` | empty | per saved machine: `remote_drop` (folder for briefs and reports), `rotate_command` (account rotation, if the machine has one) |
| `guard_allow` | empty | command prefixes the guard lets through; only the user edits this |
| `notify` | `none` | `herdr`: a toast on the user's Herdr when a decision is needed |
| `research` | `subagents` | `herdr-only`: even fact finding goes to herdr agents |
| `review_rounds` | `3` | review → fix rounds before the user decides |

Project card `CONDUCTOR.md` in the session directory (template in `assets/templates/CONDUCTOR.md`): repositories, checks that prove work, what "done" means, off-limits, autonomy, and the lists `Pre-authorized actions`, `Allowed follow-up work`, `Escalate always`, `Standing answers`.

Session directory resolution: adopt an existing project (a CONDUCTOR.md listing this repository, the pointer file `~/.local/state/herdr-conductor/projects.tsv`, or a match under `projects_root`); otherwise create one under `projects_root` or in the repository; ask when ambiguous.

## herdr 0.9.4 and 0.9.5 changes reflected

- agy and grok read `idle` at their prompt while background tasks or subagents still run: a settled wait is not the end of a team run.
- herdr no longer installs Codex turn hooks (0.9.5); codex status comes from screen detection. Run `herdr integration install codex` after upgrading.
- `done` is idle and not yet seen: reads never mark it seen, an explicit focus does; `completion_seq` records finished turns.
- New error codes handled: `confirmation_required`, `workspace_not_found`, `agent_not_running`.
- On macOS, `pane run` and `agent start` refuse commands too long for a shell that is still starting.
- Detection rules update live; local overrides in `~/.config/herdr/agent-detection/` win.

## Deliberately not included

An MCP server around herdr (the CLI's JSON is enough), workflow scripts, monitors, channels, cross-session messaging, an output style, and a Stop-hook turn guard (background waits make it unnecessary). Agent model choices are never hardcoded: they come from your routing or the request.

## License

MIT. Author: Yigit Konur.
