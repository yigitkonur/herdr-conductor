#!/usr/bin/env python3
"""Compact view of one herdr server: one row per agent (or per pane with --panes).

usage: snapshot.py [--machine LABEL] [--json] [--panes] [--workspace ID]

Runs `herdr [--machine LABEL] api snapshot` once (read-only) and joins agents to
their workspace and tab labels. Exit 1 with herdr's error on stderr if the call fails.
"""
import argparse
import json
import os
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--machine", help="saved machine label (herdr --machine)")
    ap.add_argument("--json", action="store_true", help="print rows as JSON")
    ap.add_argument("--panes", action="store_true", help="one row per pane, agents or not")
    ap.add_argument("--workspace", help="only this workspace id")
    a = ap.parse_args()

    cmd = ["herdr"] + (["--machine", a.machine] if a.machine else []) + ["api", "snapshot"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        sys.exit("herdr not found on PATH")
    except subprocess.TimeoutExpired:
        sys.exit("herdr api snapshot timed out after 60 s")
    if p.returncode != 0:
        sys.stderr.write(p.stderr or p.stdout)
        sys.exit(1)
    snap = json.loads(p.stdout)["result"]["snapshot"]

    ws = {w["workspace_id"]: w for w in snap.get("workspaces", [])}
    tabs = {t["tab_id"]: t for t in snap.get("tabs", [])}
    items = snap.get("panes", []) if a.panes else snap.get("agents", [])
    home = os.path.expanduser("~")
    rows = []
    for x in items:
        if a.workspace and x.get("workspace_id") != a.workspace:
            continue
        w = ws.get(x.get("workspace_id"), {})
        t = tabs.get(x.get("tab_id"), {})
        cwd = x.get("cwd") or ""
        if not a.machine and cwd.startswith(home):
            cwd = "~" + cwd[len(home):]
        rows.append({
            "server": a.machine or "local",
            "workspace": f'{x.get("workspace_id")} {w.get("label", "")}'.strip(),
            "tab": f'{x.get("tab_id")} {t.get("label", "")}'.strip(),
            "pane": x.get("pane_id"),
            "name": x.get("name", ""),
            "agent": x.get("agent") or "-",
            "status": x.get("agent_status", ""),
            "completion_seq": x.get("completion_seq", ""),
            "state_change_seq": x.get("state_change_seq", ""),
            "focused": "*" if x.get("pane_id") == snap.get("focused_pane_id") else "",
            "cwd": cwd,
        })

    if a.json:
        print(json.dumps({"version": snap.get("version"), "protocol": snap.get("protocol"),
                          "focused_pane_id": snap.get("focused_pane_id"), "rows": rows}, indent=1))
        return
    print(f'{a.machine or "local"}: herdr {snap.get("version")} protocol {snap.get("protocol")}, '
          f'{len(ws)} workspaces, {len(tabs)} tabs, {len(snap.get("panes", []))} panes, '
          f'{len(snap.get("agents", []))} agents; user focus {snap.get("focused_pane_id")} (*)')
    cols = ["workspace", "tab", "pane", "name", "agent", "status", "completion_seq", "focused", "cwd"]
    head = {"completion_seq": "seq", "focused": "f"}
    width = {c: max([len(head.get(c, c))] + [len(str(r[c])) for r in rows]) for c in cols}
    print("  ".join(head.get(c, c).ljust(width[c]) for c in cols))
    for r in rows:
        print("  ".join(str(r[c]).ljust(width[c]) for c in cols).rstrip())


if __name__ == "__main__":
    main()
