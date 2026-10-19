---
name: herdr
description: This skill should be used when the user mentions herdr, or asks to inspect, start, prompt, wait on, read, answer, review or clean up coding agents (claude, codex, agy and others) in herdr workspaces, tabs, panes or worktrees, locally or on a saved machine; for example "what is running in herdr", "start a codex in herdr and have it fix X", "have another harness review this PR", "run these in parallel worktrees", "conduct/orchestrate/supervise agents", "autopilot this project with herdr agents". It works from inside a herdr pane or from outside herdr. It is not for ordinary Claude Code subagent work that never mentions herdr.
---

# herdr conductor

Drive herdr (workspaces, tabs, panes, worktrees and the coding agents in them) from this Claude Code session. The installed binary is the authority for syntax: `herdr <group> <sub> --help` prints that command's usage and runs nothing, and `herdr completion zsh` holds the whole tree. Facts here were seen on herdr 0.9.5 unless tagged *(seen 0.9.3)*.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. References live in `${CLAUDE_PLUGIN_ROOT}/skills/herdr/references/`; read one when the work reaches it (table below).

Reading this skill does not by itself authorize launching agents or touching existing sessions; a task from the user does, within its scope.

## Stance

- **Conduct; do not build.** Agents write, run, test and review; the conductor decides what is asked of whom and in what order, and keeps the ledger. Detail pulled into this session crowds out the plan, so stay at the level of briefs, states and receipts. Facts (a file exists, a version, how a module is laid out) may come from read-only subagents; building, testing, reviewing and long research go to herdr agents (`research: herdr-only` in CONDUCTOR.md makes even facts go there).
- **Small briefs, one turn each.** A brief should be finishable in one turn and checkable afterwards. Before anything large, ask only for a plan written to a file; read it, then hand it out one step at a time. A large task handed over whole is lost whole, even by agents that run teams of their own.
- **The author does not verify its own work.** Cheap checks (exit codes, git state, the PR exists) run on the machine; reviews and tests go to another agent.
- **The agent's report is a claim; the machine is the witness.** Check files, git, PRs and URLs on the machine, not by asking the agent again.
- **The ledger is memory.** Attention fades over a long session and compaction drops detail; task and project runs keep their plan, targets and waiters in a ledger file (references/ledger.md).
- **Decide what git can undo; bring the user what it cannot.** Facts are yours to find, decisions are the user's; the autonomy level says which decisions are already delegated (references/autonomy.md).
- **Decide with evidence, brief with conclusions.** Give executing agents the conclusions and a few sources, not the search.

## Traps (hold these before the first command)

- Agents run interactive via `agent start` only. Never `codex exec`, standalone `codex review`, `claude -p`, `agy -p` or any print mode, `nohup`, or an agent launched with `pane run`, not even after a quota hit or a broken TUI: Herdr then has no interactive agent to wait on or read.
- **One command, one reply, one decision.** Run herdr commands one at a time and let each reply choose the next. Shaping one reply with a short `python3 -c` filter is reading, not chaining. No scripts that drive agents unattended: a chain that runs unattended also fails unattended.
- **Trust the reply you already have.** Mutating commands return what they made (`workspace create` gives the workspace, its tab and `root_pane`; `agent prompt --wait` gives the agent with its settled `agent_status`). Query again only when the command failed.
- **Herdr tracks states, not turns.** A wait matches a state, the current one included, not your message. Codex folds a prompt sent mid-turn into that turn, so one completion can answer two prompts; only a marker word you chose tells whose answer it is.
- **A read is a screen, not a document.** Reads return the terminal after the agent's UI rendered it: code blocks or JSON may not survive, a marker word will, and so will your own prompt (codex rewrapped it and the marker landed alone on a prompt line). Match the answer's line (`• MARKER` in codex), not "any line with the marker".
- Never open an interactive client from this session: bare `herdr`, `herdr --remote …`, `session attach`, `agent attach`, `terminal attach`, `machine reconnect`. They hang the tool.
- `--machine <label>` goes on **every** command meant for that machine, discovery included. IDs and agent names are scoped to one server.
- Never probe a mutating subcommand by omitting its arguments: `workspace create` runs with defaults. Use `--help`.
- `--no-focus` on every workspace, tab, pane and worktree you create; never `agent focus` or `workspace focus` unless asked. The user's Herdr TUI is live and this session is a second client.
- Keep `agent start` arguments short: on macOS a command longer than a starting shell accepts is refused before it is queued.
- Name the server in every record and report: `local w2H:pAG`, `<machine> wT:p1Z`.

## Where you are

- **Inside a herdr pane** (`HERDR_ENV=1` and `herdr pane current --current` resolves): that pane is this session. Never prompt it, send keys to it or close it. `--current` may target it for splits (`pane split --current … --no-focus`). Other panes in its workspace belong to the user or to other sessions.
- **Outside herdr** (`HERDR_ENV` unset): there is no caller pane. Never use `--current`, `$HERDR_PANE_ID`, `$HERDR_TAB_ID`, `$HERDR_WORKSPACE_ID` or `herdr pane current`; give every command an explicit ID or a unique live agent name. An omitted target can fall back to the UI-focused pane, which belongs to the user.
- Either way: closing a workspace that holds the user's focus moves their view to another one.

## Choose the scenario

| Signal in the request | Scenario | What happens |
| --- | --- | --- |
| One herdr action or one short agent turn with nothing to verify afterwards: what is running, read a pane, answer a dialog, ask an agent a question, run a command in a pane | **quick** | Act directly. No ledger, no questions beyond a decision the user owns. |
| One agent produces something to check: a fix, a file, a review of one diff | **task** | A run ledger, one agent (directly or through the `herdr-worker` subagent), verify on the machine, report. |
| Needs a plan file, more than one agent, or more than one wave | **project** | Upfront questions, CONDUCTOR.md, plan brief, waves, review loop, autonomy (references/scenarios.md). |
| States across servers, standing supervision | **watch** | Snapshot table and flags; optional periodic sweep (`/herdr-conductor:watch`). |
| Judge a frozen candidate (PR, diff, commit) | **review** | A reviewer that is not its author; verdict as a receipt (references/scenarios.md). |

Ties go to the smaller scenario; a task that grows promotes itself to a project (write CONDUCTOR.md then). When the request fits two scenarios with materially different work, ask with AskUserQuestion about the scenario only; the autonomy level comes from CONDUCTOR.md or the user config, and is asked only at the start of a project.

## Read before you act

| When | Read |
| --- | --- |
| Before the first `agent start` of a harness in this session | references/dialogs.md and references/harness-claude.md, harness-codex.md or harness-agy.md |
| Before a wait longer than a few minutes, several agents at once, or ending a turn while agents work | references/waiting.md |
| A state looks wrong, or before treating `idle`/`done` as finished | references/states.md |
| Command syntax, a reply field, an error code, keys, limits | references/cli.md |
| A brief longer than a few lines, or a brief for another machine | references/briefs.md |
| Task or project: where the ledger and CONDUCTOR.md live | references/ledger.md |
| Whether to decide or ask; dialogs, quota, retries, review failures | references/autonomy.md |
| Project, watch or review flow; upfront questions | references/scenarios.md |
| Parallel writers, PRs, cleanup of worktrees | references/worktrees.md |
| Anything on a saved machine | references/machines.md |

## Discover (read-only, safe at any time)

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py" [--machine m]   # one row per agent: server, workspace/tab labels, name, status, completion_seq, cwd
herdr [--machine m] api snapshot             # whole tree, server version and protocol, the user's focus
herdr [--machine m] agent get <target>
herdr [--machine m] agent read <target> --source visible --lines 60
herdr [--machine m] agent explain <target>   # rule and evidence behind a status
herdr [--machine m] status server --json     # server version and protocol
```

- **One snapshot is the map.** `api snapshot` returns every workspace, tab, pane and agent with labels, `version`, `protocol` and the user's focus (`focused_workspace_id`, `focused_tab_id`, `focused_pane_id`) in one call; on a busy machine eleven `tab list` calls took 7 s and the snapshot under one *(seen 0.9.3)*. `workspace list`, `tab list --workspace`, `pane list --workspace` and `agent list` are narrower views of the same tree.
- Agents carry no tab label, so "the api agent" is a join: an agent's `workspace_id` and `tab_id` lead to the labels that name it. Several matches: narrow by `cwd` and last output before asking. A codex title is the thread name from its first prompt and does not follow later work; trust labels and names over titles.
- **Status belongs to panes; an agent is a presence.** An empty shell reports `unknown`; whether an agent is there is the `agent` field.
- Agent commands take a unique live agent name or the pane ID hosting the agent, not terminal IDs or kind labels. Names match `[a-z][a-z0-9_-]{0,31}`, follow the current occupant, and are cleared when it exits or is replaced or by `agent rename <target> --clear` (the old name then gives `agent_not_found`; the pane ID still works). A pane moved to another workspace gets a new ID. Re-resolve targets by name at the start of each turn instead of trusting IDs from history or the ledger.
- "What is running" means this machine and every relevant saved machine (`herdr machine list --json`).

## Agent states in one screen

- `idle`: ready. `done`: ready, with a finished turn nobody has viewed. Reads, explains and waits never mark it seen; an explicit focus does, and each TUI client tracks its own badge. Neither proves success: a codex given a model that does not exist printed a 400 error and settled `done`, exit 0.
- `working`: busy. agy and grok read `idle` at their prompt while background tasks or subagents still run, so a settled wait proves nothing there.
- `blocked`: Herdr recognized an approval or question dialog. A dialog it does not recognize reads `idle` or `done` (agy's trust dialog reads `idle`); only the screen tells them apart.
- `unknown`: no classification; an empty shell reports it too. Never completion.
- `completion_seq` is Herdr's record that a turn ended. It grows by more than one per turn, so compare with greater-than. It is absent while the agent works and before its first finished turn, it is kept when `done` turns `idle`, and an `idle` reached straight from `working` (an agy team run's end) has none, so its absence does not say the work is unfinished. A value above the ledger's says Herdr saw a turn end; whether the work ended is the screen's to say.
- **The status is Herdr's guess; the screen is the fact.** Every settle is followed by a read. A footer naming keys ("Enter to select", "enter Submit") is a dialog whatever the status says; a question in prose is a finished turn, answered with an ordinary prompt.
- `agent explain <target>` names the detection rule and evidence; `--json` adds every rule evaluated and the rule set's source and version. A machine's local overrides in `~/.config/herdr/agent-detection/` win over the bundled and remote rules, so one harness can read differently per machine (references/states.md).

## Send work and read results

```bash
herdr [--machine m] agent prompt <target> "$(cat <<'EOF'
...brief...
EOF
)" --wait --timeout 300000          # Bash tool timeout at least 330000
```

- Pass the brief through a quoted heredoc as above, so nothing is expanded locally.
- `--wait` waits for the first settled `idle`, `done` or `blocked` after the turn starts and returns the agent; branch on `.result.agent.agent_status`. Do not add `--until` for that default.
- `agent_blocked`: nothing was sent (the screen stayed byte-identical); the agent is at a recognized dialog.
- `agent_prompt_stalled`, `timeout` or a connection error: the prompt **may or may not** have been delivered. With `--timeout 0` nothing was typed; with `--timeout 1000` it timed out and the agent answered anyway *(seen 0.9.3)*. Run `agent get` and a visible read before anything else; collect the result with `agent wait`. Never resubmit blindly.
- If the agent is already `working`, the wait is satisfied by the current turn ending, and codex steers your text into that turn. Send to a working agent only when steering is wanted; otherwise wait first.
- Without `--wait`, `agent prompt` returns at once (`agent_prompted`): the bytes were written, nothing more. `--wait --until working --timeout 30000` confirms delivery in about a second.
- Slash commands that start no turn (`/stop`, `/tasks`) go without `--wait`; with it, `/stop` came back `agent_prompt_stalled` and still ran.
- Work answered in a few minutes fits `prompt --wait --timeout`; long or parallel work takes a delivery check and a background wait (references/waiting.md).
- Read results with `agent read <target> --source recent-unwrapped --lines N`; `--lines` counts back from the bottom. While codex works, more lines than its screen holds fail with `agent_not_idle`; `--source visible` still reads. Ask the agent to end its answer with a marker word new for this run and extract after the last one, once the wait returned: agy once printed it mid-turn, before its edits. An answer longer than a screen goes to a Markdown file in the run folder on the agent's machine, and the reply is only the path.

## Blocked agents and dialogs

1. Read the dialog: `agent read <target> --source visible --lines 60` shows the question, the command, the agent's reason and the options with their keys; `agent explain` names the rule that saw it.
2. Decide by the autonomy level (references/autonomy.md). Answer it yourself when the answer is reversible and inside the brief: trusting a folder the run created, edits and commands in the agent's own repo, a question the brief or plan already settles; note the answer in the ledger. Otherwise ask the user: server, pane, the question and options as written, what each causes, your recommendation first.
3. **A dialog speaks its own keys.** Send what the footer offers: `agent send-keys <target> <key> [key ...]`. Accepted, in any case: single characters, `enter`, `esc`, `tab`, `shift+tab`, `space`, `backspace`, `up`, `down`, `left`, `right`, `ctrl+<x>`, `alt+<x>`, `f1`–`f12`. `home`, `end`, `pageup`, `pagedown`, `delete`, `insert` and the dash form `ctrl-a` are rejected, and one bad name rejects the whole list (`invalid_key`) before any byte is written. A free-text field takes `pane send-text <pane_id> '<text>'`, which types without Enter.
4. `send-keys` returns only `ok`. Read the screen and confirm the choice was taken before the next wait: a wait matches the current state, so one started while the dialog is still up returns that `blocked` at once. One dialog may hold several questions and is still one `blocked`; the next dialog is the next `blocked`, so start a fresh wait after each answer. Declining in codex cancels the whole turn, which still ends `done`.

Per-harness dialogs and keys: references/dialogs.md.

## Layout and starting agents

```bash
herdr [--machine m] workspace create --cwd <path> --label <label> --no-focus
#   -> .result.workspace.workspace_id, .result.tab.tab_id, .result.root_pane.pane_id
herdr [--machine m] tab create --workspace <ws> --cwd <path> --label <label> --no-focus
#   -> .result.tab.tab_id, .result.root_pane.pane_id
herdr [--machine m] pane split <pane_id> --direction right --cwd <path> --no-focus
#   -> .result.pane.pane_id
herdr [--machine m] agent start <name> --kind <kind> --pane <pane_id> --timeout 30000 [-- <agent-args>]
```

- **One tab per agent; close before you open.** Label the tab and name its agent alike, `<role>-<subject>`, unique on the server (`rev-api-pr31`; roles such as `plan`, `exec`, `rev`, `fix`, `res`). A tab on the ledger is yours; nothing else is. Before each `tab create` and when the work ends, stop the waiters of your finished tabs whose context the next step will not reuse, then close them.
- Where to put agents: a quick or task agent gets a tab in the conductor's workspace when this session runs inside herdr, otherwise a run workspace (`hc-<slug>`). A project gets its own workspace, and every parallel writer its own worktree (references/worktrees.md). Never reshape the user's own workspaces.
- Remote paths must be absolute, `~` or start with `~/`.
- **Starting an agent is typing; ready is what the screen shows.** `agent start` types `<kind> <agent-args>` at the shell prompt and nothing checks the arguments: a rejected flag leaves its error in the shell while `agent start` waits out its timeout (read it with `pane read`). It needs a shell pane at its prompt with nothing in the foreground; `clear` a reused pane first (a dialog footer left in scrollback kept a fresh claude reading `blocked`). Keep `--timeout` near 30000; harnesses start in 3–5 s, and a launch that dies surfaces only as `timeout`.
- Herdr quotes each argument after `--` itself: `--settings '{"ultracode":true}'` reaches claude whole, while quotes added around it made claude look for a file of that name.
- A start that returns is not a ready agent. In new folders claude stopped at its trust dialog with `agent_not_ready`, while codex and agy returned `idle`, even `interactive_ready: true`, with a dialog on screen; agy's came about 3 s late, reads `idle` for good, and a prompt sent into it was taken as the dialog's Enter and lost. Read the screen after every start (again a few seconds later for agy) and answer what it shows. Every harness meets a new folder with a trust dialog, `/tmp` subfolders included.
- Ordinary commands: `pane run <pane_id> '<cmd>; echo MARK_<nonce>_$?'` with a nonce new for each run (single quotes, so `$?` reaches the pane), then `pane wait-output <pane_id> --regex 'MARK_<nonce>_[0-9]+' --timeout <ms>`. The marker carries the exit code (`pane run` reports nothing). `pane wait-output` searches existing output first: a reused marker matched the previous run, and `--match` matched the typed command. `pane send-text` and `pane send-keys` drive panes that have no agent.
- A harness swap or account rotation reuses the pane: end the old agent until `agent get` says `agent_not_found`, `clear`, then `agent start` there.

## Principles learned by running it

- **`done` is unread news that does not keep.** It survived every read for minutes, then turned `idle` when a client looked at its workspace; an `idle` therefore hides whether a turn ended since you last looked, and `completion_seq` is Herdr's record of it (references/states.md).
- **A wait is a process, not a promise.** Killing a wait (TaskStop, a tool timeout) ends only the waiting; the agent works on. Closing an agent's workspace left its `agent wait` hanging, so whoever closes an agent first stops its waiters. Several waiters, from this session and others, can watch one agent at once.
- **Lifetimes nest.** Closing a workspace ends its panes and their agents; `agent_not_found` afterwards confirms the cleanup. Waiters sit outside that nest.
- **History lives in the agent's UI, not in Herdr.** `recent` holds only what the agent left in scrollback. Codex redraws one screen, and a fullscreen claude leaves only its visible rows; read that claude's transcript on its machine (`~/.claude/projects/<cwd with / as ->/<session>.jsonl`) or ask the agent for a file.
- **The brief is the only fence you bring.** An agent may run without any approval dialog (bypass modes inherited from its own settings), so scope and limits travel inside the prompt (references/briefs.md).
- **Stopping a turn is not stopping its work.** `esc` ended codex's turn while the command it had started ran on in the background. Stop work through the harness's own task control (codex `/stop`, agy `/tasks` then `k`), then confirm on the machine (`pgrep -f`) that the process is gone; the status will not tell.
- **agy's quota hides behind any status.** After each agy wait, read its screen for `quota reached` before trusting `idle`, `done` or `blocked` (references/harness-agy.md).
- **A surprise is a test case.** When a reply contradicts this skill, write command, reply, exit code and versions into the ledger, reproduce it in a workspace you created, and report it so the case table (tests/CASES.md in the plugin's repository) can take it.

## Ending a turn

A background wait wakes this session when it ends, so a turn may end while agents work, but only when every working agent on the ledger has a live waiter task, or a `/loop` or cron covers it. Otherwise arm one before ending, or say plainly in the reply which agent is unwatched (references/waiting.md). The final report comes when every ledger agent is done and verified, its waiters are stopped and its tab is closed or deliberately kept.

## Safety

- The plugin's guard hook denies the never-list: `herdr server stop` and the other `server` commands, `herdr update`, `config reset-keys`, `channel set`, `machine add|remove|enable|disable|reconnect`, `session stop|delete|attach`, `agent attach`, bare `herdr`, `--remote`, `worktree remove --force`, `workspace close --group`, `pkill`/`killall` of herdr, and approval-bypass flags in agent arguments. When the user asks for one, they run it themselves with `! <command>`, or allow it in their config (references/autonomy.md).
- Do not close workspaces, tabs, panes or sessions the run did not create unless the user explicitly asked. Never add `--group` just to get past `workspace_group_close_required`.
- Stop only your own waiter tasks, by task ID; other sessions run waits on the same agents.
- Use `--trust-repository` only for repositories the run created or the user vouched for.
- Client and server versions can differ: check `herdr status client --json` and `herdr [--machine m] status server --json` before relying on newer features. A missing method is not permission to upgrade a server.
- A connection failure does not prove a mutation was not applied. Inspect the state before retrying.

## Reporting

- Report once, when the work ends; every state in it comes from command output in this run.
- Name the server and pane or agent for each item.
- Report separately what was submitted, consumed, completed and verified.
- If something failed, give the command and its error code, and say which step remains unverified.
- Name the assumptions and the decisions taken without asking (the ledger holds them).
