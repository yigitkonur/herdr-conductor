---
# herdr-conductor project card. Lives in the project's session directory.
repos:
#  - key: github.com/owner/repo          # normalized remote URL or git common dir
#    server: local                       # or a saved machine label
#    path: /absolute/path/to/checkout
autonomy: L2
default_branch: main
routing:
#  exec: codex -- -s workspace-write
notify: none
research: subagents
review_rounds: 3
pr: draft                               # draft | ready (ready requests reviews from real people on a shared repo)
max_parallel: 3                         # agents working at once
---

# <project>

## Card
- Checks that prove work: <test, build and lint commands with expected output>
- Done means: <e.g. PR open, reviewed PASS by an agent that is not the author, checks green>
- Off limits: <paths, services, branches and data agents must not touch>
- Standing agents: <name: harness, role> (none yet)
- Settled decisions: <choice: source> (none yet)
- Stakes: <what is in production; what git can and cannot undo>

## Pre-authorized actions
<!-- L3 only: irreversible actions the run may take, each with its condition. Never credentials, logins, payments or the guard's list. -->
(none)

## Allowed follow-up work
<!-- Work the run may start beyond the original goal at L2 and L3. One per line. -->
(none)

## Escalate always
<!-- Matters that go to the user at every level. One per line. -->
(none)

## Standing answers
<!-- Questions already settled: the question, then the answer. Matching questions are answered from here at L1 and above. -->
(none)
