---
# PLANTED (same as found-statistic): critic 01 (Facts used check) must flag S2 at severity 1.
type: regex
pattern: '\{(?=[^{}]*"severity"\s*:\s*1\b)(?=[^{}]*"location"\s*:\s*"[^"]*\bS2\b)(?=[^{}]*(?:68|statistic|source|fact|통계|출처|근거))[^{}]*\}'
flags: i
target:
  source: file
  path: docs/lessons/eval-statistic-guarantee/history/cycle-1/critic-01.json
---
