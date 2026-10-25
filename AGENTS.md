# Maintainer notes (herdr-conductor)

Claude Code and Codex plugin `herdr-conductor` (marketplace `herdr-conductor`, plugin in `plugins/herdr-conductor`). It teaches an agent to drive herdr (workspaces, tabs, panes, worktrees and the coding agents in them): one skill, a worker agent, a guard hook and a session-start hook. The Codex side is `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`; the skill and hooks are shared.

## Layout
- `plugins/herdr-conductor/skills/herdr` : the skill and its `references/`; `plugins/herdr-conductor/agents/herdr-worker.md` is the worker agent; `hooks/` holds the guard and the session-start line; `bin/` has `herdr-snapshot`.
- `scripts/hc` : a small Claude-only per-project switch for checkouts. Not part of the plugin.
- `tools/lint.py` : checks every herdr command and flag in the docs against the installed CLI, regression rules, links, the coverage map and a leak scan (`tools/leak-private.txt` is gitignored). Only `--help` and `completion zsh` ever run.
- `tests/guard_check.py` : feeds synthetic commands to the guard hook. Nothing runs herdr.
- `tests/CASES.md`, `docs/COVERAGE.md` : evidence documents (what was run live, what the original skill covered). Keep them factual; do not rewrite history in them.

## Local checks
- `python3 -I tools/lint.py` and `python3 -I tests/guard_check.py` (a herdr on the PATH is needed for lint).
- `cd plugins/herdr-conductor && claude plugin eval . --trust-plugin --no-publish` runs the eval suite (the sandbox has no herdr socket).
- No secrets, tokens, account ids or personal paths in this repo. Commit under the GitHub noreply identity.

<!-- kit:agents:start -->
## Releases, versions and installs (shared by every plugin repo)

- **Never bump a version by hand.** `.github/workflows/release.yml` runs after `ci` is green on `main`. `scripts/kit/release.py` reads the conventional-commit subjects since the last release tag (`feat` is a minor, `fix`/`perf`/unprefixed a patch, `type!:` or a BREAKING CHANGE line a major, a minor while the version is 0.x; docs, ci, chore, test, style, build and refactor release nothing) and counts only commits that touch shipped files. It writes every manifest, the marketplace entries and CHANGELOG.md, commits `chore(release): vX [skip ci]`, tags `vX` and `<plugin>--vX` (several plugins: `<plugin>--vX` only) and publishes the GitHub release. `python3 scripts/kit/release.py` with no flags prints what it would do; Actions > release > Run workflow forces a level or a dry run.
- **One version source: the manifests** (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, the marketplace entry). Never a constant in code; read the manifest at runtime.
- Installed copies update only when the version string changes, so a change users should get must reach `main` as a releasing commit type (`feat`, `fix`, `perf`, or `!`).
- **Install policy:** installed globally and off (`"defaultEnabled": false`), switched on per project with `plugin on <name>`. Never document a project-scope install as the way in.
- `scripts/kit/*`, `scripts/kit.sha256`, `.github/workflows/release.yml`, the `kit:manifests` job in `ci.yml` and the blocks between `kit:` markers in README.md and AGENTS.md are copies from [yigitkonur/plugin-kit](https://github.com/yigitkonur/plugin-kit). Change them there and run its `sync.sh`; `scripts/kit/check-manifests.py` fails CI on a local edit.
- Before pushing: `python3 scripts/kit/check-manifests.py --validate`, `python3 scripts/kit/secret-scan.py --tree`, `python3 scripts/kit/check-links.py`, then this repo's own checks.
<!-- kit:agents:end -->
