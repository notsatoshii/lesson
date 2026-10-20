---
description: 'Clean control, band E live, written to sit at a true 8: no planted defect. No critic should raise a severity-1 finding.'
tags: [lesson-critics, control]
plugins: ["../.."]
runs: 3
max_turns: 200
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Write, Edit, Bash]
expected_outcome: 'docs/lessons/eval-control-clean/cycle-1.md exists and carries no severity-1 finding.'
---

/lesson docs/lessons/eval-control-clean/plan.md --skip-interview --cycles 1 --only 01-runnable,02-learning-design,03-practical,04-modalities,05-engagement,06-story,07-media,08-clarity,09-design
