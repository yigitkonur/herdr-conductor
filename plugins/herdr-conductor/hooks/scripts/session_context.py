#!/usr/bin/env python3
"""SessionStart hook for herdr-conductor: one short context line, only when it matters.

Speaks when herdr is installed and either this session runs inside a herdr pane or
the working directory maps to a herdr-conductor session directory. Local commands
only, each capped at 2 s; never ssh or --machine.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

STATE = os.path.expanduser("~/.local/state/herdr-conductor/projects.tsv")
CONFIG = os.path.expanduser("~/.config/herdr-conductor/config.md")
CODEX = "--host=codex" in sys.argv


def run(cmd, cwd=None):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=2, cwd=cwd)
        return p.stdout.strip() if p.returncode == 0 else ""
    except Exception:
        return ""


def frontmatter(path):
    try:
        m = re.match(r"^---\n(.*?)\n---", open(path, encoding="utf-8").read(), re.S)
    except OSError:
        return ""
    return m.group(1) if m else ""


def field(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.*?)[ \t]*$", fm, re.M)
    return m.group(1).strip("'\"") if m else ""


def norm(url):
    url = re.sub(r"^(https?://|ssh://|git@)", "", url.strip())
    url = re.sub(r"\.git$", "", url).replace(":", "/", 1) if "://" not in url else url
    return url.rstrip("/")


def repo_key(cwd):
    url = run(["git", "remote", "get-url", "origin"], cwd)
    if url:
        return norm(url)
    common = run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd)
    return common or ""


def is_card(path, key):
    """A CONDUCTOR.md counts only with a `repos:` block, and when it lists keys, one must be this repository's."""
    fm = frontmatter(path)
    if not re.search(r"^repos:", fm, re.M):
        return False
    keys = [norm(k) for k in re.findall(r"key:[ \t]*(\S+)", fm)]
    return not (keys and key and norm(key) not in keys)


def session_dir(cwd, key):
    root = run(["git", "rev-parse", "--show-toplevel"], cwd)
    common = run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd)
    main = os.path.dirname(common) if os.path.basename(common) == ".git" else ""  # a linked worktree's main checkout
    projects_root = os.path.expanduser(field(frontmatter(CONFIG), "projects_root") or "")
    stop = {os.path.expanduser("~"), "/", projects_root.rstrip("/")}
    d = cwd
    while True:
        card = os.path.join(d, "CONDUCTOR.md")
        if os.path.isfile(card) and is_card(card, key):
            return d
        side = os.path.join(d, ".herdr-conductor", "CONDUCTOR.md")
        if os.path.isfile(side) and is_card(side, key):
            return os.path.dirname(side)
        if (root and os.path.samefile(d, root)) or d in stop or os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    if main:
        side = os.path.join(main, ".herdr-conductor", "CONDUCTOR.md")
        if os.path.isfile(side) and is_card(side, key):
            return os.path.dirname(side)
    if key and os.path.isfile(STATE):
        for line in open(STATE, encoding="utf-8"):
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2 and parts[0] == key and os.path.isfile(os.path.join(parts[1], "CONDUCTOR.md")):
                return parts[1]
    return ""


def open_run(sdir):
    runs = os.path.join(sdir, "runs")
    best = None
    if os.path.isdir(runs):
        for name in os.listdir(runs):
            led = os.path.join(runs, name, "ledger.md")
            if os.path.isfile(led):
                head = open(led, encoding="utf-8").read(4000)
                if re.search(r"status:\s*open", head):
                    mt = os.path.getmtime(led)
                    if not best or mt > best[1]:
                        best = (led, mt, head)
    return best


def waiters(ledger_text):
    m = re.search(r"^## Waiters\n(.*?)(?=^## |\Z)", ledger_text, re.M | re.S)
    return [l.strip() for l in (m.group(1).splitlines() if m else []) if l.strip()][:8]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    if not shutil.which("herdr"):
        return
    source = data.get("source", "startup")
    sid = data.get("session_id", "")
    cwd = data.get("cwd") or os.getcwd()
    inside = os.environ.get("HERDR_ENV") == "1"
    key = repo_key(cwd)
    sdir = session_dir(cwd, key)
    if not inside and not sdir:
        return

    parts = []
    ver = run(["herdr", "--version"]).replace("herdr ", "")
    srv = run(["herdr", "status", "server", "--json"])
    try:
        s = json.loads(srv)
        parts.append(f"herdr {ver} (server {s.get('version')}, protocol {s.get('protocol')}, "
                     f"{'running' if s.get('running') else 'not running'}"
                     f"{'' if s.get('compatible', True) else ', INCOMPATIBLE'})")
    except Exception:
        parts.append(f"herdr {ver} (server not reachable)")
    if inside:
        parts.append(f"this session runs inside herdr pane {os.environ.get('HERDR_PANE_ID', '?')} "
                     "(never prompt, key or close it)")
    else:
        parts.append("this session runs outside herdr (no caller pane; explicit IDs, never --current)")
    if sid:
        parts.append(f"session id {sid}")
    if sdir:
        fm = frontmatter(os.path.join(sdir, "CONDUCTOR.md"))
        parts.append(f"session dir {sdir} (autonomy {field(fm, 'autonomy') or 'default'})")
        run_ = open_run(sdir)
        if run_:
            led, mt, head = run_
            age = int((time.time() - mt) / 60)
            owner = field(head, "owner_session")
            if owner in ("unknown", "none", "-"):
                owner = ""
            mine = bool(owner) and owner == sid
            w = waiters(open(led, encoding="utf-8").read())
            if CODEX and (mine or not owner):
                parts.append(f"open run {led} (last written {age} min ago); Codex has no background waiters: "
                             "for each Waiter run `herdr agent get <name>`, compare completion_seq, read the "
                             "screen, then wait in the foreground with a timeout. Waiters: " + (" | ".join(w) or "none"))
            elif source == "resume" and (mine or not owner):
                parts.append(f"open run {led} (last written {age} min ago); background waiters did not "
                             "survive: for each Waiter run `herdr agent get <name>`, compare completion_seq, "
                             "read the screen, then re-arm. Waiters: " + (" | ".join(w) or "none"))
            elif source == "compact" and (mine or not owner):
                parts.append(f"open run {led} (last written {age} min ago); this process lives on, so background "
                             "waiters armed before the compaction usually still run: do not re-arm them. A "
                             "notification whose completion_seq is not above the ledger's is a duplicate. An agent "
                             "that settled with no notification is a lost waiter: `herdr agent get <name>`, "
                             "read the screen, then re-arm. Waiters: " + (" | ".join(w) or "none"))
            else:
                parts.append(f"open run {led} owned by {'another session' if owner and not mine else 'an unknown session'} "
                             f"(last written {age} min ago); adopt it only after checking no live session drives it")
    ctx = "herdr-conductor: " + "; ".join(parts) + "."
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}}))


if __name__ == "__main__":
    main()
