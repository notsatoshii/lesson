---
description: 'Band B live plan: the hook is an agenda read aloud, points are given for attendance, and S6 shows a public individual leaderboard.'
tags: [lesson-critics, planted]
plugins: ["../.."]
runs: 3
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Write, Edit, Bash]
expected_outcome: 'docs/lessons/eval-agenda-leaderboard/cycle-1.md exists and lists each planted defect at its location; graders/ name them.'
---

/lesson docs/lessons/eval-agenda-leaderboard/plan.md --skip-interview --cycles 1 --only 05-engagement
