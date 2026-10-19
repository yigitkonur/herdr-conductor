# Live cases

The plugin is a set of claims about a CLI and about agents that change under it. This file keeps the claims honest: what was run, what came back, where each finding is stated, and what to run again when something changes. `python3 -I tools/lint.py` fails when a case has no Trace line or a Trace phrase is gone from the plugin file it names.

Machines: **local** is a macOS workstation, **remote** a Linux server saved as a herdr machine (`--machine`). T-cases were run on herdr 0.9.3 (protocol 22) with codex-cli 0.160, claude 2.1.28x and agy 1.2.15–1.2.16; N-cases on herdr 0.9.5 with this plugin.

## Cases

| case | claim under test | result |
| --- | --- | --- |
| T1 | `status` over `--machine` | bare `status` exit 2 "not an API-backed machine command"; `status server --json` exit 0 with version, protocol, `compatible` (remote) |
| T2 | a wait on a settled agent returns at once | only when the current state is in the `--until` set: on a `done` codex, no `--until` 0.83 s and `--until done --until blocked` 0.85 s exit 0; `--until blocked` and `--until idle` timed out (remote) |
| T3 | delivery after `timeout` | `agent wait --timeout 0` checks once; `agent prompt --wait --timeout 0` typed nothing; `--timeout 1000` timed out in 1.72 s and was answered (`completion_seq` 278 → 281) (remote) |
| T4 | read sources | four: `visible`, `recent`, `recent-unwrapped`, `detection`; `detection` byte-identical to `visible` on codex; `wait-output` has no `detection` |
| T5 | `agent rename --clear` | name dropped; old name `agent_not_found`; pane ID still works |
| T6 | `pane run` markers | a reused `MARK_0` matched the previous run in 0.66 s; a per-run nonce waited for the new command; `--match` hit the typed command line |
| T7 | `worktree open` on an open checkout | same workspace, pane and terminal, `already_open: true`, `--label` renamed it |
| T8 | `--workspace` with `--cwd` | exit 2, usage as plain text |
| T9 | `idle`/`done` do not prove success | codex with a model that does not exist: start exit 0, prompt exit 0 `done`, 400 error on screen |
| T10 | snapshot contents | `protocol`, `layouts`, `focused_workspace_id`, `focused_tab_id`, `focused_pane_id`; `agent_session` on most agents |
| T11 | `cd` into a worktree | only the pane's `cwd` changes; `workspace_id` and the workspace's checkout stay |
| T12 | `agent start` returning `idle` means ready | no: `idle` and `interactive_ready: true` with codex's trust dialog up; the next `agent get` read `blocked` (`trust_directory`). On 0.9.5 (codex 0.163) `agent start` itself returned `agent_not_ready` there, and after `enter` codex read `done` with a new `completion_seq` before any prompt |
| T13 | waits and prompts on a `blocked` agent | default wait exit 0 in 1.03 s; `--until idle` timed out; prompt `agent_blocked` in 0.82 s, screen byte-identical |
| T14 | read formats | `--format ansi`, `--ansi`, `--raw` byte-identical (colours re-rendered, CRLF); `wait-output --raw` matched no ESC pattern |
| T15 | agy's trust dialog | no rule (`default_known_agent_idle_fallback`); `--until blocked` timed out; a prompt into it exited `agent_prompt_stalled` after 12.7 s, answered the dialog and lost its text |
| T16 | `agent explain` flags | `--format json` equals `--json`; `--verbose` 37 lines; `--file` classifies offline in 0.08 s; exit 2 over `--machine` |
| T17 | `pane split --ratio` | the split pane keeps the ratio; shown only in `layouts`; `--right-click` changed nothing visible |
| T18 | `integration status` | exit 2 over `--machine`; over ssh exit 0 |
| T19 | claude's grilling and fullscreen | trust `agent_not_ready` in 5.0 s, `down enter`; grilling asked six questions in prose and settled `done`, not `blocked`; fullscreen `recent` gave the 20 visible rows |
| T20 | agy `/teamwork-preview` | `blocked` at "Question 1/1", then a team of five for ~22 min; meanwhile `idle` once and `done` three times with new `completion_seq`; ended `idle` with none |
| T21 | `done` stays until seen | `done` survived `agent get`, 15 s, every read source, `pane read`, `pane get`; later turned `idle` keeping `completion_seq` |
| T22 | agy resumes on its conversation | three `ctrl+c` quit and printed `agy --conversation=<id>`; restarted with it, an 8-step task cut at step 2 finished steps 2–8, none repeated (local) |
| T23 | claude in ultracode | the marker came twice (workflow start, answer); a wait started before the first returned after the second; quotes around `--settings` JSON broke it; a stale dialog footer in a reused pane read `blocked` until `clear` (local) |
| T24 | agy reviews a PR from a mission file | one `gh pr comment` per round as allowed, report where told; round 1 found two major and two minor faults lint had passed (local) |
| N1 | a background `agent wait` wakes the Claude Code session after its turn ended | PASS (0.9.5, claude 2.1.302): a background `agent wait` on a working codex ended at 23:11:52 and the idle session was woken by the task notification; the output file held the settled JSON (`done`, `completion_seq` 344) and `HC_WAIT_EXIT=0`; the marker was on screen. Not run: a question open while a wait ends (UNVERIFIED) |
| N2 | the guard denies the never-list and passes briefs that mention it | PASS: 45 synthetic commands at first, now 58 in `tests/guard_check.py` (denies incl. `pane run`/`send-text` text, `ssh`, `sh -c`, `$(…)`, `env`, `timeout`, absolute path, `danger-full-access`; passes incl. heredoc briefs and `grep` that mention the words; per-command `guard_allow`); live: a fresh session was denied `herdr --session … server stop` and `workspace close … --group`. Found live by the setup doctor: `command -v herdr` was denied (false positive), fixed and retested |
| N3 | the SessionStart line appears inside herdr and for an open run after resume and compaction | PASS for `startup` (inside and outside herdr) and `--resume` (open run listed with its Waiters and the re-arm instruction; a foreign run listed as such); `compact` shares the resume code path and was tested synthetically; a live `/compact` is UNVERIFIED |
| N4 | quick scenario with claude on 0.9.5: trust dialog, question dialog keys, cleanup | PASS (claude 2.1.302): `agent_not_ready` after 3.8 s at the trust dialog (`live_blocked_form`), `down enter` → `idle`, no `completion_seq`; PONG in 5 s (`done`, 330); AskUserQuestion read `blocked` (`interactive_question_blocked`), `down enter` chose Blue, marker `⏺ COLOR-Blue-r4y`; tab closed, `agent_not_found`, the user's focus unchanged |
| N5 | codex on 0.9.5: background wait, `completion_seq`, `esc` and `/stop` | PASS (codex 0.163): trust dialog → `agent_not_ready`, `enter` → `done` 339 before any prompt; a 100 s command with a background wait → `done` 344, marker `• LONG-m3p`; `esc` → `done` in 0.2 s with `sleep 300` still running ("1 background terminal running"); `/stop` without `--wait` killed it; `TaskStop` on a waiter removed the process and left the agent untouched. Not run: `ctrl+c` menu |
| N6 | agy on 0.9.5: trust dialog reads `idle`; the team-end marker wait | PARTIAL (agy 1.4.2): `agent start` → `idle`, `interactive_ready: true`, trust dialog on screen 4 s later and `explain` → no rule (`default_known_agent_idle_fallback`); `enter` → ready; `/teamwork-preview` → `blocked` at "Question 1/1", `enter` launched; the team worker stopped at once with `Individual quota reached` (429) while the leader's status bar showed room; the leader wrote the file itself and declined the end marker; the anchored `pane wait-output` regex did not match the quoted marker in prose and did match a marker alone on its line. UNVERIFIED: team rows with `idle` at the prompt (no real team ran); quota recovery |
| N7 | the `herdr-worker` subagent returns its fixed shape | PASS: a fresh session used `herdr-conductor:herdr-worker` twice. Short path: codex committed `w.txt`, the worker ran the done-checks itself, closed its workspace and returned the fixed shape; the main session spot-checked. `needs_decision` path: the worker answered claude's trust dialog (vouched folder), returned the Colour dialog with its keys and left the agent open; the main session pressed `enter` (Red), `agent wait` → `done`, marker `⏺ COLOR-Red-r7q`. UNVERIFIED: the long `running` path |
| N8 | a project through `/herdr-conductor:conduct` | PASS (local, headless `claude -p`, ~8 min): `/herdr-conductor:conduct` with the upfront answers supplied wrote a git-excluded `.herdr-conductor/` with CONDUCTOR.md and a run ledger (`owner_session`, Targets, step states, Waiters; closed at the end), opened its own workspace, created two worktrees with `--no-focus`, ran codex (feat-a) and claude (feat-b) in them with background waits and markers, had each branch reviewed read-only by the other harness (`reviews/<branch>.md`, first line PASS), merged both locally, removed both clean worktrees, closed its tabs and workspace last, and removed the codex trust entry it had added; the user's focus did not move. Checked on the machine: `git log --graph`, `git worktree list`, `git status`. Refusals tested separately: `dirty_worktree_requires_force` on an untracked file, `workspace_group_close_required` on the main workspace, then clean removal and close-main-last. UNVERIFIED: pull requests and `gh` (no remote), the watch table during a run |
| N9 | a remote round with a file brief through the drop folder | PASS (remote, herdr 0.9.5, codex): discovery with `--machine` (snapshot 28 workspaces, `status server --json`, `machine status`, bare `status` exit 2); a file brief copied with scp to a drop folder and confirmed with `ssh ls`; trust dialog → `agent_not_ready`, `enter`; one-line prompt pointing at the file → `done` 138; the commit, the file and the report checked over ssh; the report pulled back; marker `BRIEFDONE-w4n` alone on its line; workspace closed, scratch and the added trust table removed |
| N13 | install on a saved machine through herdr, as the README says | PASS (remote linux box, claude 2.1.303, herdr 0.9.5): scratch workspace with `--machine`, `agent start` → `agent_not_ready` at the trust dialog, `down enter` → `idle`; `/plugin marketplace add yigitkonur/herdr-conductor` → "Successfully added" and an automatic plugin reload; `/plugin install …` → scope menu (Herdr `done`, not `blocked`), `enter` → "Installed … active"; on disk: two-line settings diff, cache copy with exec bits, `claude plugin validate` passes, both hooks run on python 3.12; a fresh claude saw the skill and the worker agent and the session-start line, `/herdr-conductor:setup doctor` ran, and the guard denied `herdr server stop` under bypass permissions while `command -v herdr` passed; server still running, workspace and folder removed, plugin left installed |
| N14 | a background wait armed before `/compact` | PASS (herdr 0.9.5, claude 2.1.303): `sleep 100; echo HCW_r1x7` in the background, turn ended `ARMED`, `/compact` settled in a few seconds with "Task … still running in background"; at the 100 s mark the idle session woke by itself and printed `WOKE` plus the output. Waiters survive compaction, so the session-start line no longer says they died there (it still does after `--resume`) |
| N15 | the guard denies a prompt, keys, typed text or close aimed at the session's own pane, tab or workspace | PASS: 58 synthetic commands (`tests/guard_check.py`); live, a conductor asked to close its own tab: first run closed its own workspace because the guard compared the literal id and the model typed `$HERDR_TAB_ID`; fixed to judge the `$HERDR_*` spellings; rerun denied `herdr tab close "$HERDR_TAB_ID"` with the final-denial text and the model reported it and did not route around it |
| N16 | a claude worker with this plugin installed, briefed with the worker line, does the work itself | PASS: `notes.txt` written, no `herdr` call and no skill call in its transcript. Contrast without the worker line: the same (a plain brief that only mentions herdr never triggered the skill), so the risk the line guards against was not reproduced |
| N17 | "review the uncommitted change" | PASS: the run froze the candidate in `reviews/` (`calc-div.patch`, `calc-div.base` with the base SHA and the patch sha256, `candidate/calc.py`), a fresh claude wrote `calc-div-verdict.md` (first line PASS), the conductor reran its checks and found `git diff HEAD` unchanged; codex was out of quota, so the reviewer was a claude (said in the report) |
| N18 | `/herdr-conductor:conduct` with an open run in the session directory | PASS: one run folder before and after; the conductor adopted the unowned open run, wrote `owner_session`, ran the task through a claude agent (marker seen, `hello.txt` checked), closed the tab and the ledger |
| N19 | `herdr-worker` hand-over | PASS: a brief that asks for AskUserQuestion in a new folder: the worker answered the trust dialog under `trusted:` (macOS `/private/tmp` noted), returned `needs_decision` with `left_open: yes`, the tab stayed in the snapshot, the conductor asked the user, relayed `enter`, the file read `red`, and only then closed the tab |
| N20 | `agent start` with a name a live agent holds | SEEN (0.9.5): `agent_name_taken`, immediate, the message names the holder's pane, nothing typed into the new pane |
| N21 | the session-start hook and cards | PASS: a `CONDUCTOR.md` without `repos:` and one listing another repository → silent; one listing this repository (also as `https://….git`) → adopted; from a linked worktree the card in the main checkout's `.herdr-conductor/` is found; `compact` and `resume` print different waiter text |
| N22 | `/herdr-conductor:watch local --every 1` | PASS: the first sweep printed the table and flags (a foreign open ledger flagged, not adopted); the cron job (prompt `herdr-conductor watch sweep: …`) fired on its own as "Running scheduled task" and swept again against the baseline; `--stop` listed the job and deleted it |
| N11 | the eval suite scores the plugin above a no-plugin baseline | PASS (`claude plugin eval`, a small model, 2 runs per arm, $0.74, 130 s): 4 of 4 cases at 1.0; baseline 0 / 0.3 / 0.75 / 1.0 on trigger / start-wait / timeout-recovery / negative, delta +1.0 / +0.7 / +0.25 / 0; the skill-fired grader is plugin-only. Rerun on 0.1.2 ($0.77, 219 s): trigger 1.00 vs 0.00 (+1.00), start-wait 0.90 vs 0.40 (+0.50; one with-arm run wrote `codex exec` inside a sentence that forbids it and tripped the negative regex), negative 1.00 vs 1.00, timeout-recovery 0.50 vs 0.50 and, over two more reruns, 0.50 / 0.75 with against 0.50 / 0.75 without: with tools allowed the model still answers this plan-only question from its own knowledge and never calls the skill, so that case does not separate the plugin from the baseline (the first run scored it 1.0; the suite is noisy). Kept as it is, not tuned to pass |
| N12 | codex at its usage limit | SEEN (0.9.5, codex 0.163): `■ You've hit your usage limit … try again at <date>` then the "Switch to …" model dialog; Herdr `idle` (`osc_title_idle`), `prompt --wait` exit 0 `done` with a new `completion_seq`; a `herdr-worker` found it, left the dialog alone and returned `blocked` with the three options |
| N10 | install from the marketplace and run from the cache copy | PASS: public repo created, marketplace and plugin installed from `yigitkonur/herdr-conductor` (user scope, source github); fresh sessions with no `--plugin-dir` loaded the four skills and the worker agent, the skill ran `herdr-snapshot` from the cache copy, the guard denied `herdr --session … server stop` while `command -v herdr` passed, and the `herdr-worker` agent committed a file through a claude agent (checked on the machine, nothing left in herdr) |

## Trace

Where each finding is stated (paths relative to `plugins/herdr-conductor/`). Rewording a finding means updating its line in the same change.

| case | file | phrase |
| --- | --- | --- |
| T1 | skills/herdr/references/machines.md | A bare `status` is refused |
| T1 | skills/herdr/references/cli.md | a bare `status`, `agent explain --file` and `integration status` exit 2 |
| T2 | skills/herdr/references/cli.md | It returns at once (exit 0) only when the current state matches its set |
| T3 | skills/herdr/SKILL.md | With `--timeout 0` nothing was typed |
| T3 | skills/herdr/references/cli.md | `--timeout 0` was never typed |
| T4 | skills/herdr/references/cli.md | (four; `pane wait-output` has no `detection`) |
| T4 | skills/herdr/references/states.md | `agent read <target> --source detection` returns the text the rules read |
| T5 | skills/herdr/SKILL.md | `agent rename <target> --clear` (the old name then gives `agent_not_found`; the pane ID still works) |
| T6 | skills/herdr/SKILL.md | with a nonce new for each run |
| T6 | skills/herdr/references/cli.md | a stale `MARK_0` matched in 0.66 s |
| T7 | skills/herdr/references/worktrees.md | with `already_open: true` |
| T8 | skills/herdr/references/worktrees.md | `--workspace` and `--cwd` exclude each other |
| T9 | skills/herdr/SKILL.md | printed a 400 error and settled `done`, exit 0 |
| T9 | skills/herdr/references/harness-codex.md | the turn settled `done`, exit 0 |
| T10 | skills/herdr/SKILL.md | (`focused_workspace_id`, `focused_tab_id`, `focused_pane_id`) |
| T11 | skills/herdr/references/worktrees.md | A shell's `cd` does not move a pane |
| T12 | skills/herdr/references/dialogs.md | the next `agent get` read `blocked` |
| T13 | skills/herdr/SKILL.md | returns that `blocked` at once |
| T13 | skills/herdr/references/cli.md | the prompt got `agent_blocked` in 0.8 s |
| T14 | skills/herdr/references/cli.md | gave byte-identical output |
| T15 | skills/herdr/references/dialogs.md | agy's trust dialog has no detection rule |
| T15 | skills/herdr/references/states.md | That is how agy's trust dialog reads `idle`. |
| T16 | skills/herdr/references/states.md | classify it with this machine's rules (0.08 s) |
| T17 | skills/herdr/references/cli.md | the ratio shows only in the snapshot's `layouts` |
| T18 | skills/herdr/references/states.md | Over `--machine`, `integration status` exits 2 |
| T19 | skills/herdr/references/harness-claude.md | asked six questions in prose |
| T19 | skills/herdr/references/harness-claude.md | fullscreen, `recent` gave only the 20 visible rows |
| T20 | skills/herdr/references/states.md | A settle can be a single frame. |
| T20 | skills/herdr/references/harness-agy.md | no `● Agent(` row is left on screen |
| T21 | skills/herdr/references/states.md | Reads, explains and waits leave it in place |
| T22 | skills/herdr/references/harness-agy.md | the third quit and printed `agy --conversation=<id>` |
| T23 | skills/herdr/references/harness-claude.md | printed the answer and the marker again 28 s later |
| T23 | skills/herdr/references/dialogs.md | `clear` the pane before `agent start` there. |
| T24 | skills/herdr/references/harness-agy.md | posted exactly the one PR comment it allowed |
| N1 | skills/herdr/references/waiting.md | when the wait exits, the session is woken with a task notification |
| N2 | skills/herdr/SKILL.md | The plugin's guard hook denies the never-list |
| N3 | skills/herdr/references/ledger.md | The SessionStart hook prints the session directory |
| N4 | skills/herdr/references/dialogs.md | `agent_not_ready`, exit 1, after 3–5 s |
| N5 | skills/herdr/references/harness-codex.md | `agent prompt <t> "/stop"` without `--wait` |
| N6 | skills/herdr/references/waiting.md | Wait for that line in the background, server-side |
| N7 | agents/herdr-worker.md | Report (always this shape, as your final message) |
| N8 | skills/herdr/references/scenarios.md | The last page is autonomy |
| N9 | skills/herdr/references/briefs.md | Copy it to that machine's drop folder |
| N10 | skills/herdr/SKILL.md | Plugin root: `${CLAUDE_PLUGIN_ROOT}` |
| N13 | skills/herdr/references/harness-claude.md | the footer is the only sign of the menu |
| N14 | skills/herdr/references/waiting.md | a wait armed before `/compact` woke the session afterwards |
| N15 | skills/herdr/references/autonomy.md | a prompt, keys, typed text or close aimed at this session's own pane, tab or workspace |
| N16 | skills/herdr/references/briefs.md | ignore any herdr-conductor skill |
| N17 | skills/herdr/references/scenarios.md | A review the user asks for is always done |
| N18 | skills/conduct/SKILL.md | continue that run |
| N19 | agents/herdr-worker.md | leave it open (`left_open: yes`) |
| N20 | skills/herdr/references/cli.md | `agent_name_taken` |
| N21 | skills/herdr/references/ledger.md | a `CONDUCTOR.md` without a `repos:` block is not a card |
| N22 | skills/watch/SKILL.md | herdr-conductor watch sweep: |
| N11 | evals/plan-start-wait/prompt.md | List the exact herdr commands you would run |
| N12 | skills/herdr/references/harness-codex.md | neither the status nor the exit code shows the quota hit |

## Retest triggers

| change | how it shows | run again |
| --- | --- | --- |
| herdr client, server or protocol | `herdr --version`; `herdr [--machine m] status server --json` | lint, every case |
| detection rules | `agent explain <target> --json` → `manifest_version`, `manifest_source`, `local_override_shadowing_remote` | T2, T4, T9, T12, T13, T15, T19, T20, N4–N6 and the dialog tables; rules update while `herdr --version` does not |
| a harness version | `<harness> --version` on the machine (for a wrapped `agy`, the real binary's path, never the wrapper) | T2–T5, T9, T12, the harness files |
| a harness's own settings (bypass mode, fullscreen TUI) | its settings file | T19 and the harness file |
| herdr integrations | `herdr integration status` on each machine (exit 2 over `--machine`) | T15, T20 and the harness files |
| server restart or reconnect | snapshot IDs differ from the ledger | re-resolve targets; T10 |
| a new machine | `herdr machine list --json` | T1, T6 and one agent start there |
| Claude Code version | `claude --version` | N1–N3, N7 |
| an edit to the plugin | `git diff` | lint; the cases whose Trace lines it touched |

## When something new is learned

1. **Write it down as seen**: command, reply, exit code, time, server, herdr and harness versions, into the run ledger. A claim from elsewhere (docs, another session, this plugin) is a prediction, not a result.
2. **Reproduce the smallest variant** in a workspace you created. A CLI contract (exit code, field, flag) needs one run; a state, timing or focus effect needs a second run, or the opposite condition beside it (T3: `--timeout 0` and `--timeout 1000` gave opposite answers to one question). Predict what you will read, not only the state (T20's "`working`, then `done`" held while the team still worked). A flag that misbehaves over `--machine` runs once more locally before it is blamed, and a cause read from one run gets a control run (T21).
3. **Classify it**: a CLI fact (the lint's drift check covers it), a behaviour (add or update a case here), or a contradiction of the plugin (add a regression rule to `tools/lint.py` that fails on the old wording, and see it fail before the fix).
4. **Find every restatement** before editing: the case's Trace lines, then a grep of its key terms across the plugin. Fix all of them in one change.
5. **Re-run**: lint to 0 FAIL, then the cases whose Trace lines changed.
6. **Record**: the case row (result, date, versions) and its Trace lines. When a new result contradicts a recorded one, run the old case again before overwriting it; if both hold, the difference is a condition (version, harness, focus, machine) and the row names it.
