---
name: watch
description: Show what is running in herdr across this machine and saved machines - one table per server with workspace and tab labels, agent states and completion_seq - and flag agents that are blocked, out of quota or finished; optionally repeat on a schedule. Invoked as /herdr-conductor:watch [local|<machine>|all] [--every <minutes>] [--stop].
argument-hint: "[local|<machine>|all] [--every <minutes>] [--stop]"
disable-model-invocation: true
allowed-tools: Bash(herdr *), Bash(python3 *), Read
---

# Watch herdr

Arguments: $ARGUMENTS

Read-only: this command takes nothing over. Acting on an agent the session does not own needs the user's go.

1. Servers: `local` (default), a machine label, or `all` (this machine plus every enabled label in `herdr machine list --json`).
2. For each server run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py"` (add `--machine <label>` for a saved machine). A machine that fails gets `herdr machine status <label> --json`; report its reason instead of a table.
3. Flag, per agent, after reading only what is needed (`herdr [--machine m] agent read <target> --source visible --lines 15`):
   - `blocked`: the dialog's question in a few words and its keys;
   - agy agents: `quota reached` or a reset timer on screen, whatever the status;
   - `done`, or a `completion_seq` above the one in the previous sweep: finished since last looked;
   - agents on an open ledger in this project with no live waiter task.
4. Print one compact table per server and the flags beneath it; lead with what needs the user.
5. `--every <minutes>`: create a recurring `CronCreate` job whose prompt is `/herdr-conductor:watch <same servers>`, pick a minute that is not :00 or :30, and tell the user its id, its next run time and that it fires only while the session is idle, lives only in this session and expires after 7 days. `--stop`: `CronList`, then `CronDelete` the jobs whose prompt starts with `/herdr-conductor:watch`.
