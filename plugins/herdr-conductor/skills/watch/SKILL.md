---
name: watch
description: Show what is running in herdr across this machine and saved machines - one table per server with workspace and tab labels, agent states and completion_seq - and flag agents that are blocked, out of quota or finished; optionally repeat on a schedule. Invoked as /herdr-conductor:watch [local|<machine>|all] [--every <minutes>] [--stop].
argument-hint: "[local|<machine>|all] [--every <minutes>] [--stop]"
disable-model-invocation: true
allowed-tools: Bash(herdr *), Bash(herdr-snapshot *), Read, CronCreate, CronList, CronDelete
---

# Watch herdr

Arguments: $ARGUMENTS

Read-only: this command takes nothing over. Acting on an agent the session does not own needs the user's go.

1. Servers: `local` (default), a machine label, or `all` (this machine plus every enabled label in `herdr machine list --json`).
2. For each server run `herdr-snapshot` (add `--machine <label>` for a saved machine; if it is not on PATH, `python3 "${CLAUDE_PLUGIN_ROOT}/bin/herdr-snapshot"`). A machine that fails gets `herdr machine status <label> --json`; report its reason instead of a table.
3. Flag the agents as defined under "watch" in `${CLAUDE_PLUGIN_ROOT}/skills/herdr/references/scenarios.md`, reading only what is needed (`herdr [--machine m] agent read <target> --source visible --lines 15`).
4. Print one compact table per server and the flags beneath it; lead with what needs the user.
5. `--every <minutes>`: run `CronList` first and reuse a job whose prompt already starts with `herdr-conductor watch sweep:`; otherwise create a recurring `CronCreate` job whose prompt is the plain request `herdr-conductor watch sweep: <same servers>. Print the herdr watch table and flags, read-only.` (a scheduled fire does not run a slash command of a user-invoked skill; the herdr skill routes this request to the watch scenario), pick a minute that is not :00 or :30, and tell the user its id, its next run time and that it fires only while the session is idle, lives only in this session and expires after 7 days. `--stop`: `CronList`, then `CronDelete` the jobs whose prompt starts with `herdr-conductor watch sweep:`.
