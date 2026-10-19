---
type: llm
---

PASS if the described steps include reading the agent's screen after starting it (for example because of a trust or folder dialog) and checking the result on the machine (tests, git state or a PR) rather than trusting the agent's own report.
FAIL if the plan only starts the agent, prompts it and accepts "done" as success.
