---
# PLANTED (same as found-guarantee): critic 08 confirms the 보장 promise at S6, severity 1.
# Lint also reports it to critic 01; this grader checks that 08 sees the forbidden idea too.
# Fails when the loop ran a short cycle (01 only) despite --only; see evals/README.md.
type: regex
pattern: '\{(?=[^{}]*"severity"\s*:\s*1\b)(?=[^{}]*"location"\s*:\s*"[^"]*\bS6\b)[^{}]*\}'
flags: i
target:
  source: file
  path: docs/lessons/eval-statistic-guarantee/history/cycle-1/critic-08.json
---
