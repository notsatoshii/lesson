---
# CONTROL: the judge reads the cycle report. Catches severity-1 findings written in a shape the regex misses.
type: llm
focus:
  source: file
  path: docs/lessons/eval-control-clean/cycle-1.md
---

This is the cycle report of a lesson-review loop run on a clean control plan that has no planted defect.

PASS if no finding in the report is marked severity 1 (written as [1], sev-1, sev 1 or severity 1), in any section (fixed, open, gate or lint lines), and the report does not say the plan fails timing or the gate.
FAIL if any finding is marked severity 1, or the report says timing is OVER or UNDER, or the gate failed, or the report is missing or empty.
Severity 2 and 3 findings do not affect the verdict.
