# Waiting on agents from Claude Code

Back to [SKILL.md](../SKILL.md). `herdr agent wait` is the heartbeat: every prompt is followed by a wait, and every wait by a screen read, before the next step is chosen. Only a state change ends a wait; time passing or an empty read never does. Herdr cannot call this session, so the session waits through its own tools.

## Which wait

| work | do |
| --- | --- |
| A turn expected to take a few minutes | Foreground `agent prompt … --wait --timeout <ms>`, herdr's timeout at most 570000 and the Bash tool's `timeout` at least herdr's plus 30000. |
| Longer, or several agents at once | Confirm delivery with `agent prompt … --wait --until working --timeout 30000`, then one background wait per agent (below). |
| An agent you did not prompt (adopted, watched) | A background wait straight away; it returns at once when the current state already matches its set. |
| A team run whose leader settles while workers run | The team-end wait (below). |

The Bash tool caps a foreground call at 10 minutes and then moves it to the background; plan for that instead of being surprised by it. macOS has no `timeout` command: bound every wait with herdr's own `--timeout`.

## Background waits

```bash
# Bash tool, run_in_background: true. One task per agent.
herdr [--machine m] agent wait <name> --timeout 3600000 2>&1; echo "HC_WAIT_EXIT=$?"
```

- The task returns its id at once. Write it into the ledger's Waiters line with the agent name, server, pane, marker and the `completion_seq` from the last settle before this prompt (or `absent`). Then do other work or end the turn: when the wait exits, the session is woken with a task notification, and its output file holds herdr's JSON and the exit line.
- `HC_WAIT_EXIT=0`: the agent settled. Read the screen and run the post-settle checklist (references/states.md), compare `completion_seq` with the ledger (greater-than), and act. Re-arm only when the agent is `working` again: a default wait on an `idle` or `done` agent returns at once, so otherwise arm `--until working` first, or use the team-end wait.
- `HC_WAIT_EXIT=1`: herdr returned a JSON error; read `.error.code`.
  - `timeout`: the agent did not settle in that time. Read the screen once; if it is still working, arm the same wait again. A 570 s wait once timed out five minutes after the reviewer had written its report, and Herdr showed `idle` a minute later (cause unknown), so every timeout gets that one read.
  - `agent_not_found` or `agent_not_running`: the agent exited, was renamed or its pane moved. Re-resolve by name from a fresh snapshot; never adopt a pane by position.
  - anything else (connection, `workspace_not_found`): stop that line, record it, report it.
- Several agents: one background task each. Each wakes the session on its own; there is no need to batch.
- `TaskStop <task_id>` ends a wait without touching the agent. Stop an agent's waiters before closing its tab or workspace: a wait outlived the workspace it watched, and a wait on a moved pane ends `agent_not_running`.
- Stop only waiters this session started. Other sessions may wait on the same agents; all of them return.
- Never poll Herdr (`agent get` or `agent read` in a loop, `sleep` loops). A lost wait is restarted; a `completion_seq` above the ledger's says Herdr saw a turn end meanwhile.

## Team runs (leader settles while workers run)

agy and grok read `idle` at their prompt while their subagents still run, and an agy `/teamwork-preview` run settled `idle` and `done` several times before its team finished *(seen 0.9.3; by design since 0.9.4)*. A default wait therefore returns early, and waiting again returns at once. Do this instead:

1. Give the brief a marker the agent prints only after every worker has finished and the result is checked, built from two parts so the typed prompt never contains it whole: "When everything is finished and checked, print on its own line the word `TEAMEND` followed by `-` and `k3x9`" → the screen will show `TEAMEND-k3x9` only when the agent writes it.
2. Wait for that line in the background, server-side, anchored so it matches only a line that holds the marker alone (an agy that declined to print it quoted it in a sentence, and an unanchored pattern matched that): `herdr [--machine m] pane wait-output <pane_id> --regex '^[^A-Za-z0-9]*TEAMEND-k3x9\s*$' --timeout 3600000 2>&1; echo "HC_WAIT_EXIT=$?"`. Use a new suffix for every run: `wait-output` searches what is already on screen, so a reused marker matches at once.
3. When it matches, read the screen: no `● Agent(` row (or the harness's equivalent) may be left, and the result must check out on the machine. A team row still running means the marker came early: wait on the agent with `--until working`, then on the default set, and read again.

Local rule sets may already report a running team as `working` (some carry `subagent_working` or `background_agents_working` rules); `agent explain` on that machine says which. The marker wait works either way.

## After compaction, resume or a restart

- Background tasks do not survive `--resume` or a new session, and after compaction the ids in the ledger may point at nothing. Treat every Waiters line as unknown: `agent get <name>`, compare `completion_seq`, read the screen, then re-arm. Never resend a prompt because its waiter is gone.
- A step whose state is short of `completed` (references/ledger.md) gets `agent get`, a visible read and a marker check before anything is sent.
- A wait silent well past its `--timeout` is lost: `agent get`, then re-arm.

## Ending the turn while agents work

Allowed when every working ledger agent has a live waiter task, or a `/loop` or cron covers it. Before ending, list the Waiters you rely on. If an agent has no live waiter (it was adopted mid-turn, a wait failed, the session runs headless), arm one, or say in the reply which agent is unwatched and how to resume it. Never end the turn on a working agent silently: a supervisor that does loses its agents until someone writes again.

## Fallbacks

- **`/loop`** (the user runs it, for multi-hour autopilot or when background wake-ups prove unreliable): "continue the open herdr-conductor run in `<session dir>`". Each iteration reads the ledger, acts on finished waits, re-arms, and schedules its next wake-up with a long fallback delay (20 minutes or more), since the background waits are the real signal.
- **`CronCreate`, one-shot**: a check-back when nothing harness-tracked is running, for example waiting for a human login, or resuming an agent at a quota reset time ("Resets in 3h6m"). Cron jobs fire only while the session is idle, live only in this session unless made durable, and recurring ones expire after 7 days.
- **Notifications to the user**: with `notify: herdr` in the config, `herdr notification show "herdr-conductor: decision needed" --body "<one line>" --sound request` puts a toast on the user's Herdr. It is best effort: `no_foreground_client` and `rate_limited` are normal replies.

## Questions while agents work

AskUserQuestion blocks the session: no notification is handled while a question is open, so every other agent finishes or blocks unattended. Ask only when no ledger agent is working or nothing independent is left. Otherwise write the question under "Waiting on the user" in the ledger, keep the other agents moving, and ask the collected questions together when the session would otherwise stop.

## Shell traps (zsh)

- `$PIPESTATUS` is empty in zsh (use `setopt pipefail` and `${pipestatus[1]}`). A trailing `| head` hides the exit code. Any command in between, `echo` included, resets `$?`: take `rc=$?` right after the command.
- `${=VAR}` splits a variable into words; an unmatched glob is an error.
- Errors come as JSON on stderr with exit 1 and an empty stdout, so read with `2>&1`; syntax errors exit 2 with plain usage.
- Checks on a saved machine: `ssh -o BatchMode=yes -o ConnectTimeout=10 <target> '<cmd>'`, with the target from `herdr machine list --json`.
