---
description: 'Band C live plan: segments sum 12 min over the budget, and S2 is a 20-minute lecture.'
tags: [lesson-critics, planted]
plugins: ["../.."]
runs: 3
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Write, Edit, Bash]
expected_outcome: 'docs/lessons/eval-overtime-lecture/cycle-1.md exists and lists each planted defect at its location; graders/ name them.'
---

/lesson docs/lessons/eval-overtime-lecture/plan.md --skip-interview --cycles 1 --only 01-runnable,04-modalities
