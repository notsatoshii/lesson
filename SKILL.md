---
name: lesson
description: Autonomous lesson-design loop. One command interviews you about the course or lesson (who, how long, what they walk away with), writes a brief, drafts the lesson plan (first time) or takes the plan you have, then runs cycles of parallel critics (runnable, learning design, practical, modalities, engagement + gamification, story + humour, visuals + media, clarity + age fit, design) and a single editor until the plan clears a scored bar or plateaus. Use when the user says /lesson, "review this lesson", "plan a lesson/course/workshop", "make this lesson fun", or wants a lesson built or improved end to end without babysitting.
argument-hint: "<plan file | folder | topic> [--mode live|online|video|guide|talk] [--bar 8] [--cycles 4] [--skip-interview] [--only <critic,...>] [--dry]"
---

# lesson

Read [loop/orchestration.md](loop/orchestration.md) before doing anything. It is the whole procedure; this file is the map.

The loop exists for one reason: a lesson that is correct can still be dull, passive and forgettable. Every cycle asks the same nine questions of the plan: does it run, does it teach, is it practical, does it reach doing / seeing / reading / listening, is it fun and a little bit of a game, does it tell a story with dry humour that fits the age, are the visuals and video planned and earning their place, is it clear for this age, and are the materials well designed.

## Phases

1. **Intake** (you, no questions): find the plan (a file, a folder of lessons, or only a topic), decide new draft vs existing, read the house rules (`lesson.md` in the project root, then CLAUDE.md), find an existing brief, load the taste layer (`taste/README.md`). Facts come from the filesystem, never from the user.
2. **Interview** (`interview/questions.md`): rounds of numbered questions with a recommended answer each, in the style of the `grilling` skill, asking only what the files cannot answer. Ends by reading back the definition of done, writing `docs/lessons/<slug>/brief.md` from `interview/brief-template.md`, and starting. No approval step. Skipped when a brief exists and the user did not ask for a new one; the existing brief is used as is.
3. **First draft** (only when no plan exists yet): a fact gate first (every fact the plan needs, sourced or marked `needs fact:` in the brief), then the plan from the brief with `templates/lesson-plan.md`, one media brief per visual with `templates/media-brief.md`. Do not review during the draft.
4. **Cycles** (`loop/orchestration.md`): gate (`tools/gate.py`) → parallel critics → merged ranked findings (`tools/merge.py`) → decide (stop or continue) → one editor → production of the media the briefs specify (`media/out/`) → repeat.
5. **Report**: `docs/lessons/<slug>/cycle-N.md` per cycle, `docs/lessons/<slug>/final.md` at the end (with the decisions the loop made, for review), and a five-line summary in chat.

## Rules that never bend

- Critics read, the editor writes. Never two writers on the same files.
- A critic sees the brief, the plan, the media briefs, the gate output and, from cycle 2, the blind pair and its own closure checklist. Never the editor's reasoning, previous scores, other critics' findings or chat. It writes its JSON to the cycle's history folder and returns only a path, a score and a severity-1 count.
- Checks before scores. Each critic marks every check in its rubric pass / fail / n/a with evidence, then derives its score by the rule in `critics/00-shared.md` against anchors at 4, 7 and 9 and the quoted example segments in `critics/examples/`. A result without checks, a quoted anchor or a weakest segment is invalid; re-run that critic.
- Blind means blind. From cycle 2 critics compare the previous and the current plan as `plan-A` and `plan-B` in random order, in both reading orders. "Better" counts only when both agree. Longer is not better.
- No invented facts. No made-up statistics, quotes, studies, tool behaviour, prices, history. A segment that needs a fact the project does not have keeps a visible `[needs fact: …]` marker, listed in `final.md`. Humour and story may be invented; facts may not.
- Every lesson ends in something real. A learner walks out with a thing they made or can now do on their own material, named in the plan. "Understood the concept" is not an outcome.
- Fun serves the learning. A game mechanic, joke or story beat that does not carry a concept or a practice is a finding, not a bonus.
- Age fit is a gate. Humour, examples, reading level, session length and game mechanics are judged against the brief's age band (`taste/age-bands.md`), never against the writer's own age.
- House rules win over this skill. If `lesson.md` or CLAUDE.md fixes the language and register, forbids words, bans product names or caps session length, every critic and the editor obey it.
- The loop never asks the user anything after the interview. When a call is needed (a brand pick, a paid tool, a gap in an apply, boss or check segment), it takes the safest sourced option or a clearly marked placeholder, keeps going, and logs a decision the loop made: the call, the option chosen, why, the segment. Copy the user wrote under a "copy may not change" rule stays unchanged; proposed rewrites are listed, not applied. The decisions are reviewed in `final.md` after the run.
- The loop stops on its own, and only for these: **bar** (no open severity-1 or severity-2 finding, the gate passes, every derived score ≥ bar, full panel ran), **plateau** (a cycle that closed no severity-1 or severity-2 finding and opened none), **cap** (cycle cap, default 4, or token cap). It keeps the best-scored snapshot and restores it at the stop if the last cycle was worse.
- Report faithfully. A plan that does not fit its time slot is reported as not fitting, with the arithmetic. "Bar reached" means the critics stopped finding things, not that the lesson is proven with learners.

## Flags

- `--mode` live (class or workshop with a teacher), online (self-paced on a screen), video (recorded), guide (written how-to, install walkthrough), talk (one-off presentation). Detected from the plan when absent.
- `--bar N` the score every critic must reach, on top of no open severity-1 or severity-2 finding (default 8, see house rules).
- `--cycles N` hard cap on cycles, short cycles included (default 4).
- `--skip-interview` with no brief, write it from the files and house rules using each question's recommended answer, logged as decisions the loop made. With a brief, it changes nothing (an existing brief is always used as is).
- `--only a,b` run only the named critics (ids in `critics/`), for a focused pass.
- `--dry` run intake and interview, write the brief, stop before any draft.

## Sub-commands

- `/lesson taste init` seed the owner's taste file (see `taste/owner-taste.md`); `taste add "<note>"`, `taste show`, `taste promote`.
- `/lesson media <plan>` only produce or refresh the media briefs and, where tools allow, the assets: screenshots via `tools/capture.py` and `tools/highlight.py`, diagrams via `tools/diagram/` (or the `diagram` skill, or inline SVG), icons via `tools/icons.py`, guide decks via `tools/guide.py`, handouts via `tools/templates/handout.typ`, narration via `tools/narrate.py`, quiz exports via `tools/quiz_export.py`, short videos via `tools/video/`. See `tools/README.md`.
- `/lesson calibrate <lines>` append the owner's labels on past findings (`<slug>/c<N>-<NN>-<k> valid | invalid: note | sev N: note`) with `evals/calibrate.py add`, then print each critic's precision. Optional; the loop never waits for labels.
- `/lesson course <folder>` run the loop on each lesson in a folder in order, then one course-level pass (critic 02's course checks: progression, spacing, the artifact chain).

## Testing the skill

`evals/` holds fixture plans with planted defects plus a clean control, and the owner's calibration labels on real findings. Run them after any edit to a rubric, the shared rules or the loop, and after a model change; a critic that misses its planted defect, raises a severity-1 on the control, or spreads by more than one point across runs on the control needs its rubric rewritten before the loop is trusted. How to run them is in `evals/`.
