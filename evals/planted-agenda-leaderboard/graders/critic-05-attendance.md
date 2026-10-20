---
# PLANTED (same as found-attendance-points): critic 05 itself must flag attendance points.
type: regex
pattern: '\{(?=[^{}]*"severity"\s*:\s*[12]\b)(?=[^{}]*(?:attendance|being here))[^{}]*\}'
flags: i
target:
  source: file
  path: docs/lessons/eval-agenda-leaderboard/history/cycle-1/critic-05.json
---
