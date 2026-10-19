# Scenarios

Back to [SKILL.md](../SKILL.md). The router in SKILL.md picks one; this file says how each runs. Every scenario uses the same mechanics (SKILL.md) and the same safety; they differ in how much state and how many questions they carry.

## quick

One herdr action or one short agent turn with nothing to verify afterwards. Act directly: discover, act, read, answer. No ledger and no session directory. If it turns into a deliverable, promote it to a task and write the ledger then.

## task

One agent produces one result to check.

1. Resolve the session directory and open a run ledger (references/ledger.md). Goal, scenario, autonomy.
2. Pick the harness: the one the user named, else `routing` for the role, else ask once (offer the harnesses that `command -v` finds on that machine).
3. Either run it yourself (tab, start, dialogs, brief, wait, read) or hand it to the `herdr-worker` subagent, which returns a fixed shape with receipts and never asks the user. A worker that returns `needs_decision` brings the dialog text and keys: decide or ask, then answer the dialog yourself. A worker that returns `running` brings the handles: arm your own background wait.
4. Verify on the machine: the done-checks of the brief, run by you (cheap) or by a second agent (tests, review).
5. Close what the run opened, stop its waiters, close the ledger, report.

## project

A goal that needs a plan file, more than one agent, or more than one wave.

### Upfront questions (once, at the start)

1. Map the goal as a design tree: every decision branches into the decisions that hang off it. Split a goal made of independent pieces before refining any of them.
2. Facts are yours to find: the ledger, an existing CONDUCTOR.md, the repository (through read-only subagents), the machines. Decisions are the user's.
3. Ask in rounds. The frontier is every decision whose prerequisites are settled. Ask the whole frontier with AskUserQuestion, up to four questions per call and as many calls as the frontier needs; each question has two to four options, the recommended one first and marked, each saying what it leads to. Wait for the answers, recompute the frontier, ask the next round. A question whose answer depends on another question still open belongs to a later round.
4. Stop when nothing open would change the brief: scope, architecture, rework cost, what "done" means. Settle minor and reversible points yourself and write each choice and its reason into the ledger.
5. The last page is autonomy: the level (L2 recommended unless the card says otherwise), for L3 the pre-authorized actions, and Standing answers for the decisions the plan will expose. Phrase them as scenarios: "When an agent asks to add a dependency, should I decide?", "When a review passes and checks are green, may I merge?", "When an agent hits its quota, may I switch it to another harness?".
6. Write CONDUCTOR.md (card and policy) and the ledger, then start without asking for approval of a plan; the assumptions go into the ledger and the final report.

### From goal to steps

1. **Plan.** Brief a planning agent (routing `plan`, else the harness the user prefers) for a plan only, written to a file: in the repository when it should travel with the PR, else `research/` in the run folder on that machine. Give it a generous ceiling ("at most 2500 lines"): the detail is what lets you cut it into steps that each fit one turn, each with its own check. When the goal is still fuzzy, the brief may open with "grill me on this before you plan"; such questions come back in prose, so answer them in one prompt from the ledger and the card and relay only true decisions to the user.
2. **Waves.** In the same planning session, after the plan exists: "If you orchestrated this plan with as many sub-agents as you like, in at most five waves (fewer, even one, if that is better; your call), how would you split it?" The answer is the wave plan; copy it into the ledger.
3. **Steps.** Hand each wave's steps to executing agents (routing `exec`), one step per brief, parallel steps in separate worktrees (references/worktrees.md). The ledger holds the whole; no agent ever does. Step by step is only as good as its reading: prompt → wait → read → check → ledger, one command at a time.
4. **Review** every PR (below), then the next wave.
5. **Close**: final checks on the integrated result, worktrees removed only after their PRs are confirmed, tabs closed, waiters stopped, ledger closed, one report.

### While it runs

Between plan steps, send the next step yourself; asking there stalls the work. Progress goes to the ledger, not into status replies. Questions follow references/waiting.md (not while agents work and other steps remain). When a card fact changes (a new check, a moved repository), write it into CONDUCTOR.md at once.

## review

Judge a frozen candidate: a PR, a commit range, a diff.

- Only work that ends in a PR or a fixed commit gets a review; anything else gets the cheap checks (exit codes, `git status`, `git log`).
- The reviewer is a fresh agent that is not the author: a different harness when one is available (routing `review`), else a fresh instance of the same harness in its own checkout of the head. It is read-only: no edits, no pushes, no tests that write into the author's checkout.
- Bind the review to the candidate's identity: PR number, base and head SHA. A head that moves invalidates the verdict; review the new pair.
- A round: "review <PR> against <plan or brief>; post findings with `gh pr comment`, first line PASS or FAIL; reply with the marker" → on FAIL the author: "address the latest review comment on <PR>, push, reply with the marker" → the reviewer again. Up to `review_rounds` rounds (default 3), then the user decides. One GitHub account cannot approve or request changes on its own PR, so verdicts travel as comments. One such round found two major and two minor faults that lint had passed.
- Receipt in the ledger: PR URL, base and head SHA reviewed, reviewer name and harness, verdict, comment URL. Merging is the user's unless L3 pre-authorizes it.
- No repository yet: the author may create a private one (`gh repo create <name> --private --source=. --push`) when the card or the user allows it.

## watch

What is running, across servers, without taking anything over.

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py"` locally and with `--machine <label>` for each saved machine (`herdr machine list --json`); a machine that does not answer gets `herdr machine status <label> --json`.
- Flag per agent: `blocked` (read the dialog), agy (read for `quota reached`), `done` with a `completion_seq` above the last sweep's, `unknown` panes that should hold an agent, agents on an open ledger that have no live waiter.
- Watch is read-only. Acting on an agent the run does not own needs the user's go; the agents of an open ledger are the run's own.
- Periodic sweeps: `/herdr-conductor:watch --every <minutes>` sets a recurring `CronCreate` (session-only, fires when the session is idle, expires after 7 days); stop it with `CronDelete`.

## research

- `research: subagents` (default): repository and documentation facts come from read-only subagents, so this session's context stays on the plan.
- Web research, version questions, an unfamiliar error, "which library", or `research: herdr-only`: a fresh herdr agent with a plain prompt. Brief: the question, the decision it serves, what counts as evidence (primary sources, versions, dates); output to `research/<topic>.md` in the run folder, conclusions first, then sources as URLs; reply with a summary of at most ten lines and the marker. Read the summary; open the file only when the summary does not settle the decision. One research agent may be reused for follow-ups on the same topic; an unrelated topic gets a fresh one.
- Give executing agents the conclusions and a few URLs, never the search.
