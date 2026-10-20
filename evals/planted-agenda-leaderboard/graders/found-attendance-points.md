---
# PLANTED: 'every child gets 10 points for being here' (Game layer progression and S1).
# Expect a severity 1 or 2 finding naming attendance points, at S1 or the Game layer.
type: regex
pattern: '^\s*[-*]\s*\[(?:sev(?:erity)?[ -]?)?[12]\](?=[^\n]*(?:attendance|being here|for being present))'
flags: mi
target:
  source: file
  path: docs/lessons/eval-agenda-leaderboard/cycle-1.md
---
