---
type: llm
---

PASS if the answer says the prompt may or may not have been delivered, looks at the agent's state or screen first, and does not resubmit the same prompt before doing so.
FAIL if it simply sends the prompt again, or treats the timeout as proof that nothing was delivered.
