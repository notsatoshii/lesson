---
# PLANTED (same as found-lecture): critic 04 itself must flag S2 at severity 1 or 2.
# Fails when the loop ran a short cycle (01 only) despite --only; see evals/README.md.
type: regex
pattern: '\{(?=[^{}]*"severity"\s*:\s*[12]\b)(?=[^{}]*"location"\s*:\s*"[^"]*\bS2\b)[^{}]*\}'
flags: i
target:
  source: file
  path: docs/lessons/eval-overtime-lecture/history/cycle-1/critic-04.json
---
