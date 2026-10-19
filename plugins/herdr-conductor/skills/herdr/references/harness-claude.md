# claude (Claude Code) under herdr

Back to [SKILL.md](../SKILL.md) · dialogs: [dialogs.md](dialogs.md).

## Starting

- `herdr agent start <name> --kind claude --pane <pane> --timeout 30000 -- <args>`. Arguments that matter: `--model <alias or full name>`, `--effort low|medium|high|xhigh|max`, `--permission-mode acceptEdits|auto|bypassPermissions|manual|dontAsk|plan`, `--settings '<json>'`. Model and effort come from the user's routing (config.md, CONDUCTOR.md) or the request; this plugin sets none.
- Never `claude -p` or `--print`: there is no interactive agent to wait on.
- claude brings its own settings: on one machine `permissions.defaultMode` was `bypassPermissions` and `tui` was `fullscreen` with no flag typed, so it ran without approval dialogs and kept no scrollback. Read the status line after start; put scope into the brief.
- First run in a folder: `agent_not_ready` at the trust dialog, `down enter` (dialogs.md).
- A worker claude may have this very plugin installed. Its brief says it is a worker under a conductor: it does the work itself, ignores the herdr-conductor skill and must not start or control herdr agents unless the brief asks for it (references/briefs.md).

## How its screen behaves

- Answers are `⏺ text` lines, so a marker line reads `⏺ MARKER`; your prompt comes back as `❯ …`.
- Herdr reads its state from the prompt box (`live_prompt_box` idle; `live_blocked_form` and `interactive_question_blocked` blocked). A trivial turn took 2 s and still came back `done` from `prompt --wait`.
- It leaves its transcript in scrollback unless its TUI is fullscreen; fullscreen, `recent` gave only the 20 visible rows. The whole turn is then in `~/.claude/projects/<cwd with / as ->/<session>.jsonl` on that machine (`agent get` → `.agent_session.value` is the session id).
- Claude's background work (Workflows, background agents, teammates) can outlive the turn that started it. Started with `--settings '{"ultracode":true}'`, claude labelled its input box "ultracode"; a small task ran as a Workflow, claude printed the marker once as the workflow started and ended that turn, then woke on the workflow's notification and printed the answer and the marker again 28 s later; a wait `--until done --until blocked` started before the first marker returned only after the second *(seen 0.9.3)*. So the run is over at the last marker with no "Waiting for N dynamic workflow" line on screen. Newer rule sets read such waits as `working` (`dynamic_workflow_prompt`, `background_agents_working`, `waiting_for_teammates_working`); check `agent explain` on that machine.

## Slash commands that manage claude itself

`/plugin marketplace add <owner/repo>` runs straight away, with no menu, and reloads plugins by itself. `/plugin install <name>@<marketplace>` opens a scope menu ("Install for you (user scope)" is the highlighted first row; footer "Enter to select · Esc to go back"); `enter` takes user scope and prints "Installed … Plugin is now active." *(claude 2.1.303)*. They start no model turn, so send them without `--wait`. Herdr read both screens `done`, with a new `completion_seq` for each command, never `blocked`: the footer is the only sign of the menu. Restart claude after installing so hooks and the session-start line load: `agent prompt <name> "/exit"` without `--wait`, wait until `agent get` says `agent_not_found` (the pane is a shell again), `clear`, `agent start` again and read the screen.

## Questions and grilling

- Asked for its question tool, claude shows AskUserQuestion dialogs, each `blocked` (keys in dialogs.md).
- Asked to "grill me on this before you plan", a claude with a grilling skill loaded it by itself, asked six questions in prose, each with its recommendation, and ended the turn: `prompt --wait` came back `done` after 20 s, not `blocked` *(seen 0.9.3)*. Read the questions (from the transcript when it is fullscreen) and answer them in one ordinary prompt, from the ledger, CONDUCTOR.md and the facts; relay only true decisions to the user, claude's recommendation first.

## Interrupting and stopping

- Not mapped for running commands. After a cancelled approval it waits at "Interrupted · What should Claude do instead?" (dialogs.md).
- Resume a claude that exited: note `.agent_session.value` first, confirm the process is gone and the pane is a shell, then start it again with the harness's own resume option (`claude --help` on that machine names it) and restore the scope in the first prompt.
