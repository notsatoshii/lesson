---
# PLANTED: S1's instruction opens with 당신 (forbidden in lesson.md) and stacks 에 대한 / 의 phrases.
# Expect a severity-1 finding at S1.
type: regex
pattern: '^\s*[-*]\s*\[(?:sev(?:erity)?[ -]?)?1\](?=[^\n]*\bS1\b)'
flags: m
target:
  source: file
  path: docs/lessons/eval-translationese/cycle-1.md
---
