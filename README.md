# herdr-conductor

run a whole squad of coding agents from one claude code session. herdr handles the panes, this plugin handles the thinking.

you tell claude what you want done. it spins up claude, codex, agy (or whatever herdr supports) in their own tabs, hands each one a small brief, waits for them in the background, answers their dialogs, checks the work on the machine, and gets it reviewed by a different agent than the one that wrote it. no babysitting, no "is it done yet" loops.

## why this exists

driving agents through a terminal multiplexer is weirder than it looks. `idle` does not mean finished. trust dialogs eat your prompt. a quota hit hides behind a perfectly green status. a wait that outlives its pane just hangs there. an agent's "done" is a claim, not a receipt.

this plugin is the scar tissue from running all of that for real, written down so claude stops rediscovering it the hard way every session.

## get it

```text
/plugin marketplace add yigitkonur/herdr-conductor
/plugin install herdr-conductor@herdr-conductor
```

the second command opens a small menu asking where to install. pick the first one, "install for you (user scope)", and hit enter. then run `/herdr-conductor:setup` once. it's a doctor: checks herdr, the server, your integrations, saved machines and which harnesses are installed. read-only, it won't touch anything without asking.

you need:

- herdr 0.9.5 or newer, on every machine you want to drive
- claude code with plugin support (tested on 2.1.302)
- `python3` (the hooks and the snapshot helper use it)
- the harness clis you actually want to run (claude, codex, agy...), installed and logged in

works from inside a herdr pane or from a plain terminal outside herdr. it figures out which one it's in.

## installing on a saved machine

plugins live in each machine's own claude config, so a remote box needs its own install. you can do it without leaving your session, straight through herdr:

```text
herdr --machine <label> agent start inst --kind claude --pane <pane> --timeout 30000
herdr --machine <label> agent prompt inst "/plugin marketplace add yigitkonur/herdr-conductor"
herdr --machine <label> agent prompt inst "/plugin install herdr-conductor@herdr-conductor"
herdr --machine <label> agent send-keys inst enter
```

read the screen after each one. the first start stops at claude's folder-trust dialog (`down enter` if the folder is yours), and the install menu needs that last `enter`. then restart claude there so the hooks load. the box needs herdr 0.9.5, `python3` and a route to github. this exact flow was run on a linux box and the doctor, the skill, the worker agent and the guard all came up.

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
- **worktrees for parallel writers.** one branch each, a pr or branch as the receipt, clean removal order, and it never forces a dirty one.
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

a small hook denies the herdr commands that can wreck your day: stopping or reloading the server, `herdr update`, machine and session management, interactive clients that hang the tool, `worktree remove --force`, `workspace close --group`, killing herdr, and approval-bypass flags for agents. it also looks at text typed into panes, so an agent can't be told to run them for you.

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

- background-wait wake-up on an idle session
- the guard, 45 synthetic commands plus live denies. the doctor run even caught a false positive (`command -v herdr`) that got fixed
- quick, task, delegate and project scenarios. the project run built two branches in two worktrees with two harnesses, had each reviewed by the other, merged and cleaned up
- the worktree refusals (dirty checkout, group close)
- a file brief delivered to a remote machine through a drop folder
- the `claude plugin eval` suite: 4 of 4 cases pass, and the no-plugin baseline scores clearly lower where it should

being honest, not yet verified: pull requests through `gh`, a live `/compact`, the worker's long `running` path, an agy team with workers actually running (its quota was gone), and agy quota recovery. they're flagged in the docs so nothing pretends otherwise.

every live case and what it showed is in [`tests/CASES.md`](tests/CASES.md).

## hacking on it

```text
python3 -I tools/lint.py
```

checks every herdr command and flag in the docs against your installed cli, plus regression rules, links, a coverage map of the original skill, and a leak scan. only `--help` and `completion zsh` ever run.

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
