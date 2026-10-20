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
2. **Critics, then one editor, in a loop.** Each cycle, two scripts check the plan first (timing and house-rule lint), then nine critics read the brief and the plan in parallel, tick a checklist and score against written anchors and example segments. One editor revises the ranked list. Repeat until no serious finding is left, the loop stops improving, or a cap is hit.

After the interview it never asks you anything: not "continue?", not "approve?", not "which option?". When it needs a call, it takes the safest sourced option or leaves a clearly marked placeholder, keeps going, and lists every call it made in `final.md` for you to review afterwards.

## The critics

| id | lens |
|---|---|
| 01 runnable | the timing and lint gate, minutes add up, materials listed, a prepare / what-goes-wrong line per segment, instructions quotable, fast/slow/wrong paths, evidence of learning; gates the rest |
| 02 learning design | observable outcome, a review of earlier lessons, the finished result and success criteria shown first, examples and non-examples, worked examples matched to prior knowledge, retrieval and spacing, misconceptions named, a check that performs the outcome and a branch for its result |
| 03 practical | every learner leaves with something real on their own material; assignments they would do unassigned, with an entry tier; the artifact is used again |
| 04 modalities | every key idea reaches the learner by more than one channel (do / see / read / listen) and everyone gets to do it; passive stretches against the band's house defaults |
| 05 engagement | the hook, every learner answers every question, the challenge curve, fast feedback, small real choices, safe failure; rewards and competition that help rather than backfire |
| 06 story | the concept lives in the story's events, callbacks, one voice, dry humour about the content that fits the age band and never costs a learner dignity |
| 07 media | diagrams, icons, highlighted screenshots and short video planned where they carry the mechanism, following the multimedia checks, specified well enough to produce, no invented data |
| 08 clarity | reading level for the band, the common wrong idea voiced, define before use, one action per sentence, native language and register, no ambiguity |
| 09 design | slides, handouts and screens look intentional and consistent, one icon family, Hangul-safe exports; plus an ideas list that is never auto-built |

How a critic judges:

- **Checks first.** Each critic marks every check in its rubric pass / fail / n/a with one line of evidence, then derives its score by a written rule: start at the matching anchor (4, 7 or 9), move one point at most, and cap at 5 with an open severity-1 finding, at 7 with a severity-2.
- **Examples, not adjectives.** `critics/examples/` holds, per critic, quoted plan segments at a 4, a 7 and a 9, and a good / bad pair per check.
- **Always a weakest segment**, even at or above the bar.
- **Blind comparison.** From cycle 2 the previous and current plans are shown as `plan-A` and `plan-B` in random order. Each critic answers "which better helps the learner reach the outcome?" and "which better follows the brief and house rules?" twice, once in each reading order. "Better" counts only when both agree, and a plan that only got longer is "same".
- **Closure.** Each critic checks the locations where the editor says it fixed last cycle's findings: closed, still open or regressed.
- **One owner per area** (practice, feedback, story, humour, visuals, layout, copy), so overlapping findings merge into one, with a vote count.

## The plan format

`templates/lesson-plan.md`. A lesson is segments, each with one beat (hook, learn, try, apply, check, reward), a modality mix, minutes, a media slot, a game hook, a story or humour note and a prepare / what-goes-wrong line (the 자료 및 유의점 column of a Korean 교수·학습 과정안), plus an outcome with evidence, success criteria or a model answer shown before the task, an "expect effort" line, misconceptions with the segment where each surfaces, a check-result branch, a story frame, a game layer, a practical assignment, materials, a media list and a facts table. Media briefs (`templates/media-brief.md`) specify diagrams, icon sets, screenshots with numbered callouts, storyboarded video and slides so that they can be produced by a tool or a person.

## Age bands

`taste/age-bands.md` fixes, per band from 5-year-olds to seniors, the longest passive stretch, segment and session lengths, reading rules, the humour that lands and the humour that fails, the game mechanics that work and the ones that backfire. Every critic judges against the brief's band, never against its own age.

## Stop rules

- **Bar:** the full panel ran, the gate passed, no severity-1 or severity-2 finding is open, and every critic's derived score is ≥ bar (default 8).
- **Plateau:** a cycle that closed no severity-1 or severity-2 finding and opened no new one.
- **Cap:** `--cycles` (default 4, short cycles included) or the token cap (house rules, else `taste/defaults.md`).

The loop keeps a best-so-far snapshot (fewest open severity-1, then severity-2 findings, then the highest score sum) and restores it at the stop if the last cycle was worse. When the gate fails, a cycle runs critic 01 and the editor only. There is no "blocked" stop and no "your call" stop: gaps are filled with the safest sourced option or a marked placeholder and logged.

"Bar reached" means the critics stopped finding things. It is not proof the lesson works with learners; `evals/` is how the critics themselves are checked.

## Flags

- `--mode live|online|video|guide|talk` detected from the plan when absent
- `--bar N` the score every critic must reach, on top of no open severity-1 or severity-2 finding (default 8)
- `--cycles N` hard cap on cycles (default 4)
- `--skip-interview` with no brief, write it from the files and house rules using recommended answers, logged as decisions; an existing brief is always used as is
- `--only a,b` run only the named critics
- `--dry` intake and interview, write the brief, stop

## What you get

- `docs/lessons/<slug>/brief.md` the brief, with the fact gate: every fact the plan needs, sourced or marked `needs fact:`
- `docs/lessons/<slug>/cycle-N.md` per cycle: gate result, words and tokens, scores, findings with votes, disagreements, decisions the loop made
- `docs/lessons/<slug>/history/cycle-N/` the snapshot, the gate output, each critic's JSON and the blind pair
- `docs/lessons/<slug>/final.md` the stop reason, the delivered snapshot, open findings, and everything for your review: decisions the loop made, `[needs fact: …]` markers, proposed rewrites of locked copy, ideas

## Taste

Three levels, read in order: the project's `taste.md`, the owner's private taste file (`~/.claude/lesson/taste.md`, seeded by `/lesson taste init` and grown from the owner's reactions during runs), then the skill's own `taste/` (age bands, references by mode, the slop list, defaults). When the `uiux` skill is installed, anything on a slide or a screen also follows its taste layer.

## House rules

Put a `lesson.md` in your project root to set rules the loop obeys above its own: language and register, forbidden words, product-name bans, session length caps, facts that may never be invented, what the game layer may never reward, default bar, token budget. The loop also reads your `CLAUDE.md`. See [examples/lesson.md](examples/lesson.md).

## Tools

Two gate scripts run before the critics every cycle: `timing.py` (minutes, passive stretches, beats, channels against the age band) and `lint.py` (forbidden words, product names, media rows without briefs, missing instructions, reading load). Their severity-1 lines go straight to critic 01.

The media scripts make the assets the briefs ask for, from the brief itself:

- **Screenshots:** `capture.py` shoots a web page at phone width and writes the callout coordinates; `highlight.py` draws numbered boxes, arrows and blur.
- **Diagrams and icons:** `diagram/render.py` renders Mermaid with a Korean font at 2x; `icons.py` fetches one icon family per lesson from Iconify.
- **Guides and handouts:** `guide.py` turns a guide plan into a step deck (PDF and phone images) and a printable handout.
- **Narration and video:** `narrate.py` makes draft narration plus captions from the script; `video/storyboard.py` renders the storyboard into a captioned phone video.
- **Quizzes and interactive:** `quiz_export.py` exports check items to Kahoot, Google Forms and Anki; `interactive/lia.py` builds a LiaScript course (SCORM for company LMSs); `interactive/twine.py` builds a branching decision scenario.

Full usage for every script is in [tools/README.md](tools/README.md). The loop gates every cycle on `tools/timing.py` and `tools/lint.py`.

## Testing the skill

`evals/` holds six fixture plans with planted defects plus a clean control, and `evals/calibration.json` with the owner's labels on real findings (valid, invalid, wrong severity). Run them after any edit to a rubric, the shared rules or the loop, and after a model change. A critic that misses its planted defect, raises a severity-1 on the control, or spreads by more than one point across runs on the control gets its rubric rewritten before the loop is trusted. How to run them is in `evals/`; on Windows, eval runs that grant Bash need WSL2.

## Install

As a plugin, in Claude Code 2.1.275 or later:

```
/plugin install lesson --marketplace notsatoshii/lesson
```

Or as a plain skill:

```bash
git clone https://github.com/notsatoshii/lesson ~/.claude/skills/lesson
```

Or clone anywhere and symlink the folder into `~/.claude/skills/`. The media tools have their own setup (Playwright, mermaid-cli, marp-cli, Typst, edge-tts, Node for video); see `tools/README.md`. Each tool says what is missing when it runs. The loop uses whatever is installed: the `grilling` skill's round format for the interview (falls back to its own), the `diagram` skill or inline SVG for diagrams, `uiux` and `impeccable` for the look of materials, `dataviz` for charts, `motion-anything` for motion, a browser tool for screenshots.

## Layout

```
SKILL.md                   the command: phases, rules, flags, sub-commands
loop/orchestration.md      the procedure the main session follows
interview/questions.md     the question bank, in rounds
interview/brief-template.md
templates/lesson-plan.md   the plan format
templates/media-brief.md   diagrams, icons, screenshots with callouts, video, slides
templates/cycle-report.md
critics/00-shared.md       what every critic gets: checks, score rule, ownership, blind comparison, output JSON
critics/01..09-*.md        one lens each, with anchors
critics/examples/          per critic: quoted segments at 4, 7 and 9, and good / bad pairs per check
editor/revise.md           the single writer's rules
taste/                     age bands, references, slop, defaults, the owner's file
tools/                     timing.py and lint.py (the gate); highlight.py, capture.py, icons.py,
                           diagram/, guide.py, templates/handout.typ, narrate.py, quiz_export.py,
                           video/, interactive/ (media)
evals/                     fixture plans with planted defects, a clean control, calibration labels
examples/                  a house-rules file, a project taste file
```

## What it is not

Not a curriculum, not an LMS, not a replacement for a teacher's judgement. It is a procedure that makes a model ask before it writes a lesson, check it against how people actually learn and what keeps them awake, and stop when it is done.

MIT.
