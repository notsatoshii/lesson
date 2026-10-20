# The owner's taste file

One file per person, across every course and machine. It is a log of real decisions about teaching, not a list of adjectives: what they chose, what they rejected, in their words, with the date and the course. The critics and the editor read it second, after the project's `taste.md` and before the skill's own taste.

Location: `$LESSON_TASTE` if set, else `~/.claude/lesson/taste.md`. Keep it outside project repos. Symlink it into a private synced folder if you work on more than one machine.

## Format

```markdown
# <name>'s teaching taste

## Likes
- <date> · <course> · "<their words>" → <what it means for a plan, one line>

## Dislikes
- <date> · <course> · "<their words>" → <what to avoid, one line>

## Picks (A/B decisions)
- <date> · <course> · chose <A> over <B> because "<their words>"

## Closest references
- <reference> for <what> (their words if they named it)

## Standing rules (confirmed twice or more)
- <rule> (first <date>, again <date>)
```

A line moves to Standing rules once the owner has said the same thing on two occasions. Standing rules are the part the critics quote in findings.

## How it is seeded: `/lesson taste init`

1. Import: read what the host already knows about the owner's teaching preferences (memory files, earlier briefs, course design docs, `taste.md` files in their projects) and list it back, each line as a quote with its date; the owner confirms or strikes each.
2. Pairs interview, ten rounds at most. Each round shows two short versions of the same two-minute segment and asks which, and why in a few words. Rounds: opener (a situation vs a prediction), explaining (analogy first vs definition first), practice (guided steps vs figure it out with hints), the game layer (XP and badges vs a single boss challenge), story (a recurring character vs the learner as the character), humour (one dry aside vs a running gag), visuals (one diagram per idea vs a storyboard), assignment (make a thing for yourself vs make a thing for someone else), check (a duel vs a checklist), pace (short and many vs long and few). Render each pair as the two segments written out, so the pick is about the lesson, not a description of it.
3. Write the file. Read it back in five lines. Stop.

## How it grows: capture

During a run, every time the owner reacts to a plan, a segment or a cycle report with a judgement about the teaching (not about facts or copy), the orchestrator appends the reaction to the file under Likes or Dislikes, quoted and dated, with the course name. Examples of what counts: "too much talking", "that joke is trying too hard", "this is the kind of assignment I want", "kids won't sit through that", "more like the escape room". What does not count: facts, copy edits, bug reports, priorities.

The orchestrator writes these at the end of the run (step 4, Report), not mid-cycle, and lists what it added in the chat summary so the owner can strike a line.

`/lesson taste add "<note>"` appends a line by hand. `/lesson taste show` prints the file. `/lesson taste promote` moves repeated lines to Standing rules and shows the result.

## How it is read

- Critics 05 (engagement) and 06 (story) quote the owner's Standing rules and Dislikes in findings where they apply, and name the owner's Closest references when they score the taste bar.
- Critics 02–09 and the editor read Likes, Dislikes and Standing rules before judging or writing anything new.
- Nothing in the file overrides the brief's outcome, the age band or the house rules. Where they conflict, the brief wins for that lesson and the critic says so in one line.

## Labels on findings

The owner's verdicts on individual findings (valid, invalid, wrong severity) are not taste and do not go in this file. They go to `evals/calibration.json` by the format in `taste/calibration.md`, and they measure the critics rather than steer them.
