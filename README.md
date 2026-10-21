# herdr-conductor

run a whole squad of coding agents from one claude code session. herdr handles the panes, this plugin handles the thinking.

you tell claude what you want done. it spins up claude, codex, agy (or whatever herdr supports) in their own tabs, hands each one a small brief, waits for them in the background, answers their dialogs, checks the work on the machine, and gets it reviewed by a different agent than the one that wrote it. no babysitting, no "is it done yet" loops.

## why this exists

driving agents through a terminal multiplexer is weirder than it looks. `idle` does not mean finished. trust dialogs eat your prompt. a quota hit hides behind a perfectly green status. a wait that outlives its pane just hangs there. an agent's "done" is a claim, not a receipt.

this plugin is the scar tissue from running all of that for real, written down so claude stops rediscovering it the hard way every session.

## install

one line in your terminal. no menus, no prompts:

```bash
claude plugin install herdr-conductor --marketplace yigitkonur/herdr-conductor
```

that adds this repo as a marketplace (it is one, with a single plugin in it) and installs the plugin at user scope, so it works in every project on the machine. about 8 seconds. then start claude (or run `/reload-plugins` in a session that's already open) and run this once:

```text
/herdr-conductor:setup
```

it's a doctor: checks herdr, the server, your integrations, saved machines and which harnesses are installed. read-only, it won't touch anything without asking.

check it worked:

```bash
claude plugin list
```

you want `herdr-conductor@herdr-conductor`, `Scope: user`, `Status: ✔ enabled`. inside claude, ask "which herdr skills and agents do you have?". the answer is `herdr-conductor:herdr` and `herdr-conductor:herdr-worker`. inside a herdr pane there's also a one-line `herdr-conductor:` context at session start.

you need:

- herdr 0.9.5 or newer, on every machine you want to drive
- claude code 2.1.292 or newer (that's where `--marketplace` landed; tested on 2.1.302 through 2.1.306)
- `python3` (the hooks and the snapshot helper use it)
- the harness clis you actually want to run (claude, codex, agy...), installed and logged in

works from inside a herdr pane or from a plain terminal outside herdr. it figures out which one it's in.

### why a marketplace

claude code installs plugins by name from a marketplace, which is just a git repo with a `.claude-plugin/marketplace.json`. this repo is one, so there's nothing else to register or submit. the one-liner above is "add the marketplace, then install from it" in a single command. the other routes don't stick: `claude --plugin-dir <path>` loads a checkout for one session only.

### other ways in

the same thing in two steps:

```bash
claude plugin marketplace add yigitkonur/herdr-conductor
claude plugin install herdr-conductor@herdr-conductor
```

from inside a claude session, as slash commands:

```text
/plugin marketplace add yigitkonur/herdr-conductor
/plugin install herdr-conductor@herdr-conductor
```

the second one opens a small menu asking where to install. the first row, "install for you (user scope)", is already highlighted. hit enter.

for a whole team, commit it to the repo (project scope):

```bash
cd your-repo
claude plugin marketplace add yigitkonur/herdr-conductor --scope project
claude plugin install herdr-conductor@herdr-conductor --scope project
git add .claude/settings.json && git commit -m "add herdr-conductor"
```

that writes these two entries into `.claude/settings.json`. teammates then just clone, start claude in the repo and trust the folder. that's the whole install: claude fetches the marketplace in the background, and the skill, the worker agent and the guard are live in that very first session (the session-start line shows up from their next session). heads up, `claude plugin list` won't show it for them, because the project enabled it and they never installed it. if they want it listed, they run the `install` line above with `--scope project`. tested on a second box with every trace of the plugin wiped first.

the same json pasted into `~/.claude/settings.json` works as a declarative user install, but nothing downloads until claude starts a session.

```json
{
  "extraKnownMarketplaces": {
    "herdr-conductor": { "source": { "source": "github", "repo": "yigitkonur/herdr-conductor" } }
  },
  "enabledPlugins": { "herdr-conductor@herdr-conductor": true }
}
```

just kicking the tires, one session only, nothing installed:

```bash
git clone https://github.com/yigitkonur/herdr-conductor
claude --plugin-dir ./herdr-conductor/plugins/herdr-conductor
```

### on a saved machine

plugins live in each machine's own claude config, so a remote box needs its own install. over ssh it's the same one line:

```bash
ssh <target> 'claude plugin install herdr-conductor --marketplace yigitkonur/herdr-conductor'
```

the box needs herdr 0.9.5, `python3` and a route to github. a claude that was already running there has to restart to load the hooks. tested on a linux box: skill, worker agent, session-start line, doctor and guard all came up.

no ssh, only herdr? drive claude on that machine through herdr, like tmux:

```text
herdr --machine <label> agent start inst --kind claude --pane <pane> --timeout 30000
herdr --machine <label> agent prompt inst "/plugin marketplace add yigitkonur/herdr-conductor"
herdr --machine <label> agent prompt inst "/plugin install herdr-conductor@herdr-conductor"
herdr --machine <label> agent send-keys inst enter
```

read the screen after each one. the first start stops at claude's folder-trust dialog (`down enter` if the folder is yours), and the install menu needs that last `enter`.

### update, pin, remove

```bash
claude plugin marketplace update herdr-conductor
claude plugin update herdr-conductor@herdr-conductor
```

restart claude to apply. marketplaces from third parties don't auto-update by default; add `"autoUpdate": true` to the marketplace entry in your settings if you want that.

to pin the marketplace to a branch or tag, put it after a `#`:

```bash
claude plugin marketplace add 'yigitkonur/herdr-conductor#main'
```

releases are tagged `herdr-conductor--v<version>`, so pinning to one looks like this:

```bash
claude plugin marketplace add 'yigitkonur/herdr-conductor#herdr-conductor--v0.1.3'
claude plugin install herdr-conductor@herdr-conductor
```

the list is on the [releases page](https://github.com/yigitkonur/herdr-conductor/releases).

to remove it:

```bash
claude plugin uninstall herdr-conductor
claude plugin marketplace remove herdr-conductor
```

on a remote box, uninstall then the one-liner again left the settings file byte for byte as it was.

### if it doesn't take

- the install prints "ssh not configured, cloning via https". that's fine, the repo is public.
- you use `/plugin` inside a session and the clone fails: in-session installs don't fall back to https. start claude with `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`, or use the terminal one-liner (docs).
- installed, but claude doesn't know the skill: restart it, or `/reload-plugins`.
- the marketplace was already known from some project's settings: the one-liner then installs the plugin but doesn't write the marketplace into your user settings. run `claude plugin marketplace add yigitkonur/herdr-conductor` once and it says "declared in user settings".
- `claude plugin list` shows it but the doctor warns about `python3`: the hooks need it on the machine's path.
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
- the install itself: the one-liner from an empty claude config, project scope, a pinned ref, and a clean uninstall and reinstall over ssh on a remote box, with a fresh claude there seeing the skill, the worker agent and the session-start line
- the `claude plugin eval` suite, honestly: triggering (+1.0 over a no-plugin baseline) and the start-and-wait plan (+0.5) separate the plugin from the baseline, the "don't fire on ordinary subagent work" case holds, and the timeout-recovery case does not separate them yet (a plain model answers it the same way). the suite is noisy, details in `tests/CASES.md` (n11)

being honest, not yet verified: an agy team with workers actually running and agy quota recovery (the local agy is an account-rotating wrapper, and launching one would have rotated the account under a live session), plus three rules that are written down but were never provoked live: hands off when you're focused on an agent's pane, two timeouts on an unchanged screen count as no progress, and one re-arm after a dropped ssh. they're flagged in the docs so nothing pretends otherwise.

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
