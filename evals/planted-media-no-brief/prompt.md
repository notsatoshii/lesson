---
description: 'Band E online plan: Media list row M3 (a 40 s video for S1) has no brief in media/.'
tags: [lesson-critics, planted]
plugins: ["../.."]
runs: 3
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Write, Edit, Bash]
expected_outcome: 'docs/lessons/eval-media-no-brief/cycle-1.md exists and lists each planted defect at its location; graders/ name them.'
---

/lesson docs/lessons/eval-media-no-brief/plan.md --skip-interview --cycles 1 --only 01-runnable,07-media
