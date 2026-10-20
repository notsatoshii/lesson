# 01 Runnable

Lens: could a teacher, or the app, run this plan tomorrow exactly as written, in the time given, with the materials listed, and know at the end whether it worked? This critic gates 05–09: a plan that does not run is not improved by being funnier.

## Checks

Write one `checks` entry per bold name below (pass / fail / n/a with one line of evidence) before you score; see `00-shared.md`. You run on `gate.json`: quote it, do not recount.

- **Gate:** `tools/timing.py` and `tools/lint.py` both pass. Each lint severity-1 line is already your finding at severity 1 (`source: lint`); confirm its location and give the fix, do not re-derive it. A lint severity-2 or 3 line you agree with becomes your finding at that severity.
- **Arithmetic:** segment minutes sum to the total minus the mode's buffer (live 10 %, talk 5 %, online and video none). Transitions, logging in, handing out, moving chairs cost time; a live plan with no buffer is a finding. Use `tools/timing.py` output when attached.
- **Realistic minutes:** each segment's minutes fit what it asks. Reading 400 words takes a 10-year-old longer than two minutes. Installing software never takes five. Mark the three segments most likely to overrun.
- **Materials:** every item a segment needs appears in the materials table with who brings it and by when. Accounts, logins, downloads, printed sheets, physical objects, a second device.
- **Prepare and what goes wrong:** every segment's `prepare / what goes wrong` line names what must be ready before it starts and the one thing that most often breaks there, with the move that saves it. "Check equipment" or a blank line is a finding; an install, login or upload segment without one is severity 2.
- **Prerequisites:** prior knowledge is stated and checked in the first minutes; a learner who lacks it has a path (a 2-minute primer, a pair, a simpler variant).
- **Instructions:** every segment's learner-facing instruction is written out, in the house-rule language, and could be read aloud or shown as-is. "Discuss the topic" is not an instruction.
- **Fast / slow / wrong:** each try and apply segment says what happens when a learner finishes early, falls behind, or gets it wrong.
- **Outcome evidence:** the outcome names what the teacher or app sees. A plan whose only check is "ask if there are questions" or a self-rating has no evidence.
- **Safety and consent:** physical safety for younger bands; data and privacy when learners paste their own work into a tool; nothing that asks a minor for personal data; nothing that needs a paid account the brief did not grant.
- **Mode fit:** online plans never assume a human is present; video plans never ask the viewer to do something they cannot pause for; guide plans number every step and show the expected result after each.
- **Facts used:** every stated number, name, date and tool behaviour has a source line; each gap carries a visible `[needs fact: …]` marker in the segment and a `needs fact:` row in Facts used, not a guess hidden in the prose. A plausible unsourced number is severity 1.

## Anchors

Quoted example segments for each anchor, and a good / bad pair per check: [`critics/examples/01-runnable.md`](examples/01-runnable.md). Place the plan against those segments, not only against the words below.

- **4:** minutes do not add up or the longest segment is unrealistic; at least one material or account is missing; instructions are topics not sentences; the outcome has no evidence; or a safety or consent gap for the age band.
- **7:** it runs; timing is plausible with the buffer; materials complete; one or two segments lack a fast/slow/wrong path or an exact instruction; the evidence of learning is present but thin (one check at the end only).
- **9:** a substitute teacher could run it cold; every instruction is quotable; every segment has its overrun plan and the plan names what to cut first; evidence of learning appears at least twice; materials and prerequisites are checked in the first three minutes; every fact is sourced.
