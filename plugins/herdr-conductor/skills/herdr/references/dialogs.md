# Dialogs: trust, questions, permissions

Back to [SKILL.md](../SKILL.md). The generic procedure is in SKILL.md ("Blocked agents and dialogs"). This file holds what each harness shows and which keys passed it. Who may answer what: references/autonomy.md.

## First run in a new folder (trust)

Every harness met a new folder with a trust dialog, `/tmp` subfolders and fresh worktrees included. Who may answer it: the trust rule in references/autonomy.md.

| harness | what `agent start` returned | on screen | keys that passed it |
| --- | --- | --- | --- |
| claude | `agent_not_ready`, exit 1, after 3–5 s; Herdr reads `blocked` (`live_blocked_form`) | trust dialog, default "No, exit" | `down`, `enter` |
| codex | 0.9.5: `agent_not_ready`, exit 1, `blocked` (`trust_directory`). *(seen 0.9.3: `idle`, exit 0, `interactive_ready: true`; the next `agent get` read `blocked`)* | "Trust this folder?" with "1. Trust and continue / 2. Quit", footer "enter continue · esc quit"; on some machines "Cannot use the background server" first (1 run without daemon / 2 cancel) | `enter`; with the daemon dialog first, `1` then `enter` |
| agy | `idle`, exit 0, after ~4 s, `interactive_ready: true`, sometimes before the dialog appeared (about 3 s later) | "Yes, I trust this folder" as default | `enter` |

- After its trust dialog was answered, codex read `done` with a new `completion_seq` before any prompt (0.9.5): record that value as the baseline.
- agy's trust dialog has no detection rule: it reads `idle`, `--until blocked` times out, a default wait returns at once, and a prompt sent into it is taken as the dialog's Enter (the folder gets trusted, the text is lost, `agent_prompt_stalled` after 12.7 s) *(seen 0.9.3)*. Read the screen a few seconds after an agy start before prompting.
- Compare the folder the dialog names with the folder you meant: macOS shows `/tmp/x` as `/private/tmp/x`. A different folder is a routing mistake, not a dialog to accept.
- The answer outlives the run. Trust stores: codex `~/.codex/config.toml` (a `[projects."<path>"]` table), claude `~/.claude.json` (`projects[*].hasTrustDialogAccepted`), agy `~/.gemini/antigravity-cli/settings.json` (`trustedWorkspaces`; it stores the resolved path, and a listed parent does not cover its subfolders). After a scratch run, remove only the entries the run added (note in the ledger whether an entry existed before you answered): codex's table, agy's entry; every running claude rewrites `~/.claude.json`, so leave claude's entry and record it.
- Other startup dialogs (login, model picker, update notice, background server) are read, not assumed: answer only what the run may answer, report the rest.

## Question dialogs

What each harness showed when asked to use its own question tool:

| harness | how it asks | Herdr status | keys |
| --- | --- | --- | --- |
| claude | AskUserQuestion: up to four questions as tabs plus a Submit tab, previews beside options; more questions come as a second dialog. One question has no Submit tab and adds "Type something." and "Chat about this" rows; footer "Enter to select · ↑/↓ to navigate · Esc to cancel" | `blocked` for each dialog (`interactive_question_blocked`) | `enter` picks (one question: picks and submits); in multi-select `enter` toggles and a "Next" row moves on; `n` opens notes, typed with `pane send-text`; the Submit tab needs `enter` |
| codex | questions in prose plus "Queued follow-up inputs ? N questions shift+← to answer"; title "[ . ] Action Required" | `blocked`, then `done` when the turn ended unanswered about a minute later | answer the prose with an ordinary prompt; or `shift+left` opens the native panel (references/harness-codex.md) |
| agy | `ask_question`: one question per page, "Question n/N", previews in fences; footer "↑/↓ Navigate · enter Select · esc Skip · ctrl+r Review" | `blocked` only when the page is short; tall pages read `idle` or `done` | single: arrows and `enter`; multi: `space` toggles, `enter` submits; `right`/`left` move; "Write-in..." opens "Your answer:", typed with `pane send-text`, then `enter` "Submit All" |

- In claude, `enter` while the notes field has focus submits the note alone and drops the highlighted option; leave the field first if both should count.
- A question asked in prose (claude grilling, codex after its panel closed) ended the turn: the status is `done`, not `blocked`. Read the questions and answer them in one ordinary prompt.
- agy's question rule wants a line starting with "question" and a `─` border within the bottom 16 non-empty lines; a page whose previews are taller hides both.

## Permission dialogs

- Each harness prints its keys in the footer: codex `y` / `p` / `esc`, claude "Enter to select · Tab", agy "space Toggle · enter Submit". Send what the screen offers, then read again.
- Check the selected option every time: a later claude dialog had "switch to auto mode" selected by default. Move to the scoped, one-time option and confirm it on screen before `enter`.
- Declining in codex cancels the whole turn, which still ends `done`.
- After a cancelled approval, claude showed "Interrupted · What should Claude do instead?" and a ready composer while Herdr still read `blocked`, so `agent prompt` refused the correction. Confirm the composer is empty and the process is claude, then `pane send-text <pane> '<text>'`, read the staged text, and `pane send-keys <pane> enter`.
- Whether permission dialogs appear at all depends on the agent's own settings: a claude whose settings set `permissions.defaultMode` to `bypassPermissions` showed "bypass permissions on" with no flag typed. A per-launch `--permission-mode manual` brings the dialogs back without touching global settings.

## Reused panes

A dialog footer left in a reused pane's scrollback ("Enter to confirm · Esc to cancel") kept claude's `live_blocked_form` rule (bottom 16 non-empty lines) matching, so a fresh claude at an empty prompt read `blocked` and `agent prompt` returned `agent_blocked`. `clear` the pane before `agent start` there.
