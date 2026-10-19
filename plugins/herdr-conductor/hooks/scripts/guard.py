#!/usr/bin/env python3
"""PreToolUse(Bash) guard for herdr-conductor.

Denies the herdr never-list (server control, updates, config resets, machine and
session management, interactive clients, forced worktree removal, group closes,
killing herdr, approval-bypass flags in agent arguments). Everything else passes.
Heredoc bodies and quoted brief text are data, not commands: only words at
command position are judged, also inside `sh -c`, `ssh <target> '…'` and `$(…)`.
Text typed into a pane (`pane run`, `pane send-text`) is judged as a command too.
Exceptions: `guard_allow:` prefixes in ~/.config/herdr-conductor/config.md, matched
per simple command. Fails open: on any parsing problem the command passes. It reads
the command line only; a command assembled inside a program is not seen.
"""
import json
import os
import re
import shlex
import sys

WRAPPERS = {"command", "exec", "nohup", "time", "sudo", "nice", "caffeinate", "builtin"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
SSH_OPTS_WITH_ARG = set("-o -p -i -l -F -J -E -b -c -D -L -R -W -S -O -Q -w -B -I -m -e".split())
HERDR_GLOBAL_WITH_ARG = {"--session", "--machine", "--remote", "--remote-keybindings"}
SAFE_FLAGS = {"--version", "-V", "--help", "-h", "--skill", "--default-config"}
BYPASS = re.compile(r"(^--dangerously|bypassPermissions|^--yolo$|danger-full-access)")
SEP = {";", "&&", "||", "|", "&", "\n", "(", ")", "|&", ";;"}
# Commands that type into, start in or close their target: aimed at this session's own pane, tab or workspace
# they would hijack or kill the run. Reads, waits and `pane split --current` are not here.
SELF_TARGETED = {("pane", "run"), ("pane", "send-text"), ("pane", "send-keys"), ("pane", "input"),
                 ("pane", "close"), ("agent", "prompt"), ("agent", "send-keys"), ("agent", "start"),
                 ("tab", "close"), ("workspace", "close"), ("worktree", "remove")}
OWN_ENV = (("pane", "HERDR_PANE_ID"), ("tab", "HERDR_TAB_ID"), ("workspace", "HERDR_WORKSPACE_ID"))


def strip_heredocs(s):
    out, lines, i = [], s.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        tags = re.findall(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", line)
        i += 1
        for _, tag in tags:
            while i < len(lines) and lines[i].strip() != tag:
                i += 1
            i += 1  # skip the closing tag line
            out.append(tag)
    return "\n".join(out)


def split_commands(s):
    lx = shlex.shlex(s, posix=True, punctuation_chars=";&|()\n")
    lx.whitespace = " \t\r"
    lx.whitespace_split = True
    cmds, cur = [], []
    for tok in lx:
        if tok in SEP or set(tok) <= set(";&|()\n"):
            if cur:
                cmds.append(cur)
            cur = []
        else:
            cur.append(tok)
    if cur:
        cmds.append(cur)
    return cmds


def substitutions(tok):
    found, i = [], 0
    while True:
        j = tok.find("$(", i)
        if j < 0:
            return found
        depth, k = 1, j + 2
        while k < len(tok) and depth:
            depth += {"(": 1, ")": -1}.get(tok[k], 0)
            k += 1
        found.append(tok[j + 2:k - 1])
        i = k


def flag_value(tail, flag):
    for k, a in enumerate(tail):
        if a == flag and k + 1 < len(tail):
            return tail[k + 1]
        if a.startswith(flag + "="):
            return a.split("=", 1)[1]
    return ""


def own_target(group, sub, tail):
    """Name what this command aims at when it is the session's own pane, tab or workspace (or --current)."""
    if (group, sub) not in SELF_TARGETED:
        return ""
    if "--current" in tail:
        return "this session's own pane (--current)"
    if (group, sub) == ("agent", "start"):
        target = flag_value(tail, "--pane")
    elif (group, sub) == ("worktree", "remove"):
        target = flag_value(tail, "--workspace")
    else:
        target = tail[0] if tail and not tail[0].startswith("-") else ""
    for what, env in OWN_ENV:
        # the hook sees the command before the shell expands it, so `$HERDR_TAB_ID` is the usual spelling
        if target and (target == os.environ.get(env) or target.startswith(("$" + env, "${" + env))):
            return f"this session's own {what} {target}"
    return ""


def judge_herdr(args):
    i = 0
    scoped = False  # --machine or --session: IDs belong to another server, the session's own IDs do not apply
    while i < len(args) and args[i].startswith("-"):
        a = args[i]
        if a in SAFE_FLAGS:
            return None
        if a == "--remote" or a.startswith("--remote="):
            return "herdr --remote attaches an interactive client and hangs the tool"
        scoped = scoped or a.split("=")[0] in {"--machine", "--session"}
        i += 2 if a in HERDR_GLOBAL_WITH_ARG else 1
    rest = args[i:]
    if not rest:
        return "bare herdr launches or attaches the interactive TUI and hangs the tool"
    group, sub = rest[0], (rest[1] if len(rest) > 1 else "")
    tail = rest[2:]
    if group == "server":
        return f"herdr server {sub}".strip() + " controls the herdr server and every pane in it"
    if group == "update":
        return "herdr update replaces the binary under running sessions"
    if (group, sub) == ("config", "reset-keys"):
        return "herdr config reset-keys rewrites the user's keybindings"
    if (group, sub) == ("channel", "set"):
        return "herdr channel set changes the update channel"
    if group == "machine" and sub in {"add", "remove", "enable", "disable", "reconnect"}:
        return f"herdr machine {sub} changes saved machines (reconnect needs the user's SSH login)"
    if group == "session" and sub in {"stop", "delete", "attach"}:
        return f"herdr session {sub} stops, deletes or attaches a persistent session"
    if (group, sub) == ("agent", "attach") or (group == "terminal" and sub in {"attach", "session"}):
        return f"herdr {group} {sub} opens an interactive client and hangs the tool"
    own = "" if scoped else own_target(group, sub, tail)
    if own:
        return (f"herdr {group} {sub} aims at {own}; prompting, typing into or closing the pane "
                "this session runs in would hijack or end the run")
    if (group, sub) == ("worktree", "remove") and "--force" in tail:
        return "worktree remove --force deletes uncommitted work; that decision is the user's"
    if (group, sub) == ("workspace", "close") and "--group" in tail:
        return "workspace close --group closes every linked worktree workspace and its agents"
    if group == "pane" and sub in {"run", "send-text"} and len(tail) > 1:
        r = judge_text(" ".join(tail[1:]), 1)
        if r:
            return f"text typed into a pane would run: {r}"
    if (group, sub) == ("agent", "start") and "--" in tail:
        agent_args = tail[tail.index("--") + 1:]
        for k, a in enumerate(agent_args):
            nxt = agent_args[k + 1] if k + 1 < len(agent_args) else ""
            if BYPASS.search(a) or (a == "--permission-mode" and nxt == "bypassPermissions"):
                return f"agent argument {a} {nxt if a == '--permission-mode' else ''}".strip() + \
                       " bypasses the agent's approvals; that is the user's choice"
    return None


def judge(cmd, depth=0):
    if depth > 4 or not cmd:
        return None
    for tok in cmd:
        for inner in substitutions(tok):
            r = judge_text(inner, depth + 1)
            if r:
                return r
    i = 0
    while i < len(cmd) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", cmd[i]):
        i += 1
    while i < len(cmd):
        exe = os.path.basename(cmd[i])
        if exe in {"command", "builtin"} and any(re.match(r"^-[pPvV]*[vV][pPvV]*$", a) for a in cmd[i + 1:i + 3]):
            return None  # `command -v herdr` looks a command up; it runs nothing
        if exe in WRAPPERS:
            i += 1
            while i < len(cmd) and cmd[i].startswith("-"):
                i += 1
        elif exe == "env":
            i += 1
            while i < len(cmd) and (cmd[i].startswith("-") or "=" in cmd[i]):
                i += 1
        elif exe == "timeout":
            i += 1
            while i < len(cmd) and cmd[i].startswith("-"):
                i += 1
            i += 1  # duration
        else:
            break
    if i >= len(cmd):
        return None
    exe, args = os.path.basename(cmd[i]), cmd[i + 1:]
    if exe == "herdr":
        return judge_herdr(args)
    if exe in {"pkill", "killall"} and any("herdr" in a for a in args):
        return f"{exe} herdr kills the herdr server or other sessions' waiters"
    if exe in SHELLS and "-c" in args:
        k = args.index("-c")
        return judge_text(args[k + 1], depth + 1) if k + 1 < len(args) else None
    if exe == "ssh":
        k = 0
        while k < len(args) and args[k].startswith("-"):
            k += 2 if args[k] in SSH_OPTS_WITH_ARG else 1
        remote = args[k + 1:]
        return judge_text(" ".join(remote), depth + 1) if remote else None
    return None


ALLOW = []


def judge_text(text, depth=0):
    for cmd in split_commands(strip_heredocs(text)):
        flat = " ".join(cmd)
        if any(flat.startswith(p) for p in ALLOW):
            continue
        r = judge(cmd, depth)
        if r:
            return r
    return None


def load_allow():
    path = os.path.expanduser("~/.config/herdr-conductor/config.md")
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return []
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return []
    prefixes, inside = [], False
    for line in m.group(1).splitlines():
        if re.match(r"^guard_allow:\s*$", line):
            inside = True
            continue
        if inside:
            item = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if item:
                prefixes.append(item.group(1).strip("'\""))
            elif line.strip() and not line.startswith(" "):
                inside = False
    return [" ".join(p.split()) for p in prefixes if p.strip()]


def main():
    try:
        data = json.load(sys.stdin)
        command = data.get("tool_input", {}).get("command", "")
        if not isinstance(command, str) or not re.search(r"herdr|pkill|killall", command):
            return
        ALLOW.extend(load_allow())
        reason = judge_text(command)
    except Exception:
        return  # fail open
    if not reason:
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            f"herdr-conductor guard: {reason}. This denial is final for the run: do not reach the same "
            "effect through a script file, python -c, another shell or a pane. Tell the user; if they "
            "really want it, they run it themselves with `! <command>`, or add a guard_allow prefix in "
            "~/.config/herdr-conductor/config.md."),
    }}))


if __name__ == "__main__":
    main()
