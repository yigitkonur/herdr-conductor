# codex under herdr

Back to [SKILL.md](../SKILL.md) · dialogs: [dialogs.md](dialogs.md).

## Starting

- `herdr agent start <name> --kind codex --pane <pane> --timeout 30000 -- <args>`. Arguments that matter: `-m <model>`, `-c model_reasoning_effort=<level>` (a config key), `-p <profile>`, `-s read-only|workspace-write|danger-full-access` (sandbox), `-a on-request|never` (`untrusted` was rejected). Supervised, asking before it acts: `-- --sandbox read-only --ask-for-approval on-request`. Model and effort come from the user's routing or the request.
- Never `codex exec` (including `exec review`), standalone `codex review`, CLI `codex queue`, `nohup codex` or print modes, even after a quota hit or a TUI failure: start afresh with `agent start`.
- Given a model it cannot use, codex started normally; the first prompt printed a 400 error ("not supported when using Codex with a ChatGPT account") and the turn settled `done`, exit 0. Read the screen after the first turn.
- A pane that rendered narrow (`stty size` showed 12 columns in a new workspace) is no reason for print mode: close that tab and start in a new one *(untested fix)*.
- A `workspace-write` codex could not reach the herdr socket ("Operation not permitted"); it cannot run herdr commands itself unless approvals allow it. That only matters if a brief asks it to.
- agy's `/teamwork-preview` and `/boost` are not codex modes: remove them when moving a brief.
- Since herdr 0.9.5 no Codex turn hooks are installed and its status comes from screen detection; an older integration still installed prints hook warnings (`herdr integration install codex` updates it, with the user's approval).

## How its screen behaves

- Starts in about 5 s; trivial prompts take 3–7 s. On 0.9.5 (codex 0.163) its trust dialog makes `agent start` return `agent_not_ready`, and after `enter` it read `done` with a new `completion_seq` before any prompt (references/dialogs.md). Answers are `• text` lines, so the marker line reads `• MARKER`; your prompt comes back rewrapped.
- It redraws one screen (45 lines on one machine; `--lines 200` gave the same 45 from every source); the bottom six to eight lines are the input box and the status bar (context left, quota such as "weekly 8% left"; turns still ran for a while at "weekly 0% left", so the bar is a warning and the error text is the hit). Read above them. An answer longer than a screen goes to a file and the reply is only its path.
- Herdr reads its state from the window title (`osc_title_*` rules) and its trust dialog from the top 20 non-empty lines (`trust_directory`). The title is the thread name from the first prompt and goes stale.
- A prompt sent mid-turn is folded into that turn ("Messages to be submitted after next tool call"); one completion answered both. Send the next task after the agent is ready, once.
- Next-turn queue with `tab` (`pane send-text` the text, read the composer, `pane send-keys tab`) worked on one codex build: the follow-up ran as its own turn after the active one. It is capability-gated: verify it on the installed build in a scratch pane before relying on it; never press `enter` after `tab` as a fallback.

## Usage limit

A codex out of quota answers the prompt with `■ You've hit your usage limit. Visit … or try again at <date and time>.` and opens a model-switch dialog: "Approaching rate limits / Switch to <smaller model> for lower credit usage?" with `1. Switch`, `2. Keep current model`, `3. Keep current model (never show again)`, footer "enter select · esc back" *(0.9.5, codex 0.163)*. Herdr read it `idle` (`osc_title_idle`), and `agent prompt --wait` settled `done` with a new `completion_seq`: neither the status nor the exit code shows the quota hit, only the screen does. Do not pick option 1 or 3 on your own: switching the model changes cost and capability and is the routing's or the user's call (`esc` backs out). Recovery as for agy (references/harness-agy.md, steps 3 and 4): switch harness per the routing, or schedule a one-shot cron at the reset time.

## Question panel

- Asked for its question tool, codex printed questions in prose plus "Queued follow-up inputs ? N questions shift+← to answer" (`blocked`), and ended the turn unanswered about a minute later (`done`) *(seen 0.9.3)*.
- `agent send-keys <t> shift+left` opens the native panel; read the current question and selected option before any key; navigate to the authorized option, confirm it on screen, `enter` submits that question; the next panel may show only the remaining question. `shift+right` returns to the composer without answering. After the turn ends the panel is gone: answer with an ordinary prompt that names the question.

## Interrupting a turn (an agent running `sleep N` for you)

| key | what happened | what actually stopped the command |
| --- | --- | --- |
| `esc` | turn ended `done` within 1 s (0.2 s on codex 0.163, "Conversation interrupted"); the command lived on: "1 background terminal running · /ps · /stop" | `agent prompt <t> "/stop"` without `--wait` |
| `ctrl+c` | menu "Task is still running": 1 Cancel task / 2 Run in background / 3 Exit; status stayed `working` (`osc_title_working`), so a wait timed out | `enter` (Cancel) ended the turn `done`, command still alive; then `/stop` |

Options 2 and 3 exit codex itself. Confirm on the machine that the process is gone (`pgrep -f`).

## Resume

Read the registry, the visible screen and `pane process-info` first. Resume the exact session (`codex resume --help` on that machine names the syntax) only after the old process is dead and the pane is a shell; restore scope and model in the first prompt; never rerun a git operation or message before its effects are reconciled.
