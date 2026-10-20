---
# PLANTED: S2 is a 20-minute teacher talk (see + listen only) in band C (passive cap 7, segment cap 15).
# Expect a severity 1 or 2 finding located at S2 in the cycle report. Cap breaches are severity 2 by
# the house-default rule, so both severities pass.
type: regex
pattern: '^\s*[-*]\s*\[(?:sev(?:erity)?[ -]?)?[12]\](?=[^\n]*\bS2\b)'
flags: m
target:
  source: file
  path: docs/lessons/eval-overtime-lecture/cycle-1.md
---
