---
# PLANTED (same as found-missing-brief): critic 07 itself must flag M3 at severity 1 or 2.
# Fails when the loop ran a short cycle (01 only) despite --only; see evals/README.md.
type: regex
pattern: '\{(?=[^{}]*"severity"\s*:\s*[12]\b)(?=[^{}]*"location"\s*:\s*"[^"]*\bM3\b)[^{}]*\}'
flags: i
target:
  source: file
  path: docs/lessons/eval-media-no-brief/history/cycle-1/critic-07.json
---
