# agy (Antigravity CLI) under herdr

Back to [SKILL.md](../SKILL.md) · dialogs: [dialogs.md](dialogs.md).

## Before starting

- The `agy` on a machine's PATH may be a wrapper script that does account work on every launch (a preflight that can switch the machine's account, extra flags such as `--dangerously-skip-permissions`). Never launch it just to probe: `agy --version` over ssh switched a machine's account. Look at the wrapper with `file` and `head` instead; the real binary's path is in it.
- `herdr agent start <name> --kind agy --pane <pane> --timeout 30000 -- <args>`. Arguments that matter: `--model` (`agy models` lists them, through the wrapper's side effects), `--effort low … max`, `--mode accept-edits|plan`, `--sandbox`, `--add-dir`, `--new-project`, `--project`, `-c` (continue), `--conversation=<id>` (resume). Never `agy -p` or `--print`. Bypass and "dangerously" flags are the user's choice, never a default.
- Trust dialog: reads `idle`, may appear about 3 s after `agent start` returned (dialogs.md). Read again before the first prompt.

## Briefing agy

- The prompt's first word can pick agy's own mode: `/teamwork-preview` forms a team, `/boost` takes bugs and reviews, `/plan` checks and expands a plan. They are agy's, not the plugin's: use them when the brief or the routing says so, and remove them when a brief moves to another harness.
- A brief longer than a few lines goes into a file on agy's machine and the prompt is one line:

  ```text
  /boost Your mission is in <path>. Read the whole file before acting; it is self-contained.
  ```

  agy read such a file from outside its folder, posted exactly the one PR comment it allowed and wrote its report where told.
- For a team, the brief adds two rules *(untested)*: parallel writers each work in their own branch workspace, and every worker inherits agy's model. Still hand it one plan step, not the plan.

## Team runs

On 0.9.5 with agy 1.4.2 a `/teamwork-preview` brief was again `blocked` at "Question 1/1" (launch the drafted team; `enter` took the recommended option), then its worker stopped right away with `Individual quota reached` (429) while the leader's own status bar still showed room; the leader wrote the file itself, reported the failure in prose, settled `idle` with no `completion_seq`, and declined to print the end marker. Quota can hit a team worker alone.


`/teamwork-preview <task>` first wrote a prompt draft and asked "Question 1/1" how to proceed (`blocked`; `enter` took the recommended small team), then ran an implementer, three reviewers and a victory auditor: about 22 minutes for a one-line file *(seen 0.9.3)*. While the team ran, Herdr settled `idle` once and `done` three times, each gone a moment later; since 0.9.4 agy reads `idle` at its prompt while subagents run by design. The run is over when the team-end marker appeared (references/waiting.md), no `● Agent(` row is left on screen, and the result checks out on the machine.

## How its screen behaves

agy keeps its transcript from the banner on (the banner names the signed-in account and model): `▸ Thought for …` lines, `● Bash(…)` tool lines, then plain answer lines, above a `>` input box and a status line (context, 5H and 7D quota). Herdr reads `working` from its command lines and falls back to `idle` when no rule matches.

## Quota

A quota hit is easy to miss: agy's exit code is always 0 and Herdr's status hides it (it read `blocked`, `working` and `idle` on quota-dead panes; Herdr's own TUI marks them with a red ✕). Some rule sets have `quota_reached_blocked`.

**Signs** (read the screen; the status proves nothing):

- `⚠ Individual quota reached.` with `Resets in 3h6m2s.` and an `Error ID: …` line;
- the bottom status bar shows `5H: 0%` and a reset timer;
- no progress since the last wait.

So after every wait on an agy agent, and whenever one seems stuck, run `herdr [--machine m] agent read <name> --source visible --lines 15` and look for `quota reached`. First check whether its work already landed (`git log`, `git merge-base --is-ancestor <branch> <base>`): if so, close its tab instead of resuming it.

**Recovery, in order** (the autonomy level decides how far the run goes alone; references/autonomy.md):

1. If the machine has an account rotation command (`machines.<label>.rotate_command` in the user config), run it there; a listing-only command just reads. Without one, rotation is the user's.
2. A running agy keeps its old login, so restart it in place: note `.agent_session.value` from `agent get` (the conversation id), then `agent send-keys <t> ctrl+c` until `agent get` says `agent_not_found` (three presses on 1.2.16: the first interrupted the turn, the third quit and printed `agy --conversation=<id>`). `pane run <pane> 'clear'`, then `agent start <name> --kind agy --pane <same> -- <same args> --conversation=<id>`, wait about 5 s, answer the trust dialog if it shows, and prompt "continue from where you left off. resume any failed tasks/subagents if possible, otherwise restart them. keep going until everything is fully complete." An 8-step task cut at step 2 finished from step 2, nothing repeated. The quota line stays the last thing on screen until a new prompt arrives, so Herdr can read the resumed agy `blocked` and `agent prompt` return `agent_blocked`. Only when a visible read shows the quota line, an empty `>` input box and no key footer, type the prompt with `pane send-text <pane> "<prompt>"`, then `pane send-keys <pane> enter`, and confirm `working` on screen; any other screen is a dialog (references/dialogs.md).
3. Out again, or nothing to rotate: switch harness per the routing (or ask): quit agy as in step 2, start the other harness in that pane, and give it the brief without agy's slash commands, plus "the previous agent stopped mid-way; read git log and finish".
4. Or wait for the reset: a one-shot `CronCreate` at the reset time that resumes this step (references/waiting.md).

A quota-dead tab is closed only after its replacement's result is checked. **Never:** trust a `done`, `idle` or `blocked` agy status without reading the screen; resend a prompt because a wait timed out; probe with `agy --version` or a bare `agy`.

## Interrupting a turn (an agent running `sleep N` for you)

| version | key | what happened | what actually stopped the command |
| --- | --- | --- | --- |
| 1.2.15 | `esc`, `ctrl+c` | nothing; status `working` throughout (`background_command_working`) | `agent prompt <t> "/tasks"` without `--wait` opens its task list; `k` kills the highlighted task, the turn ends `done`; `esc` closes the list |
| 1.2.16 | `ctrl+c` | the first interrupted the turn ("Interrupted · What should Antigravity CLI do instead?"), the second did nothing, the third quit agy | whether the command died with the turn was not checked; confirm with `pgrep -f` |
