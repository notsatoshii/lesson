---
# PLANTED (same as found-leaderboard): critic 05 itself must flag the leaderboard at severity 1 or 2.
type: regex
pattern: '\{(?=[^{}]*"severity"\s*:\s*[12]\b)(?=[^{}]*(?:leaderboard|rank))[^{}]*\}'
flags: i
target:
  source: file
  path: docs/lessons/eval-agenda-leaderboard/history/cycle-1/critic-05.json
---
