# Media brief: <id> · <type>

lesson: <slug> · segment: <S-id> · type: <diagram | icon set | screenshot+highlights | video | animation | slide | handout | quiz | interactive> · status: <brief | drafted | final> · owner: <editor | tool | human>
tool: <the script that produces it, from the "produce with" line of its type below>
voice: <voice name and register for anything with narration, e.g. a Korean neural voice, 존댓말, calm; draft voice / final voice if they differ; "none" for silent assets>
icon family: <one Iconify prefix and stroke for the whole lesson, e.g. lucide, 2 px; the same on every brief of this lesson; "none" if the asset has no icons>
export: PNG at 2x for anything with text (SVG only with fonts outlined or embedded; never SVG that relies on the phone's fonts)

File name: `media/<id>.md` beside the plan, with the id in the heading. `tools/lint.py` matches briefs to Media list rows by id and checks that lesson, segment and type here agree with the plan.

## Purpose

One sentence: what the learner understands or can do after seeing this that they could not before. If the sentence is "it looks nicer", the visual is not earning its place; cut it.

## Replaces

What text or talk this visual removes from the segment (a visual that adds to the words instead of replacing some is usually a finding).

## How it follows the multimedia rules

- parts first: <where the learner meets the names of the parts before this visual shows them working (an earlier still, the icon key, a one-line glossary); "n/a" for a single still>
- labels on the parts: <confirm every label sits on or next to what it names; no legend, no "see next slide">
- on-screen text: <key terms only; the voice or the teacher carries the sentence; captions stay on>
- chunks: <for anything that plays: where it pauses between ideas and who controls the pause>

## Spec by type

### diagram
- shows: <the mechanism: boxes, arrows, what flows where>
- labels: <every label, in the house-rule language>, ≤ 7 boxes
- reading order: <where the eye starts, then>
- layout: top to bottom for phones; short labels
- style: <house style / uiux taste; white card, large type, nothing outside boxes>
- produce with: `tools/diagram/render.py <this file>` (Mermaid with the house theme and a Korean font, PNG at 2x); inline SVG via the `diagram` skill only with fonts outlined

### icon set
- concepts: <one icon per recurring concept, ≤ 8>
- icons: <concept → icon name in the family, e.g. 받은편지함 → inbox>
- rule: one stroke weight, one family (the `icon family:` line above), each icon used at least twice in the lesson
- produce with: `tools/icons.py <this file>` (fetches from Iconify, caches in the lesson folder, refuses a second family)

### screenshot+highlights
- source screen: <app / site / window, exact state, light or dark theme, language>
- capture: <viewport or crop; phone width for online lessons; include the window chrome? yes/no>
- callouts (numbered, in order of action):
  1. <box or arrow> around <element> · label "<the instruction>"
  2. …
- hide: <any personal data, account names, keys>; blur or replace before publishing
- produce with: `tools/capture.py <this file>` for web pages (captures at phone width and writes the callout coordinates into the lines above), then `tools/highlight.py <shot.png> --spec <this file>` (boxes, arrows, numbered badges, blur regions); for desktop apps, a manual capture then `tools/highlight.py`
- a step with more than three callouts becomes two screenshots

### video
- length: <N> s (online lessons: 20 to 60 s per concept; never a full lecture). Any block runs about 6 minutes or less and ends in a retrieval question the learner answers on screen before the next block.
- storyboard, one row per beat; the voice cell talks about what the on-screen cell shows:

| t | on screen | voice / caption | note |
|---|---|---|---|
| 0–5 s | <…> | "<…>" | hook |
| … | <question on screen> | "<…>" | retrieval question, learner answers before continuing |

- captions: always, written from the script (the voice cells), not from speech recognition · music: none unless the brief says so
- produce with: `tools/narrate.py <this file>` (draft narration and an SRT caption file from the voice cells; switch to the final voice for published assets), then `tools/video/` (Revideo: storyboard rows to timed sequences with burned-in captions); stills for pause-and-do points with `tools/capture.py` and `tools/highlight.py`
- generated text-to-video: a hook of a few seconds at most, never for instruction

### animation
- shows: <the change over time, one idea per chunk>
- chunks: <chunk → what moves → where it pauses>
- produce with: `tools/video/` (Revideo) for narrated or captioned motion, `motion-anything` for motion inside a web page; narration through `tools/narrate.py`

### slide / handout
- one idea per slide; the headline is the idea as a sentence, not a topic
- max text per slide by age band; key terms on the slide, the sentence spoken or done
- design: follows `taste/README.md` → uiux taste when installed
- produce with: `tools/guide.py <plan.md>` for guide-mode step decks (one step per slide, the instruction as the headline, PDF and phone PNGs); `tools/templates/handout.typ` (Typst) for printable handouts with Korean typography

### quiz
- items: <question → options → correct answer → the feedback line for each wrong option>
- source: <the plan's check or retrieval segment it comes from>
- limits: Kahoot questions ≤ 95 characters, answers ≤ 60 (Korean counts by character)
- produce with: `tools/quiz_export.py <plan.md>` (Kahoot spreadsheet, Google Forms quiz, Anki cards for spaced review)

### interactive
- format: <LiaScript page for an online mission (SCORM for a company LMS) | tweego branching scenario>
- structure: <sections or passages, the choices, where each choice leads and what consequence the learner sees>
- produce with: `tools/interactive/` (LiaScript pilot or tweego pilot); Korean support is still being tested, so note anything that breaks

## Facts shown

Every number or claim visible in the asset, with its source. `[needs fact: ...]` for gaps; the asset carries a visible placeholder until filled.

## Alt text

<one or two sentences a screen reader can say>
