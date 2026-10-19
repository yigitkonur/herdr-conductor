# Agent states, sequence numbers and detection

Back to [SKILL.md](../SKILL.md). Read before treating `idle` or `done` as finished, and whenever a state looks wrong.

## The five states

| state | means | does not mean |
| --- | --- | --- |
| `idle` | ready for input | that the task succeeded, that no turn ended since you last looked, that an agy or grok team has finished |
| `done` | ready, with a finished turn nobody has viewed | success: a codex given a model that does not exist printed a 400 error and settled `done`, exit 0 |
| `working` | busy | that it will ever settle on its own (a stuck tool call stays `working`) |
| `blocked` | Herdr recognized an approval, question or permission dialog | that every dialog is recognized: missed ones read `idle` or `done` |
| `unknown` | no classification; an empty shell reports it too | completion, or that an agent is there (check the `agent` field) |

`agent wait` without `--until` matches `idle`, `done` or `blocked`; `unknown` only when named.

## `done` and seen

- `done` is a finished turn not yet seen. Reads, explains and waits leave it in place: a `done` outlived `agent get`, `pane get`, `visible`, `recent` and `recent-unwrapped` reads and 15 s idle *(seen 0.9.3)*.
- An explicit focus marks it seen (`agent focus`, `workspace focus`, a user clicking in the TUI). One `done` turned `idle` two seconds after the server log showed a client focusing its workspace; another turned `idle` with nothing logged, while later `done`s in that focused workspace stayed *(seen 0.9.3)*. Each TUI client keeps its own Done badge, so the user's sidebar can differ from the CLI.
- So an `idle` hides whether a turn ended since you last looked. That record is `completion_seq`.

## `completion_seq` and `state_change_seq`

- `completion_seq` equals the agent's `state_change_seq` at the moment Herdr saw a turn end (both 278), and it grows by more than one per turn (278 → 281 across one prompt): compare with greater-than, never "+1" *(seen 0.9.3)*.
- It is absent while the agent works and before its first finished turn. A `done` that turned `idle` kept it, and that change did not bump `state_change_seq`. An `idle` reached straight from `working` had none (agy mid-run, and the end of a finished agy team run), so its absence does not say the work is unfinished.
- Pane `revision` and `terminal_title` stayed the same across a turn; only `completion_seq` tracked it.
- A value above the ledger's says Herdr saw a turn end. Whether **the work** ended is the screen's to say: during an agy team run Herdr settled `idle`, then `done` again and again, each `done` with a new `completion_seq` (338, 342, 344), while the team's `● Agent(…)` rows still ran under the input box *(seen 0.9.3)*. A settle can be a single frame.
- Unset fields are omitted, not null (`name`, `completion_seq`, `label`): read them with `.get`.

## After every settle: read the screen

`herdr [--machine m] agent read <target> --source visible --lines 40`, then check, in this order:

1. A footer naming keys ("Enter to select", "Enter to confirm · Esc to cancel", "enter Submit", codex `y`/`p`/`esc`) → a dialog, whatever the status (references/dialogs.md).
2. agy: `quota reached`, `Resets in …`, `5H: 0%` in the status bar → quota (references/harness-agy.md).
3. Team rows still running (agy `● Agent(`, claude "Waiting for N dynamic workflow", claude background agents) → the leader settled, the team did not (references/waiting.md, team end).
4. The marker you asked for, on the answer's own line (codex `• MARKER`), after the last prompt.
5. A question in prose → a finished turn; answer it with an ordinary prompt.
6. An error line (400, auth, rate limit) → the turn ended without the work.

Codex's question tool showed `blocked`, then ended the turn by itself about a minute later with its questions left in prose. agy's question dialog read `done` while tall ASCII previews pushed its header out of Herdr's view and `blocked` when it was short, flipping from one question to the next *(seen 0.9.3)*.

## `agent explain`

- `herdr [--machine m] agent explain <target>` prints five lines: final state, matched rule, evidence, manifest source and version. `--verbose` adds every rule's matchers and region (37 lines on codex). `--json` (same as `--format json`) prints a bare object, no envelope: `state`, `matched_rule` (`id`, `priority`, `region`, `state`), `evaluated_rules[]` (each with `matched` and `evidence`: matchers and a `region_preview`), `visible_idle`, `visible_blocker`, `visible_working`, `fallback_reason`, `warnings`, and the rule set's `manifest_source`, `manifest_version`, `cached_remote_version`, `local_override_shadowing_remote`, `remote_update_status`.
- `agent read <target> --source detection` returns the text the rules read (the bottom of the live buffer; on codex byte-identical to `visible`).
- Offline: save that text and run `herdr agent explain --file <saved> --agent <kind> --json` to classify it with this machine's rules (0.08 s). Over `--machine` this exits 2: run it on the machine itself.
- When no rule matches a known agent, Herdr falls back to `idle` and says `default_known_agent_idle_fallback`. That is how agy's trust dialog reads `idle`.

## Detection rules and local overrides

- Rules ship inside herdr, update from herdr.dev while the server runs (only for agents it already knows), and can be overridden per machine in `~/.config/herdr/agent-detection/<agent>.toml`. A local override always wins; `local_override_shadowing_remote: true` in `explain --json` says so. So one harness can read differently per machine, and the rules can change while `herdr --version` does not.
- Rule ids worth knowing (they show in `explain`): claude `live_prompt_box` (idle), `live_blocked_form` and `interactive_question_blocked` (blocked), `dynamic_workflow_prompt` (blocked), `waiting_for_teammates_working` and `background_agents_working` (working); codex `osc_title_working` / `osc_title_idle` / `osc_title_blocked` (from the window title), `trust_directory` (top 20 non-empty lines), `capacity_reached_blocked`; agy `question_prompt` (wants a line starting with "question" and a `─` border in the bottom 16 non-empty lines), `quota_reached_blocked`, `background_command_working`, `subagent_working`. Which exist depends on the machine's rule set: check `explain --json` there.
- Editing or reloading rules is the user's: `herdr server reload-agent-manifests` and `update-agent-manifests` are on the guard's never-list.

## Integrations

- `herdr integration status` lists each harness integration and whether it is outdated (`--outdated-only` lists just those). An integration reports session identity (so Herdr can resume the agent after a restart); a few also report lifecycle state. For claude, codex and agy the state comes from screen detection. Since 0.9.5 Herdr installs no Codex turn hooks.
- Over `--machine`, `integration status` exits 2: run it on the machine (`ssh <target> herdr integration status`).
- Updating an integration (`herdr integration install <agent>`) rewrites that harness's hook config; it is a setup step the user approves, not something a run does on its own.
