---
description: 'Band E Korean plan written as translated English: 당신 in every instruction, noun stacks and 되어지다 passives.'
tags: [lesson-critics, planted]
plugins: ["../.."]
runs: 3
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Write, Edit, Bash]
expected_outcome: 'docs/lessons/eval-translationese/cycle-1.md exists and lists each planted defect at its location; graders/ name them.'
---

/lesson docs/lessons/eval-translationese/plan.md --skip-interview --cycles 1 --only 01-runnable,08-clarity
