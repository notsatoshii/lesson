---
# PLANTED: S2's instruction states '직장인의 68%가 주간 보고 작성에 매주 3시간 이상을 씁니다'. The number is
# INVENTED for this fixture (no source exists; Facts used cites only '업계 조사'). It is not a real statistic.
# Expect a severity-1 finding at S2 (unsourced fact, needs fact, invented number).
type: regex
pattern: '^\s*[-*]\s*\[(?:sev(?:erity)?[ -]?)?1\](?=[^\n]*\bS2\b)'
flags: m
target:
  source: file
  path: docs/lessons/eval-statistic-guarantee/cycle-1.md
---
