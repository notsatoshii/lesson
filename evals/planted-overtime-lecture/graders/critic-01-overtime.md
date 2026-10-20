---
# PLANTED (same as found-overtime): critic 01 itself must raise the timing overrun at severity 1.
type: regex
pattern: '\{(?=[^{}]*"severity"\s*:\s*1\b)(?=[^{}]*(?:over|budget|sum|57|12))[^{}]*\}'
flags: i
target:
  source: file
  path: docs/lessons/eval-overtime-lecture/history/cycle-1/critic-01.json
---
