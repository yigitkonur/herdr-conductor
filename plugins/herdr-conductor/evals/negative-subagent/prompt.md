---
description: Ordinary subagent work that never mentions herdr must not load the herdr skill.
tags: [trigger, negative]
runs: 2
max_turns: 6
timeout_seconds: 240
allowed_tools: [Skill, Agent, Read, Glob, Grep]
---

Use a subagent to list the files in the current directory and tell me how many there are.
