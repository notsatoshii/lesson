---
# CONTROL: no planted defect. No finding line in the cycle report may carry severity 1.
type: regex
pattern: '^\s*[-*]\s*\[(?:sev(?:erity)?[ -]?)?1\]'
flags: m
match: not_contains
target:
  source: file
  path: docs/lessons/eval-control-clean/cycle-1.md
---
