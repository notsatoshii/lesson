# Orchestration

The main session is the orchestrator. It never designs a lesson and never edits one; it runs the procedure below and keeps the log.

After the interview the loop never asks the user anything. Not "continue?", not "approve?", not "which option?". When a call is needed, it makes the call by the rules in 3.4, logs it as a decision the loop made, and keeps going. The user reviews those decisions in `final.md` after the run.

## 0. Intake

1. Resolve the argument: a plan file (`.md`), a folder of lessons (course mode), or a bare topic in quotes (new draft). Record the entry file(s) and the output folder `docs/lessons/<slug>/`.
2. New draft or existing? Existing = a plan file with segments and timings exists. New = only a topic, or a file that is notes without a time structure (then the notes are input to the interview, not a plan).
3. Working copy. The loop always edits `docs/lessons/<slug>/plan.md`. An existing plan anywhere else (a curriculum folder, a doc in another format) is copied there and the source is never edited. When the copy is not in the shape of `templates/lesson-plan.md` (the gate tools read the header line, the `| S<n> |` table and the `#### S<n>` blocks), normalize it before cycle 1, mechanically: one table row per timed block with its minutes, beat and the channels it really uses; every line the author wrote kept verbatim in the detail block as `author line: "…"` (quoted learner-facing words) or `teacher notes (author):` (everything else); `none in source` in every template field the source lacks; no fixes, no new copy, no `instruction:` lines (the editor writes those, in the house-rule language, from the author lines). A fixed program rhythm with no slack gets `buffer: 0 %` in the header. Log the normalization as a decision.
4. House rules: read `lesson.md` in the project root if present, then the project's CLAUDE.md. Pull out: language and register, forbidden words, product-name bans, session length caps, age or audience fixed by the project, curriculum facts that may not be invented and where they live, bar override, cycle override, token cap. Write them into the brief's House rules section verbatim.
5. Existing brief at `docs/lessons/<slug>/brief.md`? Use it as is, unless the user asked for a new interview in the command itself. Do not ask whether anything changed.
6. Mode: live, online, video, guide, talk. From the flag, else from the plan, else asked in round 1.
7. Taste layer: load in the order `taste/README.md` gives. If the owner's file is missing, note it in the brief and continue without it.
8. Tooling: note what is installed for media (the `diagram` skill and `tools/diagram/`, `tools/highlight.py` with Pillow, `tools/capture.py`, `tools/icons.py`, `tools/guide.py`, `tools/narrate.py`, `tools/quiz_export.py`, `tools/video/`, a browser for screenshots, `motion-anything`, `dataviz`) and for design (`uiux`, `impeccable`). Check `tools/lint.py` and `tools/timing.py` run. Critics 07 and 09 are told what exists so their fixes are producible.
9. Budget: bar (`--bar`, else house rules, else 8), cycle cap (`--cycles`, else house rules, else 4), token cap (house rules, else `taste/defaults.md`). Write all three into the brief header.

## 1. Interview

Run `interview/questions.md` with the `grilling` skill's round format. Ask only what the files cannot answer: skip anything settled by the brief, the house rules or the plan. End by reading back the definition of done in one block, write the brief, and start. There is no approval step. A `--dry` run stops after the brief.

With `--skip-interview` and no brief: write the brief from the files and the house rules, fill each open question with its recommended answer, and log each one as a decision the loop made. Write the answers, numbered as in `interview/questions.md`, under the brief's "Answers the loop filled in", each with its source file; the definition of done is written, not read back.

When the house rules hold two rules that collide for this lesson (a break rule against a fixed program rhythm, a copy lock against a language rule), settle the reading once in the brief's House rules section, as a decision, so every critic applies the same reading and none raises the collision as a finding every cycle.

## 2. First draft (new lessons only)

### 2.1 Fact gate, before any writing

List every fact the plan will need: numbers, dates, prices, tool behaviour, curriculum claims, history, legal or safety rules. For each, look for a source the project holds (the fact sheets the house rules name, the brief's Facts sources, files in the repo).

- Sourced: it may enter the plan, with its source in Facts used.
- Not sourced: write it as a `needs fact: <what>` line in the brief's Facts section. The draft is built so the segment works without it: the learner's own material supplies it, or the line carries a visible `[needs fact: …]` marker. It is never filled from memory.

This turns mid-loop surprises into known gaps before cycle 1.

### 2.2 Draft

Write the plan from the brief with `templates/lesson-plan.md`, in the house-rule language. Fill every segment's detail block, including its prepare / what-goes-wrong line. Write one `media/<M-id>.md` per media row from `templates/media-brief.md`. Do not review during the draft; go to cycles.

For an existing plan, run the fact gate on what the plan already states: every unsourced number, name, date or tool behaviour becomes a `needs fact:` line in the brief and a finding for critic 01 in cycle 1.

## 3. Cycle

Cycle N runs: gate → critics → merge → decide → editor. Every stop is decided in 3.4, after the critics and before the editor, so the plan the loop delivers is always one the critics scored.

### 3.1 Gate and snapshot

1. Snapshot: copy the plan and media briefs to `docs/lessons/<slug>/history/cycle-N/`.
2. Run the gate on the snapshot: `tools/gate.py history/cycle-N/plan.md --out history/cycle-N/gate.json --mode <mode> --band <band> --house <lesson.md>` (omit `--house` when the project has no `lesson.md`). It runs `timing.py` and `lint.py`, saves both outputs with each tool's run time, and exits 1 when the cycle must be short. If a tool is missing or crashes (exit 2), note it in the cycle report and continue without it.
3. Every lint finding with severity 1 enters the merge as a severity-1 finding for critic 01, with `source: lint`. Lint findings of severity 2 and 3 are evidence the owning critic may adopt.
4. Word count: count the plan's words and the change from the previous snapshot, for the cycle report.
5. **Short cycle:** if `timing.py` or `lint.py` exits 1, this cycle runs critic 01 and the editor only. A lesson that does not fit its slot, or breaks a house rule, is not improved by a full panel. Short cycles count toward the cycle cap.
6. From cycle 2, build the blind pair: copy the previous snapshot and this one to `history/cycle-N/compare/plan-A.md` and `plan-B.md` in random order, and record which is which in `history/cycle-N/compare/map.json` (`{"A": "cycle-<N-1>", "B": "cycle-<N>"}` or the reverse). Critics never see `map.json`.

### 3.2 Critics, in parallel

Spawn one subagent per active critic in a single message.

**Prompt order.** Every critic gets the identical material first, in this order, so prompt caching can work: `critics/00-shared.md`, the run's taste digest (`docs/lessons/<slug>/taste-digest.md`, built once at intake with `tools/taste_digest.py --band <band> --mode <mode>`: the owner's file whole and only the band's and mode's parts of the skill's taste files), the brief, the house rules section and tooling note from intake, the plan and media brief paths, `gate.json`. Then the parts that differ, last: the blind pair paths, its closure checklist (the previous cycle's `fixed` findings for its lens, each with the new text's location from the editor's report), `full` or `delta`, its output path, its own `critics/NN-*.md` and its `critics/examples/NN-*.md`. Nothing else: never the editor's reasoning, previous scores or other critics' findings.

**Active critics by cycle:**

- Short cycle (gate failed): 01 runnable only, unless `--only` names critics (then those run, so a focused pass or an eval still sees its critics).
- Cycle 1, and any cycle where runnable scored below 8 last time: 01 runnable, 02 learning design, 03 practical, 04 modalities, 08 clarity.
- Once runnable has scored ≥ 8: all nine, adding 05 engagement, 06 story, 07 media, 09 design. A lesson that does not fit its slot is not made better by jokes.
- With `--only`, just those.

**Model and effort.** Critics 01 and 08 are checklist critics fed by tool output: run them on the smaller model the host offers at low effort, with `gate.json` attached. Critics 02 to 07 and 09 run on the main model at normal effort. The editor (3.5) runs at high effort.

**Delta mode.** A critic whose derived score was ≥ bar last cycle and who has no open severity-1 or severity-2 finding of its own runs in `delta`: it re-checks only the segments and media briefs in the editor's change list, plus the comparison and its closure checklist. A cycle that decides the bar (3.4) may rely on delta results only for critics whose segments the editor did not touch.

**Output.** Each critic writes its JSON to `docs/lessons/<slug>/history/cycle-N/critic-NN.json` and returns one line: path, score, severity-1 count. The orchestrator merges from the files and never pastes a critic's JSON into its own context beyond what the merge needs. A file without check results, a quoted anchor or a `weakest` entry, or with a finding that has no location, is rejected and that critic re-run once.

**Tokens.** Tell every critic to open all its inputs in one batch of parallel reads, then write its JSON: each extra turn re-reads the whole context, and a critic that reads file by file spends about half again as much (first real run: 151k tokens for one critic on a 120-minute plan). Record each subagent's token use. The cycle report carries this cycle's total, the run total and the cap.

### 3.3 Merge

1. Read every `critic-NN.json` and the gate's severity-1 lint findings.
2. Map each blind comparison back with `map.json`. Per critic: `better` when both reads of the outcome question pick the current plan and the house-rules question does not pick the previous one in both reads; `worse` when both reads of either question pick the previous plan; otherwise `same`.
3. Dedupe by location + issue. Keep the owner's wording (ownership table in `00-shared.md`) and count every critic that raised it as a vote. Give every finding an id `c<N>-<NN>-<k>` (cycle, critic number, the finding's 1-based position in that critic's JSON); a merged finding lists every id it came from. The ids go on each finding line in the cycle report so the owner can label findings later (`taste/calibration.md`).
4. Rank: severity 1 → 2 → 3. Within a severity, more votes first, then the lower-numbered critic.
5. Disagreements: when two critics give conflicting fixes for the same location, or their comparison verdicts split, write a disagreement row for the cycle report and settle it by the editor's conflict rule (hard limits, then the brief, then the lower-numbered critic).
6. Closure: tally `closed`, `still open` and `regressed` across critics. A regressed item becomes a finding at its severity.
7. Drop critic 09's `ideas` from the fix list; they go to the report only.
8. Time budget: when fixes from several critics add minutes, the merge note says the budget and which segments the brief marked as cuttable.

### 3.4 Decide

**Calls the loop makes.** Collect every critic's `decisions` and any finding that needs a call. For each, the orchestrator picks, writes the pick into the editor's list as an instruction, and logs one line: the call, the option chosen, why, the segment it affects. The rules:

- A fact the project lacks: never invented. The segment keeps a visible `[needs fact: …]` marker and is built to work without the fact where it can. Listed in `final.md`.
- Copy under a "copy may not change" rule: unchanged. Rewrites from `proposed_rewrites` are listed, never applied.
- A gap in an apply, boss or check segment: fill it with the safest sourced option (the learner's own material, a fact sheet the project holds, the brief's fallback material) or a clearly marked placeholder, and keep going.
- A brand, look or icon pick: the project's design system, else the `uiux` taste layer when installed, else `taste/defaults.md`.
- Anything that costs money or needs an account the brief did not grant: the free route, or what the brief granted.
- A tool the project does not have: the asset stays at status `brief`, or a tool noted at intake makes a simpler version.
- A real named person: replaced with a fictional stand-in.
- Two sourced options and no rule: the critics' recommended option with the most votes, else the lower-numbered critic's.

**Best so far.** Rank this cycle's snapshot against earlier ones by: open severity-1 count, then open severity-2 count, then the sum of derived scores. Only cycles that ran the same panel compete; once the full panel has run, a narrower cycle cannot be best. Record the best cycle id in `history/best.json`.

**Stop when any of these is true, and say which:**

- **Bar:** the full panel (or the `--only` set) ran this cycle, the gate passed, no severity-1 or severity-2 finding is open from any active critic, and every derived score is ≥ bar.
- **Plateau:** from cycle 2, a cycle (not a short one) that closed no severity-1 or severity-2 finding and opened no new one.
- **Cap:** cycle N = the cycle cap (default 4), or the run's tokens have reached the token cap.

On any stop, if the best snapshot ranks above this one, restore it: copy `history/cycle-<best>/` back over the plan and media briefs, and say so in `final.md` with what the later cycles changed. Then go to 4.

There is no stop for blocked work and none for the user's call. Gaps are filled by the rules above and logged.

Else run the editor (3.5), then cycle N+1.

### 3.5 Editor, alone

One subagent at high effort, `editor/revise.md`, gets the ranked list, the decisions for this cycle, the brief, the house rules, the time budget note and the file paths. It works segment by segment, severity 1 and 2 fully, severity 3 as far as the cycle budget allows, and returns per finding what it did and the location of the new text, plus any call it had to make itself (logged with the orchestrator's). It may not add activities from the ideas list and may not touch files outside the lesson's folder.

### 3.6 Report

Write `docs/lessons/<slug>/cycle-N.md` from `templates/cycle-report.md`: gate line, tokens and words, scores and comparisons, findings with votes, closure tally, disagreements, decisions the loop made, proposed rewrites, needs-fact markers, the editor's note, the decision. Write it before the editor runs when the cycle stops, after the editor when it continues.

## 4. Report

`docs/lessons/<slug>/final.md`:

- the stop reason, and the best snapshot delivered (restored or not)
- the score table across cycles, with words and tokens per cycle
- open findings
- **decisions the loop made**, once, deduped across cycles: call · option chosen · why · segment
- `[needs fact: …]` markers still in the plan, each with where the fact would come from
- proposed rewrites of locked copy, not applied
- the ideas list from critic 09, one line each
- the media list with each asset's status
- the owner-taste lines captured this run (see `taste/owner-taste.md`)
- one line on what "bar reached" means: the critics stopped finding things, which is not proof the lesson works with learners
- a short **Calibrate** block: the one-line label format from `taste/calibration.md` and the path `evals/calibration.json`, for the owner to mark findings valid / invalid / wrong severity whenever they like; the loop never waits for it

In chat: five lines at most, plain words, the stop reason first, then how many decisions and needs-fact markers wait for review in `final.md`.

Commit only if the house rules or the user said so; otherwise leave the work uncommitted and say so.

## Course mode (`/lesson course <folder>`)

Run sections 0–4 for each lesson file in order, carrying the previous lesson's artifact names into the next brief. The interview's course branch runs once, before the first lesson. Then one course pass with critics 02, 03 and 06 only, each reading all plans: progression (each lesson needs the last), spacing (concepts return at least twice across the course), the artifact chain (every artifact is used again later), and story threads that pay off. Report at `docs/lessons/<course>/course.md`, with every lesson's decisions the loop made gathered in one list.
