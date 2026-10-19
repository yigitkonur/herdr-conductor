# Coverage of the source skill

Every heading, bold lead-in and live case of the source skill (v5.3.1, written for herdr 0.9.3), and where it went. `python3 -I tools/lint.py` fails when a destination does not exist or a cut has no reason. Destinations are relative to `plugins/herdr-conductor/` or to the repository root.

| source item | destination | note |
| --- | --- | --- |
| SKILL.md: Working with the user | `skills/herdr/SKILL.md` `skills/herdr/references/autonomy.md` | Stance bullets; the decide/ask split is the autonomy file |
| SKILL.md: Conducting work through agents | `skills/herdr/SKILL.md` | Stance |
| SKILL.md: Principles (learned by running it) | `skills/herdr/SKILL.md` `skills/herdr/references/states.md` `skills/herdr/references/dialogs.md` | short form in SKILL.md, evidence in the references |
| SKILL.md: 1. Where you are | `skills/herdr/SKILL.md` | rewritten for both cases: inside a herdr pane and outside; the 'HERDR_ENV unset by design' assumption is gone |
| SKILL.md: 2. Servers: local and saved machines | `skills/herdr/references/machines.md` |  |
| SKILL.md: 3. Raycast tools | `skills/herdr/references/waiting.md` | rewritten for Claude Code background tasks; shell traps kept |
| SKILL.md: 4. Discover | `skills/herdr/SKILL.md` | plus bin/herdr-snapshot |
| SKILL.md: 5. Agent states | `skills/herdr/SKILL.md` `skills/herdr/references/states.md` |  |
| SKILL.md: 6. Send work and read results | `skills/herdr/SKILL.md` |  |
| SKILL.md: 7. Blocked agents and questions | `skills/herdr/SKILL.md` `skills/herdr/references/dialogs.md` |  |
| SKILL.md: 8. Create layout and start agents | `skills/herdr/SKILL.md` | Layout and starting agents |
| SKILL.md: 9. Raycast chat to agent mapping | cut | Raycast chats only; agents are named in the ledger's Targets and Waiters |
| SKILL.md: 10. Safety | `skills/herdr/SKILL.md` `skills/herdr/references/autonomy.md` `hooks/scripts/guard.py` | never-list enforced by the guard hook |
| SKILL.md: 11. Reporting | `skills/herdr/SKILL.md` |  |
| SKILL.md: Decide what git can undo. | `skills/herdr/references/autonomy.md` |  |
| SKILL.md: Facts are yours to find; decisions are the user's. | `skills/herdr/SKILL.md` `skills/herdr/references/autonomy.md` |  |
| SKILL.md: Bring the user only what git cannot undo or evidence cannot settle | `skills/herdr/references/autonomy.md` | the always-ask list; questions through AskUserQuestion |
| SKILL.md: The turn ends when the work does. | `skills/herdr/SKILL.md` `skills/herdr/references/waiting.md` | adapted: a turn may end when every working agent has a live background waiter |
| SKILL.md: The ledger is your memory. | `skills/herdr/SKILL.md` `skills/herdr/references/ledger.md` | chat-id ledger paths replaced by the session directory |
| SKILL.md: Small briefs, one turn each. | `skills/herdr/SKILL.md` |  |
| SKILL.md: `herdr agent wait` is the heartbeat. | `skills/herdr/references/waiting.md` |  |
| SKILL.md: One command, one reply, one decision. | `skills/herdr/SKILL.md` | Traps |
| SKILL.md: Parallel work lives in worktrees; a pull request is its receipt. | `skills/herdr/references/worktrees.md` |  |
| SKILL.md: The author does not verify its own work. | `skills/herdr/SKILL.md` |  |
| SKILL.md: Decide with evidence, brief with conclusions. | `skills/herdr/SKILL.md` `skills/herdr/references/scenarios.md` |  |
| SKILL.md: Plan with depth, execute in small steps. | `skills/herdr/references/scenarios.md` | fixed harness roles removed; roles come from routing |
| SKILL.md: The orchestrator only orchestrates (the busy-CEO rule). | `skills/herdr/SKILL.md` | relaxed by the user's decision: facts via read-only subagents; research: herdr-only restores it |
| SKILL.md: Agents run interactive via agent start; never codex exec, print modes, nohup, pane run | `skills/herdr/SKILL.md` | Traps |
| SKILL.md: Trust the reply you already have. | `skills/herdr/SKILL.md` | Traps |
| SKILL.md: One snapshot is the map. | `skills/herdr/SKILL.md` |  |
| SKILL.md: Status belongs to panes; an agent is a presence. | `skills/herdr/SKILL.md` |  |
| SKILL.md: `done` is unread news that does not keep. | `skills/herdr/SKILL.md` `skills/herdr/references/states.md` |  |
| SKILL.md: A wait is a process, not a promise. | `skills/herdr/SKILL.md` `skills/herdr/references/waiting.md` |  |
| SKILL.md: Herdr tracks states, not turns. | `skills/herdr/SKILL.md` | Traps |
| SKILL.md: The status is Herdr's guess; the screen is the fact. | `skills/herdr/SKILL.md` `skills/herdr/references/states.md` |  |
| SKILL.md: A read is a screen, not a document. | `skills/herdr/SKILL.md` | Traps |
| SKILL.md: History lives in the agent's UI, not in Herdr. | `skills/herdr/SKILL.md` |  |
| SKILL.md: The agent's report is a claim; the machine is the witness. | `skills/herdr/SKILL.md` |  |
| SKILL.md: The brief is the only fence you bring. | `skills/herdr/SKILL.md` `skills/herdr/references/briefs.md` |  |
| SKILL.md: Starting an agent is typing; ready is what the screen shows. | `skills/herdr/SKILL.md` `skills/herdr/references/dialogs.md` |  |
| SKILL.md: A dialog speaks its own keys. | `skills/herdr/SKILL.md` `skills/herdr/references/dialogs.md` |  |
| SKILL.md: Lifetimes nest. | `skills/herdr/SKILL.md` |  |
| SKILL.md: Stopping a turn is not stopping its work. | `skills/herdr/SKILL.md` `skills/herdr/references/harness-codex.md` `skills/herdr/references/harness-agy.md` |  |
| SKILL.md: A surprise is a test case. | `skills/herdr/SKILL.md` `tests/CASES.md` |  |
| SKILL.md: agy's quota hides behind any status. | `skills/herdr/SKILL.md` `skills/herdr/references/harness-agy.md` |  |
| SKILL.md: One tab per agent; close before you open. | `skills/herdr/SKILL.md` |  |
| references/agy.md: intro: the PATH agy is a wrapper with account side effects | `skills/herdr/references/harness-agy.md` | generic wrapper caution; the personal account tool is not named |
| references/agy.md: Briefing agy | `skills/herdr/references/harness-agy.md` | mode words kept as agy's own, not mandated |
| references/agy.md: Teams under /teamwork-preview | `skills/herdr/references/harness-agy.md` `skills/herdr/references/waiting.md` | plus the team-end marker wait for 0.9.4+ idle-at-prompt |
| references/agy.md: agy at its limit | `skills/herdr/references/harness-agy.md` | rotation only through a configured rotate_command |
| references/agy.md: Signs | `skills/herdr/references/harness-agy.md` |  |
| references/agy.md: Recovery, in order. | `skills/herdr/references/harness-agy.md` | fallback harness from routing, not a fixed model |
| references/agy.md: Never: | `skills/herdr/references/harness-agy.md` |  |
| references/agy.md: First run in a new folder | `skills/herdr/references/dialogs.md` |  |
| references/agy.md: Question dialogs | `skills/herdr/references/dialogs.md` |  |
| references/agy.md: How its screen behaves | `skills/herdr/references/harness-agy.md` |  |
| references/agy.md: Interrupting a turn | `skills/herdr/references/harness-agy.md` |  |
| references/briefs.md: State everything settled; leave open only what is open. | `skills/herdr/references/briefs.md` |  |
| references/briefs.md: Delivery | `skills/herdr/references/briefs.md` | machine sync replaced by the drop folder |
| references/briefs.md: What it holds, in this order (six items) | `skills/herdr/references/briefs.md` | plus the worker line |
| references/briefs.md: Before sending | `skills/herdr/references/briefs.md` |  |
| references/briefs.md: After the handback | `skills/herdr/references/briefs.md` |  |
| references/briefs.md: Skeleton | `skills/herdr/references/briefs.md` |  |
| references/briefs.md: references to the personal mission protocol files | cut | personal files; the brief rules themselves are kept |
| references/claude.md: Briefing claude | `skills/herdr/references/harness-claude.md` | 'only when the user asks' routing removed; worker line added |
| references/claude.md: Ultracode | `skills/herdr/references/harness-claude.md` |  |
| references/claude.md: Grilling | `skills/herdr/references/harness-claude.md` |  |
| references/claude.md: First run in a new folder | `skills/herdr/references/dialogs.md` |  |
| references/claude.md: Question dialogs | `skills/herdr/references/dialogs.md` |  |
| references/claude.md: How its screen behaves | `skills/herdr/references/harness-claude.md` |  |
| references/claude.md: Interrupting a turn | `skills/herdr/references/harness-claude.md` |  |
| references/cli.md: Help | `skills/herdr/references/cli.md` |  |
| references/cli.md: Subcommands used or listed | `skills/herdr/references/cli.md` | updated to 0.9.5 |
| references/cli.md: Limits and defaults | `skills/herdr/references/cli.md` | plus the macOS long-command refusal |
| references/cli.md: Replies | `skills/herdr/references/cli.md` | plus 0.9.5 agent fields |
| references/cli.md: Errors | `skills/herdr/references/cli.md` | plus confirmation_required, workspace_not_found, agent_not_running, with actions |
| references/cli.md: Keys | `skills/herdr/references/cli.md` |  |
| references/cli.md: Machines | `skills/herdr/references/machines.md` |  |
| references/codex.md: Briefing codex | `skills/herdr/references/harness-codex.md` |  |
| references/codex.md: Native PR review (proposal; live untested) | cut | a live-untested proposal tied to the old routing; reviews run through an interactive agent (scenarios.md) |
| references/codex.md: First run in a new folder | `skills/herdr/references/dialogs.md` |  |
| references/codex.md: Question dialogs | `skills/herdr/references/dialogs.md` `skills/herdr/references/harness-codex.md` | plus the shift+left panel |
| references/codex.md: How its screen behaves | `skills/herdr/references/harness-codex.md` |  |
| references/codex.md: Interrupting a turn | `skills/herdr/references/harness-codex.md` |  |
| references/harnesses.md: Who does what (fixed roles and models) | cut | removed at the user's request; roles come from routing in config.md or CONDUCTOR.md (ledger.md) |
| references/harnesses.md: Flags that matter | `skills/herdr/references/harness-claude.md` `skills/herdr/references/harness-codex.md` `skills/herdr/references/harness-agy.md` | flags only, no model names |
| references/harnesses.md: Across harnesses | `skills/herdr/references/dialogs.md` `skills/herdr/SKILL.md` `skills/herdr/references/harness-codex.md` | trust stores, reused panes, argument quoting, /stop without --wait |
| references/orchestration.md: The ledger | `skills/herdr/references/ledger.md` | session directory resolution replaces chat-id paths |
| references/orchestration.md: Briefs | `skills/herdr/references/briefs.md` |  |
| references/orchestration.md: From goal to steps (Plan, Waves, Steps) | `skills/herdr/references/scenarios.md` |  |
| references/orchestration.md: Parallel work in worktrees | `skills/herdr/references/worktrees.md` |  |
| references/orchestration.md: Review loop on the PR | `skills/herdr/references/scenarios.md` | reviewer: not the author, another harness when available |
| references/orchestration.md: Receipt for a user-explicit native Codex supplement | cut | belongs to the cut native review proposal; the review receipt in scenarios.md keeps PR, SHAs, reviewer, verdict |
| references/orchestration.md: Being told when work ends | `skills/herdr/references/waiting.md` |  |
| references/raycast.md: bash | `skills/herdr/references/waiting.md` | shell traps kept; the chat tool's timeouts cut |
| references/raycast.md: Background tasks | `skills/herdr/references/waiting.md` | rewritten for Claude Code background tasks and TaskStop |
| references/raycast.md: Staying in the turn | `skills/herdr/references/waiting.md` | rewritten: background waits wake the session |
| references/raycast.md: Chat tools worth knowing | cut | chat-app tools only |
| references/research.md: Launch and prompt | `skills/herdr/references/scenarios.md` | research section; harness from routing |
| references/research.md: Reading and reusing | `skills/herdr/references/scenarios.md` |  |
| references/testing.md (and references/testing/): test campaign protocol and its vendored copy | cut | removed at the user's request |
| SYSTEM_PROMPT.md: Project card | `assets/templates/CONDUCTOR.md` |  |
| SYSTEM_PROMPT.md: First, the skill | cut | chat-app skill loading; replaced by the skill trigger and the SessionStart line |
| SYSTEM_PROMPT.md: Every turn | `skills/herdr/references/ledger.md` | read the ledger before the snapshot |
| SYSTEM_PROMPT.md: Never lose an agent | `skills/herdr/references/waiting.md` |  |
| SYSTEM_PROMPT.md: Questions before the work | `skills/herdr/references/scenarios.md` | upfront questions |
| SYSTEM_PROMPT.md: What the user decides, and how you ask | `skills/herdr/references/autonomy.md` | AskUserQuestion replaces the chat question tool |
| SYSTEM_PROMPT.md: How a turn ends | `skills/herdr/SKILL.md` `skills/herdr/references/waiting.md` |  |
| SYSTEM_PROMPT.md: Talking to the user | `skills/herdr/SKILL.md` | Reporting |
| SYSTEM_PROMPT.md: Keeping the card true | `skills/herdr/references/scenarios.md` | While it runs |
| tests/README.md: T1 | `tests/CASES.md` |  |
| tests/README.md: T2 | `tests/CASES.md` |  |
| tests/README.md: T3 | `tests/CASES.md` |  |
| tests/README.md: T4 | `tests/CASES.md` |  |
| tests/README.md: T5 | `tests/CASES.md` |  |
| tests/README.md: T6 | `tests/CASES.md` |  |
| tests/README.md: T7 | `tests/CASES.md` |  |
| tests/README.md: T8 | `tests/CASES.md` |  |
| tests/README.md: T9 | `tests/CASES.md` |  |
| tests/README.md: T10 | `tests/CASES.md` |  |
| tests/README.md: T11 | `tests/CASES.md` |  |
| tests/README.md: T12 | `tests/CASES.md` |  |
| tests/README.md: T13 | `tests/CASES.md` |  |
| tests/README.md: T14 | `tests/CASES.md` |  |
| tests/README.md: T15 | `tests/CASES.md` |  |
| tests/README.md: T16 | `tests/CASES.md` |  |
| tests/README.md: T17 | `tests/CASES.md` |  |
| tests/README.md: T18 | `tests/CASES.md` |  |
| tests/README.md: T19 | `tests/CASES.md` |  |
| tests/README.md: T20 | `tests/CASES.md` |  |
| tests/README.md: T21 | `tests/CASES.md` |  |
| tests/README.md: T22 | `tests/CASES.md` |  |
| tests/README.md: T23 | `tests/CASES.md` |  |
| tests/README.md: T24 | `tests/CASES.md` |  |
| tests/README.md: T25 research by an agent (not yet run) | `skills/herdr/references/scenarios.md` | research section, untested |
| tests/README.md: T26 file sync between machines | cut | personal setup |
| tests/README.md: T27-T30 test campaign cases | cut | test campaigns removed |
| tests/README.md: T31 a chat stays in its turn | cut | chat-app turn model; replaced by N1 (background wake-up) |
| tests/README.md: T32 a foreground wait near the chat tool's cap | cut | chat-app tool limit; the Claude Code 10-minute foreground cap is in waiting.md |
| tests/README.md: Regression rules R1-R9 | `tools/lint.py` |  |
| tests/README.md: Trace | `tests/CASES.md` |  |
| tests/README.md: Retest triggers | `tests/CASES.md` | personal file hashes dropped |
| tests/README.md: When something new is learned | `tests/CASES.md` |  |
| tests/README.md: Runbook (layer L) | cut | replaced by the N-case live runs of this plugin |
| tests/README.md: The chat app rewrites SKILL.md | cut | a chat-app projection bug, not herdr |
| tests/README.md: History | cut | version history of the old skill |
