---
name: lesson
description: Autonomous lesson-design loop. One command interviews you about the course or lesson (who, how long, what they walk away with), writes a brief, drafts the lesson plan (first time) or takes the plan you have, then runs cycles of parallel critics (runnable, learning design, practical, modalities, engagement + gamification, story + humour, visuals + media, clarity + age fit, design) and a single editor until the plan clears a scored bar or plateaus. Use when the user says /lesson, "review this lesson", "plan a lesson/course/workshop", "make this lesson fun", or wants a lesson built or improved end to end without babysitting.
argument-hint: "<plan file | folder | topic> [--mode live|online|video|guide|talk] [--bar 8] [--cycles 6] [--skip-interview] [--only <critic,...>] [--dry]"
---

# lesson

Read [loop/orchestration.md](loop/orchestration.md) before doing anything. It is the whole procedure; this file is the map.

The loop exists for one reason: a lesson that is correct can still be dull, passive and forgettable. Every cycle asks the same nine questions of the plan: does it run, does it teach, is it practical, does it reach doing / seeing / reading / listening, is it fun and a little bit of a game, does it tell a story with dry humour that fits the age, are the visuals and video planned and earning their place, is it clear for this age, and are the materials well designed.

## Phases

1. **Intake** (you, no questions): find the plan (a file, a folder of lessons, or only a topic), decide new draft vs existing, read the house rules (`lesson.md` in the project root, then CLAUDE.md), find an existing brief, load the taste layer (`taste/README.md`). Facts come from the filesystem, never from the user.
2. **Interview** (`interview/questions.md`): rounds of numbered questions with a recommended answer each, in the style of the `grilling` skill. Ends with a definition of done the user approves. Output: `docs/lessons/<slug>/brief.md` from `interview/brief-template.md`. Skipped when a brief exists and the user did not ask for a new one; then ask one question: "Anything changed since this brief?"
3. **First draft** (only when no plan exists yet): write the plan from the brief with `templates/lesson-plan.md`, one media brief per visual with `templates/media-brief.md`. Do not review during the draft.
4. **Cycles** (`loop/orchestration.md`): parallel critics → merged ranked findings → one editor → score → repeat or stop.
5. **Report**: `docs/lessons/<slug>/cycle-N.md` per cycle, `docs/lessons/<slug>/final.md` at the end, and a five-line summary in chat.

## Rules that never bend

- Critics read, the editor writes. Never two writers on the same files.
- A critic sees the brief, the plan, the media briefs and the previous cycle's plan. Never the editor's reasoning or chat.
- Scores need anchors. Every rubric in `critics/` carries what a 4, a 7 and a 9 look like. A score without a quoted anchor is invalid; re-run that critic.
- No invented facts. No made-up statistics, quotes, studies, tool behaviour, prices, history. A segment that needs a fact the project does not have logs `needs fact:` and the editor leaves a marked gap. Humour and story may be invented; facts may not.
- Every lesson ends in something real. A learner walks out with a thing they made or can now do on their own material, named in the plan. "Understood the concept" is not an outcome.
- Fun serves the learning. A game mechanic, joke or story beat that does not carry a concept or a practice is a finding, not a bonus.
- Age fit is a gate. Humour, examples, reading level, session length and game mechanics are judged against the brief's age band (`taste/age-bands.md`), never against the writer's own age.
- House rules win over this skill. If `lesson.md` or CLAUDE.md fixes the language and register, forbids words, bans product names or caps session length, every critic and the editor obey it.
- The loop stops on its own: bar reached, plateau, cycle cap or token cap. It never asks "continue?" mid-loop. It does stop for the user's own calls: facts, curriculum claims, brand picks, money, and copy the user wrote under a "copy may not change" rule.
- Report faithfully. A plan that does not fit its time slot is reported as not fitting, with the arithmetic.

## Flags

- `--mode` live (class or workshop with a teacher), online (self-paced on a screen), video (recorded), guide (written how-to, install walkthrough), talk (one-off presentation). Detected from the plan when absent.
- `--bar N` the score every critic must reach (default 8, see house rules).
- `--cycles N` hard cap on cycles (default 6).
- `--skip-interview` use the existing brief without the "anything changed?" question.
- `--only a,b` run only the named critics (ids in `critics/`), for a focused pass.
- `--dry` run intake and interview, write the brief, stop before any draft.

## Sub-commands

- `/lesson taste init` seed the owner's taste file (see `taste/owner-taste.md`); `taste add "<note>"`, `taste show`, `taste promote`.
- `/lesson media <plan>` only produce or refresh the media briefs and, where tools allow, the assets (highlighted screenshots via `tools/highlight.py`, diagrams via the `diagram` skill or inline SVG).
- `/lesson course <folder>` run the loop on each lesson in a folder in order, then one course-level pass (critic 02's course checks: progression, spacing, the artifact chain).
