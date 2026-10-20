# Orchestration

The main session is the orchestrator. It never designs a lesson and never edits one; it runs the procedure below and keeps the log.

## 0. Intake

1. Resolve the argument: a plan file (`.md`), a folder of lessons (course mode), or a bare topic in quotes (new draft). Record the entry file(s) and the output folder `docs/lessons/<slug>/`.
2. New draft or existing? Existing = a plan file with segments and timings exists. New = only a topic, or a file that is notes without a time structure (then the notes are input to the interview, not a plan).
3. House rules: read `lesson.md` in the project root if present, then the project's CLAUDE.md. Pull out: language and register, forbidden words, product-name bans, session length caps, age or audience fixed by the project, curriculum facts that may not be invented, bar override, token budget. Write them into the brief's House rules section verbatim.
4. Existing brief at `docs/lessons/<slug>/brief.md`? Keep it unless the user asked for a new interview.
5. Mode: live, online, video, guide, talk. From the flag, else from the plan, else asked in round 1.
6. Taste layer: load in the order `taste/README.md` gives. If the owner's file is missing, offer `/lesson taste init` once, then continue without it.
7. Tooling: note what is installed for media (the `diagram` skill, `tools/highlight.py` with Pillow, a browser for screenshots, `motion-anything`, `dataviz`) and for design (`uiux`, `impeccable`). Critics 07 and 09 are told what exists so their fixes are producible.

## 1. Interview

Run `interview/questions.md` with the `grilling` skill's round format. Skip questions already answered by the brief, the house rules or the plan. End with the definition of done; wait for the user to approve it; write the brief. A `--dry` run stops here.

## 2. First draft (new lessons only)

Write the plan from the brief with `templates/lesson-plan.md`, in the house-rule language. Fill every segment's detail block. Write one `media/<M-id>.md` per media row from `templates/media-brief.md`. Run `tools/timing.py` on the plan. Do not review during the draft; go to cycles.

## 3. Cycle

Cycle N:

### 3.1 Snapshot

Copy the plan and media briefs to `docs/lessons/<slug>/history/cycle-N/` so critics can compare blind next cycle. Run `tools/timing.py` and attach its output.

### 3.2 Critics, in parallel

Spawn one subagent per active critic in a single message. Each gets exactly this, nothing more:

- `critics/00-shared.md` and its own `critics/NN-*.md`
- the brief
- the plan file and the media briefs (paths)
- the taste layer paths (`taste/README.md` names them) and the owner's taste file path when present
- from cycle 2 on, the previous cycle's snapshot
- the house rules section and the tooling note from intake

Active critics by cycle:

- Cycle 1 and any cycle where runnable scored below 8 last time: 01 runnable, 02 learning design, 03 practical, 04 modalities, 08 clarity.
- Once runnable has scored ≥ 8: add 05 engagement, 06 story, 07 media, 09 design. A lesson that does not fit its slot is not made better by jokes.

With `--only`, run just those.

Each critic returns the JSON block defined in `00-shared.md`. A result without a quoted anchor, or with a finding that has no location, is rejected and that critic re-run once.

### 3.3 Merge

Combine findings. Dedupe by location + issue. Rank: severity 1 (would not work, wrong, violates a house rule) → 2 (hurts the learning) → 3 (polish). Within a severity, lower-numbered critic first. Drop critic 09's `ideas` from the fix list; they go to the report only.

Needs-user items (facts and curriculum claims, copy under a "copy may not change" rule, brand picks, money, anything about real named people) go to a `waiting on user` list, never to the editor.

Time conflicts: when fixes from several critics add minutes, the editor must take minutes from somewhere. The merge note says what the budget is and which segments the brief marked as cuttable.

### 3.4 Editor, alone

One subagent, `editor/revise.md`, gets the ranked list, the brief, the house rules, the time budget note and the file paths. It fixes top-down, severity 1 and 2 fully, severity 3 as far as the cycle budget allows, and returns what it changed and what it did not, with reasons. It may not add activities from the ideas list and may not touch files outside the lesson's folder.

### 3.5 Score and decide

Re-snapshot (3.1). Write `docs/lessons/<slug>/cycle-N.md` from `templates/cycle-report.md`: scores per critic, findings fixed / open / waiting, the editor's note, and each critic's blind comparison verdict.

Stop when any of these is true, and say which:

- **Bar:** every active critic scored ≥ bar this cycle, and no severity-1 finding is open.
- **Plateau:** a majority of critics said "same" or "worse" two cycles running.
- **Cap:** cycle N = `--cycles`, or the token budget in the house rules is reached.
- **User's call:** the only open severity-1 items are in `waiting on user`.

Else cycle N+1.

## 4. Report

`docs/lessons/<slug>/final.md`: the stop reason, the score table across cycles, open items, the waiting-on-user list, the ideas list from critic 09 with one line each, the media list with each asset's status, and the owner-taste lines captured this run (see `taste/owner-taste.md`). In chat: five lines at most, plain words, the stop reason first.

Commit only if the house rules or the user said so; otherwise leave the work uncommitted and say so.

## Course mode (`/lesson course <folder>`)

Run sections 0–4 for each lesson file in order, carrying the previous lesson's artifact names into the next brief. Then one course pass with critics 02, 03 and 06 only, each reading all plans: progression (each lesson needs the last), spacing (concepts return at least twice across the course), the artifact chain (every artifact is used again later), and story threads that pay off. Report at `docs/lessons/<course>/course.md`.
