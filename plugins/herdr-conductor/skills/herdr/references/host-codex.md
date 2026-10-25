# When the host is Codex

This plugin was written for Claude Code. Codex loads the same skills and hooks; these are the differences. Everything else in the skill holds.

- **Plugin root.** `${CLAUDE_PLUGIN_ROOT}` is not substituted. Wherever a skill shows it literally, the root is two folders above this skill's `SKILL.md` (the folder that holds `bin/`, `hooks/` and `skills/`).
- **`herdr-snapshot`** is not on PATH. Run `python3 <root>/bin/herdr-snapshot [--machine m]`.
- **No `herdr-worker` subagent.** Task runs go direct: start the agent, wait, read the screen, verify on the machine.
- **No background tasks, no wake-up.** Wait in the foreground with herdr's own `--timeout` (milliseconds). If the shell tool hands back a still-running process, keep reading that same process; never start a second wait on the same agent. Do not end a turn on a working agent without naming it, the pane and the command that resumes it ("next message: `herdr agent wait …`").
- **No cron, no `/loop`.** `watch --every` is unavailable: print one sweep. A quota reset becomes a line in the report with the time.
- **No AskUserQuestion.** Ask in plain text: the question, numbered options, your recommendation first. Several open questions go together in one message.
- **Skills** are invoked as `$herdr`, `$conduct`, `$watch`, `$setup`. `$ARGUMENTS` is not substituted: the goal, servers and flags are what the user wrote after the skill name.
- **Shell tool.** Codex's `PreToolUse` guard sees only shell commands. The hands-off rules for the session's own pane, tab and workspace still apply when the guard does not see a command.
- **Worker agents you start** are ordinary herdr agents; their harness rules (`harness-*.md`) are unchanged.
