---
# PLANTED: S6's instruction ends '보고 시간 단축이 보장됩니다'. 보장 is a forbidden word in lesson.md.
# Expect a severity-1 finding at S6.
type: regex
pattern: '^\s*[-*]\s*\[(?:sev(?:erity)?[ -]?)?1\](?=[^\n]*\bS6\b)'
flags: m
target:
  source: file
  path: docs/lessons/eval-statistic-guarantee/cycle-1.md
---
