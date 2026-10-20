---
# PLANTED: media/M3.md does not exist; M1 and M2 have briefs.
# Expect a severity 1 or 2 finding located at M3 that names the missing brief.
type: regex
pattern: '^\s*[-*]\s*\[(?:sev(?:erity)?[ -]?)?[12]\](?=[^\n]*\bM3\b)(?=[^\n]*(?:brief|missing|no ))'
flags: mi
target:
  source: file
  path: docs/lessons/eval-media-no-brief/cycle-1.md
---
