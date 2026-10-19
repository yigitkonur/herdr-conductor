#!/usr/bin/env python3
"""Feed synthetic Bash commands to the guard hook and check deny / pass.

usage: python3 -I tests/guard_check.py        (exit 1 on any miss)
The session's own IDs are set below; nothing here runs herdr.
"""
import json
import os
import pathlib
import subprocess
import sys

GUARD = pathlib.Path(__file__).resolve().parent.parent / "plugins/herdr-conductor/hooks/scripts/guard.py"
ENV = {**os.environ, "HERDR_PANE_ID": "wOWN:p1", "HERDR_TAB_ID": "wOWN:t1", "HERDR_WORKSPACE_ID": "wOWN",
       "HOME": "/nonexistent"}  # no user config, so no guard_allow
DENY = [
    "herdr server stop", "herdr --session x server reload-config", "/usr/local/bin/herdr update",
    "herdr config reset-keys", "herdr channel set preview", "herdr machine reconnect box", "herdr session delete x",
    "herdr agent attach a", "herdr terminal attach t", "herdr", "herdr --remote box",
    "herdr worktree remove --workspace w9 --force", "herdr workspace close w9 --group", "pkill -f herdr",
    "ls; env FOO=1 timeout 5 herdr server stop", "sh -c 'herdr update'", "ssh box 'herdr server stop'",
    "echo $(herdr server stop)", "herdr pane run w9:p1 'herdr server stop'", "herdr pane send-text w9:p1 'herdr update'",
    "herdr agent start a --kind codex --pane w9:p1 -- --dangerously-bypass-approvals-and-sandbox",
    "herdr agent start a --kind codex --pane w9:p1 -- -s danger-full-access",
    "herdr agent start a --kind claude --pane w9:p1 -- --permission-mode bypassPermissions",
    # the session's own pane, tab and workspace
    "herdr tab close wOWN:t1", "herdr workspace close wOWN", "herdr pane close wOWN:p1",
    "herdr agent prompt wOWN:p1 'hi' --wait", "herdr agent send-keys wOWN:p1 enter", "herdr pane run wOWN:p1 'ls'",
    "herdr pane send-text --current 'x'", "herdr pane close --current", "herdr agent start a --kind claude --pane wOWN:p1",
    "herdr worktree remove --workspace wOWN", "herdr pane run w9:p1 'herdr tab close wOWN:t1'",
    "herdr tab close $HERDR_TAB_ID", "herdr tab close \"$HERDR_TAB_ID\"", "herdr workspace close ${HERDR_WORKSPACE_ID}",
    "herdr agent prompt $HERDR_PANE_ID 'x'", "cd /tmp && herdr pane close \"${HERDR_PANE_ID}\"",
    "herdr worktree remove --workspace $HERDR_WORKSPACE_ID",
]
PASS = [
    "herdr api snapshot", "herdr agent get a", "herdr agent read wOWN:p1 --source visible --lines 40",
    "herdr agent wait wOWN:p1 --timeout 1000", "herdr pane split --current --direction right --no-focus",
    "herdr tab close w9:t2", "herdr workspace close w9", "herdr agent prompt w9:p1 'hi' --wait",
    "herdr --machine box tab close wOWN:t1", "herdr --session s pane close wOWN:p1",
    "command -v herdr", "herdr --version", "grep -n 'herdr server stop' README.md",
    "herdr agent prompt a \"$(cat <<'EOF'\nnever run herdr server stop or pkill herdr\nEOF\n)\" --wait",
    "herdr worktree remove --workspace w9", "herdr workspace create --cwd /tmp --no-focus",
    "herdr agent start a --kind claude --pane w9:p1 --timeout 30000", "ls /tmp",
]


def denied(cmd):
    p = subprocess.run([sys.executable, "-I", str(GUARD)], input=json.dumps({"tool_input": {"command": cmd}}),
                       capture_output=True, text=True, env=ENV, timeout=10)
    return '"permissionDecision": "deny"' in p.stdout


bad = [("should deny", c) for c in DENY if not denied(c)] + [("should pass", c) for c in PASS if denied(c)]
for how, c in bad:
    print(f"MISS {how}: {c}")
print(f"{len(DENY) + len(PASS) - len(bad)}/{len(DENY) + len(PASS)} ok")
sys.exit(1 if bad else 0)
