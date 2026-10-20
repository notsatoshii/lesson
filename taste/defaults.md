# Known-good defaults

For when the brief is silent. The house rules (`lesson.md`, CLAUDE.md), the brief and the owner's taste file win over all of this. The numbers are working conventions from planning practice, not research claims; they give a critic something to compare against and the editor a place to start. Age limits come from `taste/age-bands.md`; this file never loosens them.

## Time, by band

Segment length and longest passive stretch are copied from `age-bands.md`. The active ratio is learner-active minutes (try, apply, check) to passive minutes (hook, learn, reward where the learner only watches).

| band | segment | longest passive | active : passive |
|---|---|---|---|
| A | 5–8 min | 3 min | 2 : 1 |
| B | 8–12 min | 5 min | 2 : 1 |
| C | 10–15 min | 7 min | 2 : 1 |
| D | 12–20 min | 10 min | 3 : 2 (bridge convention; `age-bands.md` fixes only A–C and E+) |
| E | 10–20 min | 12 min | 1 : 1 or better |
| F | 10–25 min | 15 min | 1 : 1 or better |
| G | 10–15 min | 10 min | 1 : 1 or better |

A talk is allowed a lower ratio only when the brief says why; the plan still needs a pause-and-do moment at least once per passive-stretch limit.

## The six beats

hook → learn → try → apply → check → reward. Typical splits when the brief gives only the total. Live plans keep a 10 % buffer outside the segments (talk: 5 %); online, video and guide have none.

| beat | 45-min live (40 scheduled + 5 buffer) | 10-min online mission | 5-min video | 20-step guide |
|---|---|---|---|---|
| hook | 4 min | 1 min | 30 s | 1 step: the finished result, shown |
| learn | 7 min | 2 min | 2 min | 2 steps: the mental model, one picture |
| try | 10 min | 3 min | 1 min pause-and-predict | 6 steps on provided material |
| apply | 13 min | 2 min | 30 s: the prompt to do it off-screen | 8 steps on the reader's own material |
| check | 4 min | 1.5 min | 30 s: the one thing to verify | 2 steps: expected result, what to do if not |
| reward | 2 min | 30 s | 30 s: what is now possible | 1 step: what to build next |

A video's try is a pause prompt with the answer after it; its apply is a task the viewer does after the video, named on screen. A guide's steps are counted, not timed; each step shows one action and one expected result.

## Feedback loop

- Reveal after a prediction: the learner commits to a guess before the answer appears.
- On wrong: the score, plus one line that says why, in words the band reads. Never only "incorrect".
- One retry at half credit. The second wrong shows the worked answer.
- No timer on judgement questions. Timers only where speed is the skill.
- Right answers get the reason too, in one line, so a lucky guess still teaches.
- In live mode the loop is a material or a partner, not the teacher: a checklist, an answer card, a self-correcting layout.

## Game layer, by mode

| mode | progression | cadence | what earns a badge |
|---|---|---|---|
| online | XP for evidence: a passed check, a submitted artifact, a retry that then passed | streaks weekly, not daily | an artifact, a boss challenge, a skill used a second time in a later lesson |
| live | team quests with a shared board; one boss challenge where each learner does the real thing alone; physical tokens for A–B | per session | the boss challenge; for A–B, the token is the badge |
| video | progress checkpoints only (which part of the series is done) | none | none |
| guide | progress checkpoints only (step n of N, visible) | none | none |
| talk | none; a single take-home challenge at the close | none | none |

Never: points for attendance, XP for self-reported anything, public ranking of individuals in A–C and E–G, daily streaks with penalties.

## Story

- A recurring guide character who is competent but slightly wrong at the start of each lesson; the learner's work shows the correction.
- Stakes shown in the hook, not announced: what goes wrong without the skill, as a situation.
- One callback in reward, to the hook's situation or to the guide's mistake.
- A–B: the character's problem. C–D: a scenario the learner could be in next year. E–G: the learner's own work or life, this week.
- The story never carries a fact. Facts are in the plan's facts list; the story is around them.

## Humour

- Dry understatement, written to be read silently; no laugh pause.
- One beat per segment at most. None in check, safety or consent moments.
- Targets: the tool, the narrator, the guide character, the absurdity of the task. Never a learner, never the group.
- Band-specific registers are in `age-bands.md`; when unsure, cut the joke.

## Media

- One mechanism diagram per learn segment, showing how the thing works, not that it exists. Two boxes and an arrow is not a diagram.
- Icons from one family, one stroke weight, used as labels and never as decoration.
- Guide mode: one screenshot per step, cropped to the region that matters, at most three numbered callouts, the callout numbers matching the step text.
- Video: 20–60 s per concept, captions always, the key frame readable with the sound off.
- Every visual has a media brief (`templates/media-brief.md`) and a row in the media list; a visual with no purpose line is cut.

## Text, by band

Learner-facing text only. "Define before use" means the term appears in plain words first, then named, in the same segment.

| band | max words per screen or slide | sentence length | terms |
|---|---|---|---|
| A | one short sentence, read aloud | up to 8 words | no new terms unless the term is the lesson |
| B | 40 | up to 12 words | concrete nouns; one new term per segment |
| C | 60 | up to 15 words | define every term once, in their world |
| D | 80 | up to 20 words | adult level; define once, then use |
| E | 80, phone-readable | up to 20 words | plain words first, an everyday analogy for each new concept, jargon only after defined |
| F | as E | as E | as E |
| G | 40, larger type | up to 15 words | no acronyms; step numbers always visible |

Korean: 존댓말 unless the house rules say otherwise; write from intent, not from an English draft; `word-break: keep-all` on screens; no 당신, no 보장 / 반드시.

## Slides and handouts

- One idea per slide. The headline is a sentence that states the idea; the slide shows the evidence for it.
- Minimum type on a projected slide: A–B 36 pt, C–D 28 pt, E–F 24 pt, G 32 pt. Nothing on the slide is smaller than the smallest size the back row reads.
- Handout body: A–B 16 pt, C–F 11–12 pt, G 14 pt.
- Room to write: a blank box or column next to every step the learner acts on; at least a third of a worksheet page is empty.
- The handout is not the slides printed. It carries the steps and the check; the slides carry the hook and the pictures.

## Online screens

- Phone first, designed at 390 px wide; nothing scrolls sideways.
- One interaction per screen; the continue control within thumb reach, 44 px tall or more.
- Progress visible on every screen (step n of N or a bar) and the time estimate for the mission visible before it starts.
- A wrong answer never clears the learner's input.
- Saving happens on every step; leaving and returning resumes at the same screen.

## Accessibility

- Captions on every video; a transcript for anything longer than a minute.
- Colour is never the only signal; pair it with a label, a shape or a number.
- Alt text on every image states what the image shows and why it is there.
- Live mode: a no-device alternative for every try and apply segment (paper, a partner's device, a printed card).
- Reading level checked against the band table above on learner-facing text only.
- Pace options named in the plan: what a fast learner does next, what a slow learner skips, in every try and apply segment.
- Online: operable by keyboard and by screen reader; focus visible; no motion that cannot be paused.
- Video: pause points announced on screen, not only in the voice.
