# <lesson title>

slug: <slug> · mode: <live|online|video|guide|talk> · age band: <see taste/age-bands.md> · group: <1 | 2–6 | 7–30 | 30+> · total: <N> min · version: <N> · written: <YYYY-MM-DD>

(Optional on the same line: `buffer: N %` when the program fixes the rhythm and leaves no slack, e.g. `buffer: 0 %`; the mode default applies otherwise.)

## Outcome

By the end, each learner **can** <one verb phrase, observable> and **has made** <the artifact, on their own material>. Evidence: <what the teacher or app sees that proves it; never self-report>.

Prior knowledge assumed: <list, or "none">. Prerequisite check: <the 30-second check at the start that confirms it>.

### Success criteria

What "good" looks like, shown to learners before they attempt the task, never only after.

- criteria: <two to four lines a learner can check their own work against; the same lines the check and the assignment use>
- model answer or work sample: <the finished example, or where it lives (a media id, a file)>; for skills with grades of quality, a weak and a strong sample side by side
- shown in: <segment id, before the first try or apply>

### Expect effort

- line: "<the sentence, in the house-rule language, that tells learners practice will feel harder than listening and that the first question is meant to be hard>"
- said in: <segment id, before the first try or pre-question>

## Story frame

- setting: <where the lesson "takes place" or the running scenario>
- character(s): <who the learner is or follows; a recurring guide if the course has one>
- stakes: <what goes wrong if the skill is missing, shown not told>
- callbacks: <two or three threads that return later in the lesson or course>
- humour register: dry, <age band>, never at a learner's expense; one beat per segment at most

## Game layer

- feedback loop: <how a learner knows within seconds whether they got it: score, reveal, checklist, duel>
- progression: <points / levels / badges / quests used here, what each is awarded for; no points for attendance or self-reported time>
- challenge curve: <where it gets harder, where it eases, the "boss": the moment they do the real thing alone>
- choice: <where the learner chooses (path, example, order), at least once>
- safe failure: <where it is fine to be wrong and what happens then>

## Segments

Every segment has one beat, a modality mix, and a clock. Beats: **hook** (a situation or prediction), **learn** (one idea, one analogy, one micro-interaction), **try** (practice on provided material, safe to fail), **apply** (the same move on the learner's own material, produces the artifact), **check** (evidence of learning, one verification habit), **reward** (progress shown, next thing teased), and **open** for a break, free talk or Q&A the learners lead (neither active nor passive: it ends a passive stretch and is exempt from the single-segment cap). Modalities: **do** / **see** / **read** / **listen**; mark every channel the segment actually uses.

| id | min | beat | title | what happens (learner's view) | modalities | media | game | story / humour |
|---|---|---|---|---|---|---|---|---|
| S1 | 3 | hook | <…> | <…> | see · listen | M1 | predict → reveal | <beat> |
| S2 | 7 | learn | <…> | <…> | see · read · listen | M2 | tap to reveal | <…> |
| S3 | 10 | try | <…> | <…> | do · see | – | score + combo | <…> |
| S4 | 15 | apply | <…> | <…> | do | M3 | XP, artifact saved | <…> |
| S5 | 4 | check | <…> | <…> | do · read | – | – | <…> |
| S6 | 1 | reward | <…> | <…> | see | – | badge / progress | <callback> |

Timing rule: segments sum to total minus a buffer (live: 10 %, online: none, video: none, talk: 5 %; a `buffer:` header value overrides it). The longest passive stretch (learner only sees / reads / listens) is capped by the age band.

### Segment detail

For each segment: the exact instruction the learner hears or reads (in the house-rule language and register), the materials, what to prepare and what usually goes wrong (the 자료 및 유의점 line of a Korean 교수·학습 과정안), the teacher's or app's move when a learner is fast / slow / wrong, and the transition line into the next segment.

#### S1 <title>
- instruction: "<…>"
- expected: "<what the learner sees when it worked; required in guide mode and for every install or setup step>"
- materials: <…>
- prepare / what goes wrong: <what must be ready before the segment starts> / <the one thing that most often breaks here, and the move that saves it>
- fast / slow / wrong: <…> / <…> / <…>
- transition: "<…>"

Check and retrieval segments also carry their items, which every learner answers and `tools/quiz_export.py` exports:

```
- check items:
  Q: <question>
  A: <correct answer>
  W: <wrong option> (misconception: <the wrong belief this option catches>)
  F: <feedback that says what to do next>
```

(repeat per segment)

## Misconceptions

The two or three wrong ideas learners most often bring. Each is voiced before the explanation that fixes it, not only corrected afterwards.

| misconception | surfaces in | how it is voiced first | the line that fixes it |
|---|---|---|---|
| <the wrong belief, as a learner would say it> | S? | <prediction, hinge question, or the narrator saying it out loud> | "<…>" |

## Check-result branch

What happens with the check's result. A check whose result changes nothing is decoration.

- weak result (<threshold, e.g. fewer than 2 of 3 criteria met>): <reteach move in this lesson, or the next lesson's opener, named>
- strong result (<threshold>): <extension on the same artifact>
- recorded where: <the sheet, the app field, the teacher's list>

## Assignment (the practical)

- task: <what they make or do on their own material after the lesson; usable the next day>
- uses: <where this artifact is used again in the course, or in their life>
- deliverable: <the file, photo, link or demonstration>
- check: <the Success criteria lines the learner can self-run, plus the one line the teacher or app checks>
- time: <N> min · optional stretch: <…>

## Materials

| item | for | who brings | prepared by when |
|---|---|---|---|
| <…> | S3 | teacher / app | <…> |

## Media list

One row per visual, each with a brief in `media/` from `templates/media-brief.md`.

| id | type | segment | purpose (one line) | status |
|---|---|---|---|---|
| M1 | diagram | S2 | <…> | brief / drafted / final |
| M2 | screenshot+highlights | S4 | <…> | |
| M3 | video 40 s | S1 | <…> | |
| M4 | icon set | all | <…> | |

## Accessibility and inclusion

reading level: <per age band> · captions on video: yes · colour never the only signal · alternatives for learners without <device / account / mobility> · pace options: <…>

## Teacher / app notes

- timing buffers: <…>
- misconceptions: see the Misconceptions table
- what to cut first if running late: <segment id>
- what to add if early: <stretch task>

## Facts used

Every number, name, date or tool behaviour stated in the plan, with its source. `needs fact:` lines are open gaps.

- <fact> ← <source>
