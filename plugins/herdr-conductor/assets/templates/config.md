---
# herdr-conductor user config: ~/.config/herdr-conductor/config.md
# Every key is optional; the values below are the defaults unless noted.

# Where new project session directories are created (one folder per project).
# Unset: a session directory lives in the repository as .herdr-conductor/ (git-excluded).
# Example: projects_root: ~/orchestration
projects_root:

# Autonomy when a project card sets none: L0 report, L1 answer from docs, L2 autonomous within the goal, L3 + pre-authorized actions.
default_autonomy: L2

# Role -> harness and agent arguments. Empty: use the harness named in the request, or ask once.
# Roles used by the scenarios: plan, exec, review, research.
routing:
#  plan: codex -- -c model_reasoning_effort=high
#  exec: agy
#  review: claude -- --permission-mode manual
#  research: agy

# Saved herdr machines (labels from `herdr machine list --json`).
machines:
#  buildbox:
#    remote_drop: ~/conductor-drop        # folder for briefs and reports on that machine
#    rotate_command: my-account-rotate     # account rotation for a quota-limited harness, if the machine has one

# Command prefixes the guard hook lets through (only the user edits this list).
guard_allow:
#  - herdr --session hc-test server stop

# none | herdr (toast on the user's Herdr when a decision is needed)
notify: none

# subagents (facts via read-only subagents) | herdr-only (everything through herdr agents)
research: subagents

# Review -> fix rounds before the user decides.
review_rounds: 3
---

Free notes for the conductor (preferences, standing context) go below the frontmatter.
