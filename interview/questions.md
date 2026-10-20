# Interview question bank

Run with the `grilling` skill's round format: a round is every question whose prerequisites are settled, numbered, each with a recommended answer. Wait for answers, recompute, next round. Ask only what the files cannot answer: skip anything already settled by the brief, the house rules or the plan. Facts (what exists in the project, what the current plan says, what tools are installed) are yours to look up, never the user's to type.

Each number is one decision with one recommended answer the user can accept with a word. When a number has several parts (Who: band, group, setting), recommend them together as one answer; never stack two separate decisions under one number.

Keep the whole interview under four rounds for one lesson. The user gives direction; the loop writes the spec. The interview is the only time the loop asks the user anything: after it, every open call is made by the loop and logged as a decision for review in `final.md`. An answer the user skips takes the recommended answer, logged the same way.

## Round 1: who and what for

1. **Who.** Age band (`taste/age-bands.md`), group size, setting, what they already know, why they are here (chose it, were sent, school). Recommend from the project's audience if known.
2. **The outcome.** When this lesson works, what can each learner do afterwards that they could not before, and what do they hold in their hands (file, object, working tool, a decision)? One verb, one artifact. "Understand X" is not accepted; ask what understanding X lets them do.
3. **Mode and time.** Live class or workshop, self-paced online, video, written guide, or a talk? Total minutes, and is that fixed? Recommend from the intake finding.
4. **New or existing.** Confirm the intake finding. For an existing plan: what must not change (activities, copy, order, materials)?

## Round 2: the shape

5. **The real material.** What will learners apply this to that is their own (their job task, their project, their room, their team)? If nothing is theirs yet, what provided material is closest to real for this band?
6. **Story frame.** Is there a running scenario, character or world already (a course guide, a brand character, a classroom theme)? If none: recommend one in one line, with stakes that fit the band. "None, keep it plain" is an acceptable answer for talk and guide modes.
7. **Game layer.** What exists: an app with XP and badges, a classroom points system, nothing. Recommend the default for the mode and band from `taste/defaults.md`. Confirm what may never be rewarded (attendance, speed on thinking, self-reported effort).
8. **Humour register.** Dry by default. How dry, and what is off limits for this audience and setting (school policy, corporate tone, religion, politics, body humour for the band)?
9. **References.** One or two lessons, courses, apps, games or teachers whose *mechanics* to learn from. State back the rule: mechanics, never their look or their brand.

## Round 3: words, pictures, facts

10. **Language and register.** From the house rules if present; confirm. Reading level override for this group if any.
11. **Media that exists.** Slides, screenshots, diagrams, videos, a character, an icon set, a design system. What may be generated (diagrams, highlighted screenshots, storyboards) and what needs a human (filmed video, photos of real people).
12. **Facts.** What may never be invented here: curriculum claims, tool behaviour, numbers, history, legal or safety facts. Where the true facts live (a doc, a fact sheet). Before drafting, the loop lists every fact the plan needs; anything without a source becomes a `needs fact:` line in the brief and a visible marker in the plan, never a mid-loop question.
13. **Devices and access.** What learners have in the room or at home: phone, laptop, accounts, printing, internet, sound. Who may lack one of these.

## Round 4: the bar

14. **Assessment.** How will anyone know it worked: what the teacher or app sees at the end, and later. Recommend evidence over self-report, matched to the mode.
15. **What to cut.** If the lesson runs long, which part goes first? If early, what is the stretch?
16. **Bar and budget.** Score bar (default 8; 9 for a flagship lesson, 7 for an internal first run), cycle cap (default 4), token cap (house rules, else `taste/defaults.md`). The bar means no open severity-1 or severity-2 finding and every critic's score at or above it.
17. **Definition of done.** Not a question. Read back in one block: who, the outcome and artifact, mode and minutes, the story frame, the game layer, the humour limits, the must-not-change list, the facts rule and the `needs fact:` list, the bar and the cycle cap. Write the brief and start the loop. If the user corrects something in the same reply, update the brief; do not wait for an approval.

## Existing-plan branch

When a plan exists, add to round 1:

- R1. **Parity.** Every activity, material and assignment the current plan has, listed from the file (you list it, the user confirms). All of it stays unless named here.
- R2. **What is wrong.** The user's own view of what fails today, in their words: dull, too long, nobody does the homework, the install step always breaks. This seeds, not replaces, the critics.
- R3. **Evidence so far.** Anything known from running it: where learners got stuck, what they said, what they produced.

## Course branch (`/lesson course`)

Add once, before the first lesson's interview:

- C1. **The spine.** The list of lessons in order, each with its outcome and artifact in one line; the artifact chain (which artifact each lesson needs from an earlier one).
- C2. **Threads.** Story threads and game progression that run across lessons (the guide character, levels, a final boss or capstone).
- C3. **Spacing.** Which concepts must return in later lessons.
