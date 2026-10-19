# herdr-conductor

A Claude Code plugin marketplace with one plugin, [`herdr-conductor`](plugins/herdr-conductor/README.md): conduct coding agents in [herdr](https://herdr.dev) from Claude Code. Discover what runs where, start claude, codex, agy and other harnesses in herdr panes, brief them, wait in the background, answer their dialogs, verify on the machine, review across harnesses, run parallel writers in worktrees, and drive saved SSH machines.

```text
/plugin marketplace add yigitkonur/herdr-conductor
/plugin install herdr-conductor@herdr-conductor
```

## Repository layout

| path | what |
| --- | --- |
| `plugins/herdr-conductor/` | the plugin (skills, agent, hooks, scripts, templates) |
| `tools/lint.py` | static checks against the installed herdr CLI: drift, regression rules, Trace, coverage, leaks, hygiene |
| `tests/CASES.md` | live cases: what was run against herdr, what came back, where each finding is stated, retest triggers |
| `docs/COVERAGE.md` | where every item of the source skill went |

Run `python3 -I tools/lint.py` after any change (needs `herdr` on PATH; only `--help` and `completion zsh` run). MIT licensed.
