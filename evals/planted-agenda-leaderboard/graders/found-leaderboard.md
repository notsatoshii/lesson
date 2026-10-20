---
# PLANTED: S6 shows every child's name and points on a class leaderboard; band B lists public ranking of
# individuals as a mechanic that backfires. Expect severity 1 or 2 at S6 or the Game layer.
type: regex
pattern: '^\s*[-*]\s*\[(?:sev(?:erity)?[ -]?)?[12]\](?=[^\n]*(?:\bS6\b|game layer))(?=[^\n]*(?:leaderboard|rank))'
flags: mi
target:
  source: file
  path: docs/lessons/eval-agenda-leaderboard/cycle-1.md
---
