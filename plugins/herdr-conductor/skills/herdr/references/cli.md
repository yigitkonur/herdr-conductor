# herdr CLI facts

Back to [SKILL.md](../SKILL.md). For herdr 0.9.5 (18 command groups, 105 leaf commands in `herdr completion zsh`). Seen in runs unless marked [help] (read from `--help` or the docs only). Case numbers (T1 …) point to the case table in the plugin's repository.

## Help

- `herdr <group> <sub> --help` prints that command's usage (exit 0) and runs nothing; `workspace create --help` created no workspace. The bare group prints its command list. Option descriptions are short; flag names and value sets are what it gives.
- `herdr completion zsh` holds the whole tree with every flag, without running anything. `herdr --skill` prints the skill bundled with herdr (it assumes a caller inside a pane).
- Not probed with `--help`, because the top-level usage routes them itself: `update`, `server` (bare, `stop`, `reload-*`, `*-agent-manifests`), `config reset-keys`, `channel set`, every `attach`/`observe`/`control`, `machine reconnect`, `plugin install`, `session stop`/`delete`.

## Subcommands

- workspace: list, create (`--cwd`, `--label`, `--env`, `--focus`/`--no-focus`), get, focus, rename, report-metadata, close (`--group` exists although `--help` omits it)
- tab: list (`--workspace`), create (`--workspace`, `--cwd`, `--label`, `--env`, `--no-focus`), get, focus, rename, close `<tab_id>`
- pane: list (`--workspace`), current, get, layout, process-info (`--pane <id>` or `--current`; a positional ID is an unknown option), neighbor, edges, focus, resize, zoom, read, rename, input, split, swap, move, close, send-text, send-keys, wait-output, run; `report-*` and `release-agent` are for agent integrations, not for a conductor
- agent: list, get, read, explain, prompt, wait, send-keys, start, rename (`--clear`), focus (moves the user's view), attach (interactive: never from a tool)
- worktree: list, create, open, remove (references/worktrees.md)
- api: snapshot, schema (`--json`, `--output <path>`); machine: list, status, reconnect (needs the user), add, rename, remove, enable, disable
- read-only: `status client --json` (this client: version, channel, protocol, capabilities, binary, session), `status server --json` (also over `--machine`: version, protocol, `compatible`, session), `integration status` (exit 2 over `--machine`), `session list --json`, `config check`, `channel show`, `plugin list --json` (forwarded; `--plugin <id>` returns one)
- [help] `notification show <title> [--body TEXT] [--position top-left|top-right|bottom-left|bottom-right] [--sound none|done|request]`: a toast on the user's Herdr
- named sessions (`--session <name>`) give an isolated server for risky experiments; never combine with `--machine` or `--remote`

## Limits and defaults

- `agent start --kind`: claude, codex, agy and 21 others; `herdr agent start --help` lists them.
- `agent start --timeout`: default 30000 ms, more than 3000 and at most 300000.
- `agent prompt`: an agent already `blocked` gets `agent_blocked` before any input is sent. With `--wait`, a submission from a non-working state that reaches neither `working` nor `blocked` within 5000 ms gets `agent_prompt_stalled`; a caller `--timeout` that runs out first gives `timeout`; turns are not tracked. Seen: `/stop` sent to a codex whose turn had just ended came back `agent_prompt_stalled` and ran anyway; `--timeout 0` was never typed; `--timeout 1000` timed out in 1.7 s and was answered (T3). At codex's trust dialog (`blocked`) the prompt got `agent_blocked` in 0.8 s, screen byte-identical (T13); at agy's, which reads `idle`, its Enter answered the dialog, the text was lost, and `agent_prompt_stalled` came after 12.7 s (T15).
- `agent wait --until idle|working|blocked|done|unknown`, repeatable (`--until done --until blocked`); without `--until` it matches `idle`, `done` or `blocked`. It returns at once (exit 0) only when the current state matches its set: on a `done` codex, no `--until` and `--until done --until blocked` returned in under a second, while `--until blocked` and `--until idle` timed out with exit 1 `timeout` (T2). `--timeout 0` checks once (T3). On a `blocked` codex the default set returned in 1.0 s, `--until idle` timed out (T13). Without `--timeout` it waits forever.
- `agent start` promises "detected and ready for input": codex and agy returned `idle` with a trust dialog on screen, claude `agent_not_ready`; agy's reply said `interactive_ready: true` over its dialog; a codex `idle` start read `blocked` (rule `trust_directory`) at the next `agent get` (T12, T15).
- On macOS, `pane run` and `agent start` refuse a command longer than the terminal's line limit while the shell is still starting, before queuing it [help]. Wait for the prompt; keep agent arguments short.
- `agent read`/`pane read --lines N` counts back from the bottom; recent sources default to the last 80 rows, `visible` and `detection` to the whole snapshot [help]. While codex works, more lines than its screen holds fail with `agent_not_idle`; `--source visible` still reads.
- Read sources: `visible`, `recent`, `recent-unwrapped`, `detection` (four; `pane wait-output` has no `detection`). `pane read --format ansi`, `--ansi` and `--raw` gave byte-identical output: colours re-rendered by Herdr and CRLF line ends; `--format text` is the default; `agent read --format ansi` pads rows to the pane width (T14).
- `pane wait-output --raw` changed nothing seen: no pattern holding an ESC matched; plain text matched with or without it (T14).
- `pane split --ratio 0.3`: the pane being split keeps 0.3; the new pane gets the rest; the ratio shows only in the snapshot's `layouts`. `--right-click pane` changed nothing visible in any reply (T17).

## Replies

- `workspace create` → `.result.workspace.workspace_id`, `.result.tab.tab_id`, `.result.root_pane.pane_id`
- `workspace get` → the workspace with its `worktree` (`checkout_path`, `is_linked_worktree`, `repo_key`, `repo_name`, `repo_root`)
- `tab create` → `.result.tab.tab_id`, `.result.root_pane.pane_id`; `pane split` → `.result.pane.pane_id`
- `pane get` → the pane with `workspace_id`, `cwd` and `foreground_cwd`; a `cd` run in the pane changed both cwds and not `workspace_id` (T11)
- `pane move` → `.result.move_result.pane.pane_id` (the new ID) and `.result.move_result.previous_pane_id` [help]
- `agent start` → `type: agent_started`, `.result.argv` (what was typed) and `.result.agent` with `interactive_ready`
- `agent prompt` → `type: agent_prompted`; with `--wait` also `.result.agent.agent_status`, plus `completion_seq` when it settled `done`. A 2 s turn still came back `done`, not `agent_prompt_stalled`.
- `agent wait`, `agent get` → `type: agent_info`, `.result.agent`. Agent fields: `agent`, `agent_session` (`agent`, `kind`, `source`, `value`: the harness's own session or conversation id), `agent_status`, `completion_seq`, `state_change_seq`, `cwd`, `foreground_cwd`, `focused`, `pane_id`, `tab_id`, `workspace_id`, `terminal_id`, `terminal_title`, `terminal_title_stripped`, `revision`, `tokens`, and `name` when set.
- `pane send-text` → no stdout, exit 0; non-ASCII text arrived intact. `send-keys` → `ok` only.
- `pane run` → no stdout, exit 0, and nothing about the command's own exit status: end the command with `; echo MARK_<nonce>_$?` with a new nonce each run (T6).
- `pane wait-output <pane> (--regex <re> | --match <text>) --timeout <ms>` → `type: output_matched`, `matched_line` and a `read` of the pane. It searches what is already there before polling: a stale `MARK_0` matched in 0.66 s while the next command slept, and `--match` on a word in the command matched the typed command line (T6). The typed line never matched a digits pattern, since it shows `$?`.
- `pane process-info --pane <id>` → `shell_pid`, `foreground_processes[{argv, cwd, name, pid}]`; a harness's background children do not appear.
- `worktree create`/`open` → `worktree_created`/`worktree_opened` with `workspace`, `tab`, `root_pane`, `worktree{branch, path, open_workspace_id, …}`; `open` on a checkout already open adds `already_open: true` (T7). `worktree remove` → `worktree_removed` (`forced`, `path`, `workspace_id`); `worktree list` → `worktree_list` with `source` and `worktrees[]`.
- `workspace close`, `tab close`, `pane close` → `{"result":{"type":"ok"}}`. CLI closes are immediate; the TUI's close confirmation does not apply, except that closing a tab that would remove a whole worktree group can return `confirmation_required` [help].
- `api snapshot` → `.result.snapshot` with `workspaces`, `tabs`, `panes`, `agents`, `layouts`, `version`, `protocol` and `focused_workspace_id`, `focused_tab_id`, `focused_pane_id` (T10).
- `agent explain --json` → a bare object, no envelope (references/states.md).
- Unset fields are omitted, not null.

## Errors

Exit 1 with `{"error":{"code":…,"message":…}}` on stderr (stdout is empty, so read with `2>&1`). Seen or documented, with what to do:

| code | meaning | do |
| --- | --- | --- |
| `timeout` | the wait or start ran out | one screen read; delivery may have happened; re-wait |
| `agent_not_found` | no agent there, a closed agent's name, a name cleared with `--clear` | re-resolve from a snapshot; after a close it confirms cleanup |
| `agent_not_running` | a wait was in progress when its pane moved | re-resolve by name |
| `agent_blocked` | prompt refused, nothing sent | read the dialog |
| `agent_not_ready` | start returned at a dialog (claude's trust dialog) | read and answer it; the name stays usable |
| `agent_prompt_stalled` | no `working` or `blocked` within 5 s | `agent get` and a read; may or may not have been delivered |
| `agent_not_idle` | `--lines` larger than a working codex's screen | read `--source visible` |
| `invalid_key` | one key name in the list is unknown | nothing was sent; fix the list |
| `workspace_group_close_required` | closing a main workspace with worktree workspaces open | remove worktrees first; never add `--group` to get past it |
| `dirty_worktree_requires_force` | `worktree remove` on untracked or modified files | preserve and report; `--force` is the user's |
| `confirmation_required` | a tab close would remove a worktree group [help] | never auto-confirm; ask |
| `workspace_not_found` | an ID that does not exist [help] | re-resolve |

Syntax errors exit 2 and print plain usage, not JSON: `worktree list` given both `--workspace` and `--cwd` (T8). Over `--machine`, a bare `status`, `agent explain --file` and `integration status` exit 2 as well ("not an API-backed machine command", T1, T16, T18).

## Keys (`agent send-keys`, `pane send-keys`)

Accepted, in any case: single characters, `enter`, `esc` (canonical; `escape` also accepted), `tab`, `shift+tab`, `space`, `backspace`, `up`, `down`, `left`, `right`, `ctrl+<x>`, `alt+<x>`, `f1`–`f12`. Rejected: `home`, `end`, `pageup`, `pagedown`, `delete`, `insert`, and the dash form `ctrl-a`. One bad name rejects the whole list before any byte is written.
