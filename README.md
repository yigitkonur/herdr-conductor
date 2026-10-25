# herdr-conductor

run a whole squad of coding agents from one claude code session. herdr handles the panes, this plugin handles the thinking.

you tell claude what you want done. it spins up claude, codex, agy (or whatever herdr supports) in their own tabs, hands each one a small brief, waits for them in the background, answers their dialogs, checks the work on the machine, and gets it reviewed by a different agent than the one that wrote it. no babysitting, no "is it done yet" loops.

## why this exists

driving agents through a terminal multiplexer is weirder than it looks. `idle` does not mean finished. trust dialogs eat your prompt. a quota hit hides behind a perfectly green status. a wait that outlives its pane just hangs there. an agent's "done" is a claim, not a receipt.

this plugin is the scar tissue from running all of that for real, written down so claude stops rediscovering it the hard way every session.

<!-- kit:install:start -->
## install

Every plugin of ours is installed **once, globally, and off**, then **turned on per project**. Nothing runs and no tokens are spent in chats that don't switch it on. It works the same in Claude Code and Codex.

### 1. install it globally

**Claude Code**

```sh
claude plugin marketplace add yigitkonur/herdr-conductor
claude plugin install herdr-conductor@herdr-conductor -s user          # stays off: defaultEnabled is false in the manifest
```

**Codex** (0.163+)

```sh
codex plugin marketplace add yigitkonur/herdr-conductor
codex plugin add herdr-conductor@herdr-conductor
codex-plugin-project.sh global-off herdr-conductor@herdr-conductor     # Codex has no enable/disable command; this keeps it off everywhere
```

All our plugins, both hosts, plus the `plugin` command and the 6-hourly update job, in one line:

```sh
curl -fsSL https://raw.githubusercontent.com/yigitkonur/plugin-kit/main/install.sh | sh -s -- --all
```

### 2. turn it on in a project

```sh
cd your-project
plugin on herdr-conductor    # Claude Code and Codex, this folder only
plugin off herdr-conductor   # undo
plugin                       # or pick from a list (TUI)
```

By hand, without the `plugin` command:

```sh
claude plugin enable herdr-conductor@herdr-conductor --scope project      # undo: claude plugin disable herdr-conductor@herdr-conductor --scope project
codex-plugin-project.sh on herdr-conductor@herdr-conductor . --trust      # undo: codex-plugin-project.sh off herdr-conductor@herdr-conductor
```

Restart `claude` / `codex` in that folder afterwards.
Codex reads a folder's `.codex/config.toml` only when the folder is trusted; `--trust` adds that, and it also enables the folder's hooks and rules, so use it for your own projects only. `plugin` and `codex-plugin-project.sh` come from [plugin-kit](https://github.com/yigitkonur/plugin-kit) (the one-line installer above).

### 3. updates

A plugin updates only when its `version` changes, and this repo's `release` workflow bumps it on every shipped change. Machines pick it up with `plugin update`, or by themselves with the 6-hourly job (`plugin autoupdate install`). By hand:

```sh
claude plugin marketplace update herdr-conductor && claude plugin update herdr-conductor@herdr-conductor
codex plugin marketplace upgrade herdr-conductor        # then start a new session
```

No GitHub SSH key on the machine? `export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` (`plugin install` sets it in Claude's settings for you).

### 4. uninstall

```sh
claude plugin uninstall herdr-conductor@herdr-conductor -s user
claude plugin marketplace remove herdr-conductor
codex plugin remove herdr-conductor@herdr-conductor
codex plugin marketplace remove herdr-conductor
```
<!-- kit:install:end -->

### first run

then start claude (or run `/reload-plugins` in a session that's already open) in a project where you switched it on, and run this once:

```text
/herdr-conductor:setup
```

it's a doctor: checks herdr, the server, your integrations, saved machines and which harnesses are installed. read-only, it won't touch anything without asking.

check it worked:

```bash
claude plugin list
```

you want `herdr-conductor@herdr-conductor` listed with `Scope: user`, disabled in any folder where you haven't switched it on (that's the point: it costs nothing there). in a project where you ran `plugin on herdr-conductor`, inside claude ask "which herdr skills and agents do you have?". the answer is `herdr-conductor:herdr` and `herdr-conductor:herdr-worker`. inside a herdr pane there's also a one-line `herdr-conductor:` context at session start.

you need:

- herdr 0.9.5 or newer, on every machine you want to drive
- claude code 2.1.292 or newer (tested on 2.1.302 through 2.1.308)
- `python3` (the hooks and the snapshot helper use it)
- the harness clis you actually want to run (claude, codex, agy...), installed and logged in

works from inside a herdr pane or from a plain terminal outside herdr. it figures out which one it's in.

### why it stays off until you switch it on

the plugin adds about 550 tokens to every session while it's enabled, which is why the install above leaves it off and `plugin on herdr-conductor` enables it for one project. a project's `false` beats a user-scope install that's on, and a project's `true` beats one that's off; that's why this works. a fresh claude saw no herdr-conductor in a folder where it was off, and `plugin on` plus `/reload-plugins` took the reload from 5 plugins, 17 skills, 17 agents, 9 hooks to 6, 21, 18, 11 (this plugin's 4 skills, 1 agent and 2 hooks).

if the repo already tracks `.claude/settings.json`, the switch writes `.claude/settings.local.json` instead (claude gitignores it) so no tracked file gets dirty; by hand, use `--scope local` on the enable and disable lines. an untracked `.claude/settings.json` is added to `.git/info/exclude` so `git add -A` can't sweep it in.

this repo also carries `scripts/hc`, a small Claude-only switch (`hc on`, `hc off`, `hc status`, each taking an optional folder) for when you have a checkout and not the `plugin` command. it installs the plugin globally and off first if the machine doesn't have it. it lives outside the plugin on purpose: the plugin's own `bin/` isn't on your path while it's off.

just kicking the tires, one session only, nothing installed:

```bash
git clone https://github.com/yigitkonur/herdr-conductor
claude --plugin-dir ./herdr-conductor/plugins/herdr-conductor
```

### codex differences

the repo is also a codex marketplace (`.agents/plugins/marketplace.json`), and the same skills and hooks load there. what codex doesn't have: the `herdr-worker` subagent, background-task wake-ups, cron and `AskUserQuestion`. the skill has a short reference for that (`host-codex.md`), so codex waits in the foreground instead.

check with `codex plugin list` (`installed, enabled` inside the project, `installed, disabled` elsewhere). the first time (and after each plugin update), codex asks you to review the plugin's hooks: choose trust, and send your prompt again, because the one typed into that dialog is lost.

### on a saved machine

plugins live in each machine's own claude and codex config, so a remote box needs its own global install. over ssh it's the installer from the block above, then `plugin on herdr-conductor` in the project on that box:

```bash
ssh <target> 'curl -fsSL https://raw.githubusercontent.com/yigitkonur/plugin-kit/main/install.sh | sh -s -- --all'
```

the box needs herdr 0.9.5, `python3` and a route to github. a claude that was already running there has to restart to load the hooks. tested on a linux box: skill, worker agent, session-start line, doctor and guard all came up.

no ssh, only herdr? drive claude on that machine through herdr, like tmux:

```text
herdr --machine <label> agent start inst --kind claude --pane <pane> --timeout 30000
herdr --machine <label> agent prompt inst "/plugin marketplace add yigitkonur/herdr-conductor"
herdr --machine <label> agent prompt inst "/plugin install herdr-conductor@herdr-conductor"
herdr --machine <label> agent send-keys inst enter
```

read the screen after each one. the first start stops at claude's folder-trust dialog (`down enter` if the folder is yours), and the install menu needs that last `enter`: pick user scope (the first row), then switch it on in the project with `plugin on herdr-conductor` like anywhere else.

### pinning a version

to pin the marketplace to a branch or tag, put it after a `#`. releases are tagged `herdr-conductor--v<version>` (and `v<version>`), so pinning to one looks like this:

```bash
claude plugin marketplace add 'yigitkonur/herdr-conductor#herdr-conductor--v0.1.4'
claude plugin install herdr-conductor@herdr-conductor -s user
```

the list is on the [releases page](https://github.com/yigitkonur/herdr-conductor/releases).

### if it doesn't take

- the install prints "ssh not configured, cloning via https". that's fine, the repo is public.
- you use `/plugin` inside a session and the clone fails: in-session installs don't fall back to https. start claude with `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`, or use the terminal commands from the block above.
- installed, but claude doesn't know the skill: you haven't switched it on in this folder (`plugin on herdr-conductor`), or the session needs a restart or `/reload-plugins`.
- the marketplace was already known from some project's settings: the install then installs the plugin but doesn't write the marketplace into your user settings. run `claude plugin marketplace add yigitkonur/herdr-conductor` once and it says "declared in user settings".
- the doctor warns about `python3`: the hooks need it on the machine's path.
- `claude plugin validate .` in a checkout of this repo checks the marketplace and the plugin manifests.

## what you can say

just talk to it. the skill kicks in whenever herdr comes up.

- "what's running in herdr right now?"
- "start a codex in a new herdr tab in ~/app, have it fix the failing test, and tell me when it's done"
- "claude wrote that diff, have codex review it in herdr"
- "run these three jobs in parallel worktrees"
- "what's going on on my build box?" (saved machines work the same way)
- `/herdr-conductor:conduct add rate limiting to the api`
- `/herdr-conductor:watch all --every 15`

## scenarios

you don't pick a mode. the skill reads the request and routes it. ties go to the smaller one.

| scenario | when | what happens |
| --- | --- | --- |
| quick | one herdr action or one short turn | just does it. no ledger, no questions |
| task | one agent makes something worth checking | run ledger, one agent (or the `herdr-worker` subagent), verified on the machine |
| project | needs a plan file, several agents, or several waves | upfront questions, project card, plan, waves, review loop |
| watch | "what's running where" | one table per server, flags for blocked / out of quota / finished |
| review | judge a pr, commit or diff | a reviewer that did not write it, a different harness when one exists |

for projects it grills you up front, a few rounds of real decisions with a recommendation on each, ends with how much autonomy you want, and then runs without pestering you.

## the stuff baked in

- **waits that wake the session.** `herdr agent wait` runs as a claude code background task. when the agent settles, the session wakes up with the result. end your turn, go get coffee, the agents keep cooking. nobody polls.
- **reads the screen, not just the status.** herdr's status is a guess. a dialog it doesn't recognize reads `idle`. so every settle is followed by a look at the actual screen.
- **dialogs, per harness.** trust prompts, question panels, permission screens, with the keys that actually worked for claude, codex and agy.
- **quota hits.** agy and codex both hide them behind a normal-looking status. the plugin reads the text and knows what to do next: resume, switch harness, or wait for the reset.
- **team runs.** agy and grok sit at `idle` while their subagents are still working. a marker-based wait catches the real end.
- **worktrees for parallel writers.** one branch each, a draft pr or branch as the receipt, clean removal order, and it never forces a dirty one.
- **the author never reviews itself.** reviews go to a different agent, ideally a different harness.
- **a ledger that survives.** every step is tracked as submitted, consumed, completed, verified. after a compaction, a resume or a reboot it reads the ledger and re-checks by name instead of resending prompts blindly.
- **saved machines.** `--machine` on every command, long briefs shipped through a drop folder, results pulled back and checked over ssh.

## autonomy dial

how much it decides alone is a setting, not a vibe.

| level | it will |
| --- | --- |
| l0 | look and report. no prompts, no keys, no closes |
| l1 | answer what the brief, the docs or your standing answers already settle |
| l2 | (default) run the whole goal. only stops for the always-ask list |
| l3 | l2 plus the irreversible stuff you pre-authorized, like merging a reviewed pr |

the always-ask list never moves: logins, credentials, payments, deleting things it didn't create, product calls that are yours.

## the guard

a small hook denies the herdr commands that can wreck your day: stopping or reloading the server, `herdr update`, machine and session management, interactive clients that hang the tool, `worktree remove --force`, `workspace close --group`, killing herdr, approval-bypass flags for agents, and anything that prompts, types into or closes the pane your own session runs in. it also looks at text typed into panes, so an agent can't be told to run them for you. a denial is final for the run: it doesn't get to route around it.

heredoc briefs that just *mention* those words pass fine. if you really want one of them, run it yourself with `!`, or allow that exact command in your config.

it's a seatbelt, not a sandbox. it reads the command line and nothing else.

## config (all optional)

two small files, both plain markdown with a frontmatter block:

- `~/.config/herdr-conductor/config.md`: your defaults. projects folder, default autonomy, which harness does which role, per-machine drop folders, guard allow-list, notifications.
- `CONDUCTOR.md` in a project's session folder: the project card. checks that prove work, what "done" means, off-limits stuff, plus the autonomy lists (pre-authorized actions, standing answers, escalate-always).

no paths are baked in. it adopts a project you already have, makes one in your projects folder or in the repo (git-excluded), and asks when it's ambiguous. `/herdr-conductor:setup` writes both files for you.

## what's in the box

| piece | what it is |
| --- | --- |
| skill `herdr` | the brain. stance, traps, router, core mechanics, plus 13 reference files it loads only when needed |
| `/herdr-conductor:conduct` | run a goal end to end |
| `/herdr-conductor:watch` | the status table, optionally on a schedule |
| `/herdr-conductor:setup` | doctor and config writer |
| agent `herdr-worker` | runs one task through one herdr agent and hands back a fixed report with receipts. never asks you anything, returns `needs_decision` instead |
| hook: guard | the never-list above |
| hook: session start | one context line when herdr matters: versions, which pane is this session, and open runs with the waiters to re-arm |
| `herdr-snapshot` | `herdr api snapshot` as a compact table, on your path while the plugin is on |

## tested for real

not vibes-tested. run live on herdr 0.9.5 with claude, codex and agy, locally and on a saved remote machine:

- background-wait wake-up on an idle session, and a wait that survives `/compact`
- the guard, 58 synthetic commands plus live denies, including a session trying to close its own tab. the doctor run even caught a false positive (`command -v herdr`) that got fixed
- quick, task, delegate and project scenarios. the project run built two branches in two worktrees with two harnesses, had each reviewed by the other, merged and cleaned up
- the worktree refusals (dirty checkout, group close)
- a file brief delivered to a remote machine through a drop folder
- a `conduct` run that opened a draft pr through `gh` and had a second claude review it with a pass comment, then removed its worktree cleanly
- the worker's long path: out of time budget, it hands back `running` with handles, and the conductor's own background wait picks the agent up when it finishes
- an open question dialog holds background notifications until it's answered (they arrive late, not lost)
- the "installed everywhere, on only where you want it" flow: installed globally and disabled on four machines, `hc on` and `hc off` driven through herdr on a scratch project, with the reload counts changing by exactly this plugin's parts
- the install itself: the one-liner from an empty claude config, project scope, a pinned ref, and a clean uninstall and reinstall over ssh on a remote box, with a fresh claude there seeing the skill, the worker agent and the session-start line
- the `claude plugin eval` suite, honestly: triggering (+1.0 over a no-plugin baseline) and the start-and-wait plan (+0.5) separate the plugin from the baseline, the "don't fire on ordinary subagent work" case holds, and the timeout-recovery case does not separate them yet (a plain model answers it the same way). the suite is noisy, details in `tests/CASES.md` (n11)

being honest, not yet verified: an agy team with workers actually running and agy quota recovery (the local agy is an account-rotating wrapper, and launching one would have rotated the account under a live session), plus, in codex, a guard hit on an argv-list tool input (only tested synthetically; the real shell tool sent a plain string) and the `$herdr` implicit-invocation path, plus three rules that are written down but were never provoked live: hands off when you're focused on an agent's pane, two timeouts on an unchanged screen count as no progress, and one re-arm after a dropped ssh. they're flagged in the docs so nothing pretends otherwise.

every live case and what it showed is in [`tests/CASES.md`](tests/CASES.md).

## hacking on it

```text
python3 -I tools/lint.py
```

checks every herdr command and flag in the docs against your installed cli, plus regression rules, links, a coverage map of the original skill, and a leak scan. only `--help` and `completion zsh` ever run.

```text
python3 -I tests/guard_check.py
```

feeds 58 synthetic commands to the guard hook and checks each one is denied or passed. nothing here runs herdr.

```text
cd plugins/herdr-conductor && claude plugin eval . --trust-plugin --no-publish
```

runs the eval suite. the eval sandbox has no herdr socket, so those cases grade what the plugin steers (triggering, the plan it describes, timeout recovery), not live runs.

found something herdr does that this doesn't say? that's a test case. write down the command, the reply and the versions, and open an issue or a pr.

## repo layout

| path | what |
| --- | --- |
| `plugins/herdr-conductor/` | the plugin: skills, agent, hooks, bin, templates, evals |
| `tools/lint.py` | the static checks |
| `tests/CASES.md` | the live case table, trace lines and retest triggers |
| `docs/COVERAGE.md` | where every item of the original skill ended up |

## license

mit. made by [yigit konur](https://github.com/yigitkonur).
