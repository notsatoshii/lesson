---
# PLANTED: S1 'hook' is the teacher reading today's agenda and taking attendance; no situation or prediction.
# Expect a severity 1 or 2 finding at S1 that names the hook or the agenda.
type: regex
pattern: '^\s*[-*]\s*\[(?:sev(?:erity)?[ -]?)?[12]\](?=[^\n]*\bS1\b)(?=[^\n]*(?:hook|agenda|plan))'
flags: mi
target:
  source: file
  path: docs/lessons/eval-agenda-leaderboard/cycle-1.md
---
