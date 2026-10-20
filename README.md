# lesson

An autonomous lesson-design loop for [Claude Code](https://claude.com/claude-code). One command interviews you about the lesson or course (who, how long, what they walk away with), writes a brief, drafts the plan (first time) or takes the one you have, then runs cycles of parallel critics and a single editor until the plan clears a scored bar or stops improving.

```
/lesson "Setting up a password manager" --mode guide
/lesson lessons/week-2-harness.md --bar 9
/lesson course docs/curriculum/online/ --only 02,03,06
/lesson media lessons/week-2-harness.md
```

## Why

Asked for a lesson, a model gives you the average lesson: objectives in teacher jargon, a talk, a worksheet, a quiz, "any questions?". It is correct and nobody would choose to sit through it. lesson separates two problems:

1. **Direction before writing.** A short interview (who and what age, the outcome as a verb plus an artifact, mode and minutes, the real material they apply it to, a story frame, the game layer, the humour limits, what may never be invented) becomes a brief that every later step is held to.
2. **Critics, then one editor, in a loop.** Each cycle, nine critics read the brief and the plan in parallel and score against written anchors. One editor revises the ranked list. Score again, until the bar is met, the scores plateau, or a cap is hit. It does not ask "continue?".

## The critics

| id | lens |
|---|---|
| 01 runnable | minutes add up, materials listed, instructions quotable, fast/slow/wrong paths, evidence of learning; gates the rest |
| 02 learning design | observable outcome, one idea at a time, worked example before practice, retrieval and spacing, misconceptions named, transfer |
| 03 practical | every learner leaves with something real on their own material; assignments they would do unassigned; the artifact is used again |
| 04 modalities | every key idea reaches the learner by more than one channel (do / see / read / listen) and everyone gets to do it; passive stretches under the age cap |
| 05 engagement | the hook, the phone test, the challenge curve, fast feedback, choice, safe failure; game mechanics tied to evidence, never decoration |
| 06 story | a narrative spine with callbacks, one voice, dry humour that fits the age band and never costs a learner dignity |
| 07 media | diagrams, icons, highlighted screenshots and short video planned where they carry the mechanism, specified well enough to produce, no invented data |
| 08 clarity | reading level for the band, define before use, one action per sentence, native language and register, no ambiguity |
| 09 design | slides, handouts and screens look intentional and consistent; plus an ideas list that is never auto-built |

Every rubric carries three anchors (what a 4, a 7 and a 9 look like). A score must quote the anchor it used, or it is thrown out. From cycle 2, each critic first compares the new plan to the previous cycle's blind, before reading the editor's note.

## The plan format

`templates/lesson-plan.md`. A lesson is segments, each with one beat (hook, learn, try, apply, check, reward), a modality mix, minutes, a media slot, a game hook and a story or humour note, plus an outcome with evidence, a story frame, a game layer, a practical assignment, materials, a media list and a facts table. Media briefs (`templates/media-brief.md`) specify diagrams, icon sets, screenshots with numbered callouts, storyboarded video and slides so that they can be produced by a tool or a person.

## Age bands

`taste/age-bands.md` fixes, per band from 5-year-olds to seniors, the longest passive stretch, segment and session lengths, reading rules, the humour that lands and the humour that fails, the game mechanics that work and the ones that backfire. Every critic judges against the brief's band, never against its own age.

## Stop rules

- **Bar:** every active critic ≥ bar (default 8) and no severity-1 finding open.
- **Plateau:** most critics say "same" or "worse" two cycles running.
- **Cap:** `--cycles` (default 6) or a token budget from the house rules.
- **User's call:** the only open blockers need the user (facts, curriculum claims, copy, brand, money).

## Taste

Three levels, read in order: the project's `taste.md`, the owner's private taste file (`~/.claude/lesson/taste.md`, seeded by `/lesson taste init` and grown from the owner's reactions during runs), then the skill's own `taste/` (age bands, references by mode, the slop list, defaults). When the `uiux` skill is installed, anything on a slide or a screen also follows its taste layer.

## House rules

Put a `lesson.md` in your project root to set rules the loop obeys above its own: language and register, forbidden words, product-name bans, session length caps, facts that may never be invented, what the game layer may never reward, default bar, token budget. The loop also reads your `CLAUDE.md`. See [examples/lesson.md](examples/lesson.md).

## Tools

- `tools/timing.py <plan.md>`: checks that minutes add up, the active:passive ratio and the longest passive stretch against the band, beats present, channel coverage. Exit 1 on any failure; the orchestrator gates on it.
- `tools/highlight.py <shot.png> --spec <brief.md>`: draws numbered callouts, boxes, arrows and blur regions on a screenshot from the media brief, for install and how-to steps. Pillow only.

## Install

```bash
git clone https://github.com/notsatoshii/lesson ~/.claude/skills/lesson
```

Or clone anywhere and symlink the folder into `~/.claude/skills/`. The loop uses whatever is installed: the `grilling` skill's round format for the interview (falls back to its own), the `diagram` skill or inline SVG for diagrams, `uiux` and `impeccable` for the look of materials, `dataviz` for charts, `motion-anything` for motion, a browser tool for screenshots.

## Layout

```
SKILL.md                   the command: phases, rules, flags, sub-commands
loop/orchestration.md      the procedure the main session follows
interview/questions.md     the question bank, in rounds
interview/brief-template.md
templates/lesson-plan.md   the plan format
templates/media-brief.md   diagrams, icons, screenshots with callouts, video, slides
templates/cycle-report.md
critics/00-shared.md       what every critic gets, the output JSON, severity rules
critics/01..09-*.md        one lens each, with anchors
editor/revise.md           the single writer's rules
taste/                     age bands, references, slop, defaults, the owner's file
tools/                     timing.py, highlight.py
examples/                  a house-rules file, a project taste file
```

## What it is not

Not a curriculum, not an LMS, not a replacement for a teacher's judgement. It is a procedure that makes a model ask before it writes a lesson, check it against how people actually learn and what keeps them awake, and stop when it is done.

MIT.
