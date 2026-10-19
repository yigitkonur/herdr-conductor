#!/usr/bin/env python3
"""Static checks for the herdr-conductor plugin.

1. DRIFT: every herdr command, flag and enumerated value shown in a code span of a
   plugin file exists in the installed CLI (`herdr completion zsh` for the tree,
   `<path> --help` for flags and value sets). Only --help and completion run.
2. COVER: every `agent` subcommand and every read `--source` value is shown.
3. Regression rules R1-R9: contradictions found once must not come back.
4. TRACE: every case in tests/CASES.md has a Trace line, and every Trace phrase
   still stands in the plugin file it names.
5. COVERAGE: every row of docs/COVERAGE.md names an existing plugin file, or says
   `merged` or `cut` with a reason.
6. LEAK: no personal setup or fixed model names in plugin files.
7. Hygiene: SKILL.md under 500 lines, relative links and references/*.md mentions
   resolve, no code span wraps onto the next line, skill frontmatter is sane.

usage: python3 -I tools/lint.py            # checks, exit 1 on any FAIL
       python3 -I tools/lint.py --tree [group ...]   # leaves with their flags
"""
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = REPO / "plugins" / "herdr-conductor"
SKILL = PLUGIN / "skills" / "herdr" / "SKILL.md"
FILES = sorted(str(p.relative_to(PLUGIN)) for p in PLUGIN.rglob("*.md"))
CASES = REPO / "tests" / "CASES.md"
COVERAGE = REPO / "docs" / "COVERAGE.md"
DENY_FIRST = {"update", "server", "terminal", "completion", "completions"}
DENY_ANY = {"attach", "observe", "control"}
DENY_PATHS = {("config", "reset-keys"), ("channel", "set"), ("machine", "reconnect"),
              ("plugin", "install"), ("plugin", "run"), ("session", "stop"),
              ("session", "delete")}
GLOBAL = {"--session", "--machine", "--remote", "--remote-keybindings", "--help",
          "--handoff", "--default-config", "--skill", "--version"}
HIDDEN = {(("workspace", "close"), "--group")}  # accepted although --help omits it
NUM = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
_extra = REPO / "tools" / "leak-private.txt"  # untracked: your own machine and tool names, one regex per line
_private = [l.strip() for l in _extra.read_text().splitlines() if l.strip() and not l.startswith("#")] if _extra.is_file() else []
LEAK = re.compile(r"\b(raycast|elicitation|gpt-\d|gemini-\d|opus|sonnet|haiku|fable)\b|/Users/[A-Za-z]+/"
                  + "".join("|" + x for x in _private), re.I)
LEAK_OK = {"README.md": {"yigit"}, "docs/COVERAGE.md": {"raycast"}}  # author credit; the source skill's file names
fails, warns = [], []


def herdr(*args):
    p = subprocess.run(["herdr", *args], capture_output=True, text=True, timeout=20)
    return p.stdout + p.stderr


def denied(p):
    return p[0] in DENY_FIRST or any(x in DENY_ANY for x in p) or p[:2] in DENY_PATHS


def build_tree():
    comp = herdr("completion", "zsh")
    funcs = {}
    for m in re.finditer(r"^(_herdr\S*?)_commands\(\) \{\n(.*?)^\}", comp, re.S | re.M):
        funcs[m.group(1).replace("-", "_")] = re.findall(r"^'([a-z][a-z0-9-]*):", m.group(2), re.M)
    node = {}

    def walk(p):
        key = "_herdr" + "".join("__subcmd__" + x for x in p)
        node[p] = [n for n in funcs.get(key.replace("-", "_"), []) if n != "help"]
        for n in node[p]:
            walk(p + (n,))
    walk(())
    flags, values = {}, {}
    for p in node:
        if not p or denied(p):
            continue
        fl, last = set(), None
        for line in herdr(*p, "--help").splitlines():
            m = re.match(r"\s{2,}(?:-[A-Za-z], )?(--[a-z0-9][a-z0-9-]*)", line)
            if m:
                last = m.group(1)
                fl.add(last)
            v = re.search(r"\[possible values: ([^\]]+)\]", line)
            if v and last:
                values[(p, last)] = {x.strip() for x in v.group(1).split(",")}
        flags[p] = fl
    return node, flags, values


def code_spans(text):
    fenced = False
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            yield i, line
            continue
        for m in re.finditer(r"`([^`]+)`", line):
            yield i, m.group(1)


def commands(code, roots):
    code = re.sub(r"\[--machine [^\]]*\]", " ", code).split(" #")[0]
    for seg in re.split(r"&&|;|\|\||\$\(", code):
        toks = [t.strip("[](),\"'") for t in seg.split()]
        toks = [t for t in toks if t]
        if "herdr" in toks:
            toks = toks[toks.index("herdr") + 1:]
        elif toks and toks[0].endswith("/herdr"):
            toks = toks[1:]
        while len(toks) > 1 and toks[0] in ("--machine", "--session"):
            toks = toks[2:]
        if toks and toks[0] in roots:
            yield toks


def sentences(text):
    para, start = [], None
    lines = text.splitlines() + [""]
    for i, line in enumerate(lines, 1):
        item = re.match(r"\s*([-*]|\d+\.)\s", line)
        if line.strip() == "" or line.lstrip().startswith(("```", "#", "|")) or (item and para):
            if para:
                joined = " ".join(x.strip() for x in para)
                for s in re.split(r"(?<=[.!?])\s+(?=[A-Z`*(\"])", joined):
                    yield start, s
            para, start = [], None
            if line.lstrip().startswith("|"):
                yield i, line
                continue
        if line.strip() and not line.lstrip().startswith(("```", "#", "|")):
            if start is None:
                start = i
            para.append(line)


def section(text, title):
    m = re.search(rf"^## {title}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else ""


def flat(s):
    return " ".join(s.split())


def drift(f, text, node, flags, values, roots, mentioned):
    words = set()
    for i, code in code_spans(text):
        words.update(re.findall(r"[a-z][a-z-]*", code))
        for toks in commands(code, roots):
            p, rest = (), toks
            while rest and rest[0] in node.get(p, []):
                p, rest = p + (rest[0],), rest[1:]
            mentioned.add(p)
            if node.get(p) and rest and re.fullmatch(r"[a-z][a-z0-9-]*", rest[0]):
                fails.append(f"DRIFT {f}:{i} unknown subcommand: {' '.join(p + (rest[0],))}")
            known = flags.get(p)
            for j, t in enumerate(rest):
                if t == "--":
                    break
                for alt in t.split("|"):
                    alt = alt.split("=")[0]
                    if not re.fullmatch(r"--[a-z][a-z0-9-]*", alt):
                        continue
                    if known is not None and alt not in known | GLOBAL and (p, alt) not in HIDDEN:
                        fails.append(f"DRIFT {f}:{i} {' '.join(p)}: no flag {alt}")
                    nxt = rest[j + 1] if j + 1 < len(rest) else ""
                    if (p, alt) in values and re.fullmatch(r"[a-z][a-z|-]*", nxt):
                        for val in nxt.split("|"):
                            if val not in values[(p, alt)]:
                                fails.append(f"DRIFT {f}:{i} {' '.join(p)} {alt}: no value {val}")
    return words


def hygiene(f, text, base):
    fenced = False
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced and line.count("`") % 2:
            fails.append(f"SPAN {f}:{i} a code span wraps onto the next line, out of lint's sight")
        for m in re.finditer(r"\]\(([^)#\s]+)", line):
            if not m.group(1).startswith("http") and not ((base / f).parent / m.group(1)).exists():
                fails.append(f"LINK {f}:{i} {m.group(1)}")
        for m in re.finditer(r"references/([a-z-]+\.md)", line):
            if not (PLUGIN / "skills" / "herdr" / "references" / m.group(1)).is_file():
                fails.append(f"REF {f}:{i} references/{m.group(1)} does not exist")
        for m in re.finditer(r"\b(harness-[a-z]+\.md|dialogs\.md|waiting\.md|states\.md|cli\.md|"
                             r"briefs\.md|ledger\.md|autonomy\.md|scenarios\.md|worktrees\.md|"
                             r"machines\.md)", line):
            if not (PLUGIN / "skills" / "herdr" / "references" / m.group(1)).is_file():
                fails.append(f"REF {f}:{i} {m.group(1)} does not exist")


def leak(f, text):
    ok = LEAK_OK.get(f, set())
    for i, line in enumerate(text.splitlines(), 1):
        for m in LEAK.finditer(line):
            if m.group(0).lower() not in ok:
                fails.append(f"LEAK {f}:{i} {m.group(0)!r}: personal setup or a fixed model name")


def front():
    for sk in sorted((PLUGIN / "skills").glob("*/SKILL.md")):
        text = sk.read_text()
        m = re.match(r"---\n(.*?)\n---\n", text, re.S)
        keys = dict(re.findall(r"^([a-z-]+): *(.*)$", m.group(1), re.M)) if m else {}
        rel = sk.relative_to(PLUGIN)
        if keys.get("name", "").strip('"') != sk.parent.name:
            fails.append(f"FRONT {rel} name {keys.get('name')!r} is not its folder {sk.parent.name!r}")
        if not keys.get("description"):
            fails.append(f"FRONT {rel} has no description")
    for ag in sorted((PLUGIN / "agents").glob("*.md")):
        m = re.match(r"---\n(.*?)\n---\n", ag.read_text(), re.S)
        keys = dict(re.findall(r"^([a-z-]+): *(.*)$", m.group(1), re.M)) if m else {}
        for k in ("name", "description", "model"):
            if k not in keys:
                fails.append(f"FRONT {ag.relative_to(PLUGIN)} has no {k}")


def rules(f, text, n_src, n_leaves, n_groups):
    for i, s in sentences(text):
        if re.search(r"\bstatus\b", s) and re.search(r"refus", s, re.I) \
                and not re.search(r"bare|status server", s, re.I):
            fails.append(f"R1 {f}:{i} 'status refused' without 'bare': {s[:90]}")
        if re.search(r"at once|immediately", s) and "settled" in s and not re.search(r"match", s):
            fails.append(f"R2 {f}:{i} 'settled returns at once' without the --until condition: {s[:90]}")
        m = re.search(r"\b(two|three|four|five|six|\d+) (?:read )?sources\b", s)
        if m and NUM.get(m.group(1), int(m.group(1)) if m.group(1).isdigit() else 0) != n_src:
            fails.append(f"R4 {f}:{i} says {m.group(1)} sources, help has {n_src}: {s[:90]}")
        m = re.search(r"(~?)(\d+) (?:leaf )?commands", s)
        if m and abs(int(m.group(2)) - n_leaves) > (3 if m.group(1) else 0):
            fails.append(f"R5 {f}:{i} says {m.group(0)}, completion tree has {n_leaves} leaves")
        m = re.search(r"\b(\d+) (?:command )?groups", s)
        if m and int(m.group(1)) != n_groups:
            fails.append(f"R5 {f}:{i} says {m.group(0)}, completion tree has {n_groups}")
        if "`timeout`" in s and "deliver" in s and not re.search(r"may or may not|whether|may have", s, re.I):
            fails.append(f"R6 {f}:{i} delivery after `timeout` stated as certain: {s[:90]}")
        if "leaves its transcript" in s and re.search(r"laude", s) and "fullscreen" not in s:
            fails.append(f"R8 {f}:{i} claude's transcript in scrollback without the fullscreen condition: {s[:90]}")
        if "turn ended" in s and re.search(r"completion_seq|Compare it", s) and "Herdr" not in s:
            fails.append(f"R9 {f}:{i} `completion_seq` taken as the work's end, not Herdr's count: {s[:90]}")
    paras = {}
    for i, s in sentences(text):
        paras[i] = paras.get(i, "") + " " + s
    for i, p in paras.items():
        if "grill" in p and "`blocked`" in p and "prose" not in p:
            fails.append(f"R7 {f}:{i} grilling's questions said to arrive as a `blocked` dialog")
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(r"MARK_\$\?|MARK_\[0-9\]", line) and "nonce" not in line.lower():
            fails.append(f"R3 {f}:{i} reusable marker without a per-run nonce")


def trace():
    if not CASES.is_file():
        fails.append("TRACE tests/CASES.md is missing")
        return 0, 0
    text = CASES.read_text()
    cases = re.findall(r"^\| ([TN]\d+) \|", section(text, "Cases"), re.M)
    rows = re.findall(r"^\| ([TN]\d+) \| ([^|]+?) \| (.+?) \|\s*$", section(text, "Trace"), re.M)
    traced = {r[0] for r in rows}
    for case in cases:
        if case not in traced:
            fails.append(f"TRACE {case} has no Trace line")
    for case, f, phrase in rows:
        path = PLUGIN / f
        if case not in cases:
            fails.append(f"TRACE {case} is not in the Cases table")
        elif not path.is_file():
            fails.append(f"TRACE {case} {f}: not a plugin file")
        elif flat(phrase.replace("\\|", "|")) not in flat(path.read_text()):
            fails.append(f"TRACE {case} {f}: phrase gone: {phrase}")
    return len(cases), len(rows)


def coverage():
    if not COVERAGE.is_file():
        fails.append("COVERAGE docs/COVERAGE.md is missing")
        return 0
    n = 0
    for i, line in enumerate(COVERAGE.read_text().splitlines(), 1):
        m = re.match(r"^\| (?!source|---)(.+?) \| (.+?) \| (.*?) \|\s*$", line)
        if not m:
            continue
        n += 1
        dest = m.group(2).strip()
        if dest.startswith(("cut", "merged")):
            if dest.startswith("cut") and len(m.group(3).strip()) < 8:
                fails.append(f"COVERAGE {i} cut without a reason: {m.group(1)}")
            continue
        for d in re.findall(r"`([^`]+)`", dest) or [dest]:
            if not (PLUGIN / d.split("#")[0]).exists() and not (REPO / d.split("#")[0]).exists():
                fails.append(f"COVERAGE {i} destination {d} does not exist ({m.group(1)})")
    return n


def main():
    node, flags, values = build_tree()
    roots = set(node[()])
    leaves = [p for p in node if p and not node[p] and p[0] != "completions"]
    groups = [p for p in node[()] if p != "completions"]
    if "--tree" in sys.argv:
        want = set(sys.argv[sys.argv.index("--tree") + 1:])
        for p in sorted(leaves):
            if not want or p[0] in want:
                vals = "; ".join(f"{f}={'|'.join(sorted(v))}" for (q, f), v in values.items() if q == p)
                print(" ".join(p), " ".join(sorted(flags.get(p, {"(not probed)"}))), vals)
        print(f"{len(groups)} groups, {len(leaves)} leaf commands")
        return 0
    n_src = len(values.get((("agent", "read"), "--source"), ()))
    mentioned, text_all, code_words = set(), "", set()
    for f in FILES:
        text = (PLUGIN / f).read_text()
        text_all += text
        code_words |= drift(f, text, node, flags, values, roots, mentioned)
        rules(f, text, n_src, len(leaves), len(groups))
        hygiene(f, text, PLUGIN)
        leak(f, text)
    for extra in ("tests/CASES.md", "docs/COVERAGE.md"):
        if (REPO / extra).is_file():
            leak(extra, (REPO / extra).read_text())
    n_cases, n_rows = trace()
    n_cov = coverage()
    for sub in node[("agent",)]:
        if ("agent", sub) not in mentioned:
            fails.append(f"COVER agent {sub} is never shown in a code span")
    for p in (("agent", "read"), ("pane", "read"), ("pane", "wait-output")):
        for v in sorted(values.get((p, "--source"), ())):
            if v not in code_words:
                fails.append(f"COVER {' '.join(p)} --source {v} never appears in code")
    for p in sorted(mentioned):
        unused = sorted(fl for fl in flags.get(p, set()) - GLOBAL - {"--json"} if fl not in text_all)
        if p and not node.get(p) and unused:
            warns.append(f"FLAGS {' '.join(p)}: not named anywhere: {' '.join(unused)}")
    front()
    n = len(SKILL.read_text().splitlines())
    if n >= 500:
        fails.append(f"SIZE SKILL.md has {n} lines (limit 500)")
    for w in warns:
        print("WARN", w)
    for x in fails:
        print("FAIL", x)
    print(f"{len(groups)} groups, {len(leaves)} leaves, {len(mentioned)} paths shown, {len(FILES)} files, "
          f"{n_cases} cases, {n_rows} trace lines, {n_cov} coverage rows, SKILL.md {n} lines: "
          f"{len(fails)} FAIL, {len(warns)} WARN")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
