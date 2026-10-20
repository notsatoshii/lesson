# Media brief: <id> · <type>

lesson: <slug> · segment: <S-id> · type: <diagram | icon set | screenshot+highlights | video | slide | handout | animation> · status: <brief | drafted | final> · owner: <editor | tool | human>

## Purpose

One sentence: what the learner understands or can do after seeing this that they could not before. If the sentence is "it looks nicer", the visual is not earning its place; cut it.

## Replaces

What text or talk this visual removes from the segment (a visual that adds to the words instead of replacing some is usually a finding).

## Spec by type

### diagram
- shows: <the mechanism: boxes, arrows, what flows where>
- labels: <every label, in the house-rule language>, ≤ 7 boxes
- reading order: <where the eye starts, then>
- style: <house style / uiux taste; white card, large type, nothing outside boxes>
- source: inline SVG via the `diagram` skill, or <tool>

### icon set
- concepts: <one icon per recurring concept, ≤ 8>
- rule: one stroke weight, one family, each icon used at least twice in the lesson

### screenshot+highlights
- source screen: <app / site / window, exact state, light or dark theme, language>
- capture: <viewport or crop; include the window chrome? yes/no>
- callouts (numbered, in order of action):
  1. <box or arrow> around <element> · label "<the instruction>"
  2. …
- hide: <any personal data, account names, keys>; blur or replace before publishing
- produce with: `tools/highlight.py <shot.png> --spec <this file>` (boxes, arrows, numbered badges, blur regions)
- a step with more than three callouts becomes two screenshots

### video
- length: <N> s (online lessons: 20–60 s per concept; never a full lecture)
- storyboard, one row per beat:

| t | on screen | voice / caption | note |
|---|---|---|---|
| 0–5 s | <…> | "<…>" | hook |

- captions: always · voice: <who, register> · music: none unless the brief says so
- produce with: screen recording + `tools/highlight.py` for stills, `motion-anything` for motion, or a human

### slide / handout
- one idea per slide; the headline is the idea as a sentence, not a topic
- max text per slide by age band; the rest is spoken or done
- design: follows `taste/README.md` → uiux taste when installed

## Facts shown

Every number or claim visible in the asset, with its source. `needs fact:` for gaps; the asset carries a visible placeholder until filled.

## Alt text

<one or two sentences a screen reader can say>
