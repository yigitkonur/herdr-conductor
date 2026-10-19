# Saved machines

Back to [SKILL.md](../SKILL.md).

- This machine: `herdr <command>` (its socket). A saved SSH machine: `herdr --machine <label> <command>` on **every** command, discovery included. List profiles with `herdr machine list --json` (each label's ssh `target`); the selector is an enabled profile ID or a unique, case-sensitive label, not an arbitrary hostname.
- `--machine` forwards API commands only: `workspace`, `worktree`, `tab`, `pane`, `notification`, `agent` (except `attach` and `explain --file`), `api snapshot`, `status server`, plugin commands. A bare `status` is refused (exit 2, "not an API-backed machine command"), while `status server --json` gives the server's version and protocol, as does `.result.snapshot.version` from `api snapshot`. `integration status` and `agent explain --file` also exit 2: run them on the machine over ssh.
- IDs and agent names are scoped to one server. The same ID can exist on both (`w4D` was one project locally and another on the remote). Always name the server when you report or act: `<label> wT:p1Z`, `local w2H:pAG`. Inherited local IDs and `--current` never identify remote panes.
- Do not combine `--machine` with `--session` or `--remote`. Forwarding never installs, starts or restarts a server and never falls back to local.
- A connection failure does not prove a mutation was not applied. Inspect remote state before retrying.
- Diagnose with `herdr machine status <label> --json`. `herdr machine reconnect` needs the user to finish SSH authentication in their terminal: tell them to run it.
- Do not add, remove, enable, disable or reconnect machines unless asked (the guard denies these).
- Remote paths must be absolute, `~` or start with `~/`.
- Checks on the machine itself: `ssh -o BatchMode=yes -o ConnectTimeout=10 <target> '<cmd>'` (git state, files, `pgrep`, `gh pr view`). The agent's report is a claim; the machine is the witness.
- Files for a remote agent (long briefs, inputs) and its reports travel through a drop folder (references/briefs.md); confirm a file arrived with `ssh <target> ls -l <path>` before prompting about it.
- A remote harness may behave differently: its own settings (bypass modes, fullscreen TUI), its own detection overrides (`agent explain --json` there), its own wrapper scripts. Read the screen after the first start on each machine.
- Client and server versions can differ: `herdr status client --json` here, `herdr --machine <label> status server --json` there. A missing method is not permission to upgrade a server.
