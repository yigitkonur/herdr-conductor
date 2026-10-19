---
name: conduct
description: Conduct a goal through herdr agents end to end - upfront questions, a project card, a plan, small briefs in waves, background waits, verification on the machine and a review by an agent that is not the author. Invoked as /herdr-conductor:conduct <goal>.
argument-hint: <goal in one or more sentences>
disable-model-invocation: true
allowed-tools: Bash(herdr *), Bash(python3 *), Bash(git *), Bash(gh *), Read, Write, Edit
---

# Conduct a goal through herdr agents

Goal from the user: $ARGUMENTS

1. If the goal above is empty, ask the user for it in one plain sentence and stop.
2. Read `${CLAUDE_PLUGIN_ROOT}/skills/herdr/SKILL.md` unless it is already loaded in this session, then `${CLAUDE_PLUGIN_ROOT}/skills/herdr/references/scenarios.md`, `ledger.md` and `autonomy.md` in the same folder. They are the rules; this command only starts them.
3. Route: a goal one agent can finish and you can check runs as a **task**; anything needing a plan file, more than one agent or more than one wave runs as a **project**. When it is unclear, ask with AskUserQuestion which of the two the user means (recommendation first).
4. Resolve the session directory (ledger.md: adopt an existing project before creating one) and open a run ledger with `owner_session` set to the session id from the herdr-conductor SessionStart line (if there is none, use `unknown`).
5. Discover: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py"` on every server the goal touches, and the repository state on its machine (`git status`, open PRs).
6. Project: run the upfront questions (scenarios.md) until nothing open would change the brief, ending with the autonomy page; write CONDUCTOR.md. Task: ask only what the evidence leaves open.
7. Run the scenario: briefs per references/briefs.md, waits per references/waiting.md, dialogs per references/dialogs.md, decisions per the autonomy level. Keep every step's state in the ledger.
8. Finish with one report: per agent the server and target, what was submitted, consumed, completed and verified, the receipts, the decisions taken without asking, and what is still open.
