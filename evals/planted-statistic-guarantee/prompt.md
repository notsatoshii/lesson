---
description: 'Band E Korean plan under house rules: an invented statistic in S2 and a 보장 promise in S6.'
tags: [lesson-critics, planted]
plugins: ["../.."]
runs: 3
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Write, Edit, Bash]
expected_outcome: 'docs/lessons/eval-statistic-guarantee/cycle-1.md exists and lists each planted defect at its location; graders/ name them.'
---

/lesson docs/lessons/eval-statistic-guarantee/plan.md --skip-interview --cycles 1 --only 01-runnable,08-clarity
