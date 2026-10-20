---
# PLANTED: segments sum to 57 min against a 45 min budget (50 min live, 10 % buffer): OVER by 12.
# Expect a severity-1 timing finding in the cycle report (any location: header, Segments, S2...).
type: regex
pattern: '^\s*[-*]\s*\[(?:sev(?:erity)?[ -]?)?1\](?=[^\n]*(?:over|budget|sum|timing|57|12 ?min))'
flags: mi
target:
  source: file
  path: docs/lessons/eval-overtime-lecture/cycle-1.md
---
