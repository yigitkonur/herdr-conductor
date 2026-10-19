# Briefs

Back to [SKILL.md](../SKILL.md). A brief carries everything the agent may not assume. The agent has none of this session's context, may run without approval dialogs, and weighs early text most.

**State everything settled; leave open only what is open.** Verified facts, a confirmed diagnosis with its evidence, the user's decisions, constraints and what was already tried go in plainly. A suspected cause is labelled a hypothesis, with what would disprove it; where to look is a starting point, not a limit. When the change is already decided, say "this is execution" and give it exactly.

## Delivery

- A brief of a few lines goes inline in `agent prompt` (quoted heredoc).
- A longer one goes into a file in the run folder (`briefs/<step>.md`, references/ledger.md) **on the agent's machine**, with a one-line prompt that names it, the harness's own mode word first if it uses one ("/boost Your mission is in <path>. Read the whole file before acting; it is self-contained."). The file outlives a restart or a hand-over to another harness, and the report goes next to it.
- Another machine: the session directory is local, so the file must travel. Copy it to that machine's drop folder (`machines.<label>.remote_drop` in the user config, else a folder the run creates next to the agent's checkout): `ssh <target> 'mkdir -p <drop>/<run>'`, `scp <file> <target>:<drop>/<run>/`, confirm with `ssh <target> ls -l <drop>/<run>/`. Give the absolute remote path in the prompt. Read the report back over ssh (or `scp` it into the run folder) and delete the drop folder when the run ends; what is not pulled back is lost.

## What it holds, in this order

Skip what does not apply; the size follows the task.

1. **Where, and what not to touch.** Machine, absolute path, branch. No merge, deploy, secrets or new dependencies, nothing outside the path unless the brief says so; other agents' worktrees, the running app and real data stay untouched. Who else works there. "You are a worker: do not start, prompt or close herdr agents" unless the brief hands it that job. This comes first.
2. **Context.** Why, what happened, what is true now; confirmed and assumed, each labelled; what to read first, with a line on why. Real artifacts beat a paraphrase: the error text, the PR URL, the IDs.
3. **Objective.** One end state you can observe, the hard limits, and which wins when they conflict. Every target a number or a yes/no: "at most 110 lines", not "about 100".
4. **Done, with proof.** Each check binary and paired with its proof: a command and its expected output. Name what already fails, and have a new failure compared against the base. All checks must pass; one that cannot is reported with evidence, never skipped.
5. **Decide or stop.** It decides alone on failing tests, small library choices and a Plan B. It stops and reports only for two designs with lasting effects, a contract unlike the brief, a fix inside another agent's files, or a missing secret, service or permission: the situation, the options, its recommendation, the decision needed. No third try of the same failing approach; two identical infrastructure failures end the attempt. A task that differs from the brief is reported, not reinterpreted.
6. **Handback.** The shape you want, facts and hypotheses labelled; more than a screen goes to a file beside the brief and the reply is only its path; the last line is a marker new for this run.

Asking first works as its own brief: "questions only, no files, end with MARKER", then the answers, then the build. claude, codex and agy each asked through their question tools and built what was agreed.

## Skeleton

```text
Work on <machine> in <absolute path>, branch <branch>. Do not: <forbidden>. Also working there: <who>. You are a worker: do not start or control herdr agents.
Context: <why; history; now>. Confirmed: <facts, artifacts>. Assumed: <hypothesis>, disproved by <signal>.
Read first: <path> (<why>).
Objective: <one end state>. Limits: <hard limits>. If they conflict: <which wins>.
Done when, all of them:
- <check>: `<command>` prints <expected>
Already failing: <list>; compare new failures against <base>.
Decide tactics alone. Stop and report (situation, options, recommendation, decision needed) only for: two designs with lasting effects, a contract unlike this brief, a fix in another agent's files, a missing secret, service or permission. No third try of one approach.
Return: <shape>, facts and hypotheses labelled; long output to <run folder>/reports/<step>.md. Last line: <MARKER>.
```

## Before sending

Could a capable stranger do it from the brief alone? Are the forbidden actions above the context? Is every done-item binary, with its proof? Is the handback shape given? Is the marker new for this run? Is it no longer than the task needs?

## After the handback

The report is a lead. Rerun the checks that matter on the machine, compare the report with the brief item by item (a target relaxed, a scope narrowed), and write the next brief from what you verified, never from the raw report. Resume an agent that holds the context and send only what is new; start a fresh one, with a standalone brief, when its context is wrong.
