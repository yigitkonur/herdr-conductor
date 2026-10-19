---
name: setup
description: Check that herdr and the harnesses are ready for herdr-conductor (a doctor), and create or update the user config and this project's CONDUCTOR.md card. Invoked as /herdr-conductor:setup [doctor|config|project].
argument-hint: "[doctor|config|project]"
disable-model-invocation: true
allowed-tools: Bash(herdr *), Bash(herdr-snapshot *), Bash(git rev-parse *), Bash(git remote *), Bash(command -v *), Bash(printenv *), Read, Write, Edit
---

# herdr-conductor setup

Argument: $ARGUMENTS (empty means all three parts, in order).

## doctor (read-only)

Run each check once and print one line per check: ok, warn or fail, with the evidence.

1. `command -v herdr`, `herdr --version`, `herdr status client --json`, `herdr status server --json` (running, `compatible`, version and protocol of each; a client newer than the server is a warn, and so is any herdr older than 0.9.5, which this plugin's text was written for).
2. `herdr config check`.
3. `herdr integration status`: list the outdated ones. Never install on your own; offer the user `herdr integration install <agent>` for each (it rewrites that harness's hook config) and run it only after a yes.
4. `herdr machine list --json`, then `herdr machine status --json` (checks without prompting for authentication). A machine that needs a login: the user runs `herdr machine reconnect <label>` themselves.
5. Harnesses: `command -v` for claude, codex, agy and any harness the user config routes to. Do not run them: a machine's `agy` may be a wrapper that switches accounts on every launch. A harness that exists only as a shell function or alias (claude often does, inside an agent's shell) is fine: report it as found, not as a warning.
6. `printenv HERDR_ENV HERDR_PANE_ID` (inside or outside herdr), `command -v python3` (the hooks and `herdr-snapshot` need it), `command -v herdr-snapshot` (the plugin's `bin/` on PATH).
7. `~/.config/herdr-conductor/config.md` present or not; a CONDUCTOR.md for this repository (references/ledger.md, finding the session directory).

## config

Create or update `~/.config/herdr-conductor/config.md` from `${CLAUDE_PLUGIN_ROOT}/assets/templates/config.md`. Ask with AskUserQuestion, recommendation first: `projects_root` (offer "none: keep projects in the repo" and any existing orchestration folder found under the home directory), `default_autonomy` (L2 recommended), `notify`, `research`, and the routing per role (offer the harnesses found in the doctor). `guard_allow` stays empty unless the user names prefixes. Show the final file before writing it; keep existing values the user did not change.

## project

Resolve the session directory for the current repository (`${CLAUDE_PLUGIN_ROOT}/skills/herdr/references/ledger.md`); create it if none exists (never at `~`, `/` or `projects_root` itself). Fill CONDUCTOR.md from `${CLAUDE_PLUGIN_ROOT}/assets/templates/CONDUCTOR.md`: find the facts yourself (remote URL, default branch, test and build commands from the repository's own docs and scripts) and ask only the decisions: autonomy, pre-authorized actions, escalate-always items, standing answers. Add the repository key and session directory to `~/.local/state/herdr-conductor/projects.tsv` when the directory is outside the repository; add `.herdr-conductor/` to the repository's exclude file (`git rev-parse --git-path info/exclude`) when it is inside. Inside means the main checkout, never a linked worktree (ledger.md). Decisions to ask also include `max_parallel` and `pr` (draft or ready).
