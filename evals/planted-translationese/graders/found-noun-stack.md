---
# PLANTED: S2's instruction is a noun stack with a double passive (설명되어집니다, 이해를 가지는 것).
# Expect a severity 1 or 2 finding at S2.
type: regex
pattern: '^\s*[-*]\s*\[(?:sev(?:erity)?[ -]?)?[12]\](?=[^\n]*\bS2\b)'
flags: m
target:
  source: file
  path: docs/lessons/eval-translationese/cycle-1.md
---
