# 07 Media

Lens: are the visuals, diagrams, icons, screenshots and video planned where they earn their place, specified well enough that someone could produce them tomorrow, and free of invented data? Reads the Media list, every brief in `media/`, and the segment table's media column. Runs only once 01 Runnable holds ≥ 8.

## Checks

- **Every learn segment carries a mechanism visual:** each learn segment has at least one visual that shows how the thing works (a flow, a structure, a before/after, the screen itself). A stock image, a photo of people at laptops or a hero illustration does not count.
- **Every row has a brief:** each Media list id has a file from `templates/media-brief.md`. A row with no brief is a finding; a brief with no row is a finding.
- **Purpose passes the test:** the Purpose line answers "what can the learner now do or understand that they could not before". "It looks nicer", "breaks up the text" and "adds energy" fail. Quote the failing line.
- **Replaces line is real:** the brief names the words or talk the visual removes from the segment. A visual that adds to the words instead of replacing some is a finding unless the brief says why.
- **Diagrams:** at most 7 boxes; every label in the house-rule language; a stated reading order (where the eye starts, then where); nothing outside the boxes. Two boxes and one arrow is a sentence, not a diagram.
- **Icons:** one family, one stroke weight; each icon stands for one recurring concept and is used at least twice in the lesson. An icon used once is decoration. One concept with two different icons across materials is a finding.
- **Screenshots for install and how-to:** one screenshot per action step; numbered callouts in order of action; at most three callouts per shot (more becomes two shots); the expected result shown after each step; personal data, account names and keys hidden or replaced; source screen, state, theme and language named so the shot can be retaken.
- **Video:** 20–60 s per concept in online mode, never a full lecture; a storyboard with timings per beat; captions always; a pause-and-do point wherever it asks the viewer to act; voice and register named. "Record a walkthrough" with no storyboard is a finding.
- **Text that wants to be a picture:** a process, a comparison, a before/after, a structure or a set of options explained in prose is a finding, with the visual type named (flow, side-by-side, structure diagram, table). Quote the text.
- **Pictures that add nothing:** clip art, decorative photos, a diagram of two boxes, a screenshot with no callouts under a how-to step. Flag for removal, not redesign.
- **Numbers have sources:** every number, date or claim visible in an asset appears in the brief's Facts shown with a source, else `needs fact:` and a visible placeholder in the asset. Never fill the gap yourself.
- **Alt text present:** one or two sentences a screen reader can say, naming what the visual shows, not "diagram".
- **Phone and theme (online mode):** the asset reads at 390 px wide; labels survive at that size; it holds in dark and light where the house rules ask; colour is never the only signal.
- **Producible with the named tooling:** each brief says which tool makes it, and the tool is one noted at intake: `tools/highlight.py` for screenshot callouts (boxes, arrows, numbered badges, blur), the `diagram` skill or inline SVG for diagrams, `motion-anything` or a screen recording for video, `dataviz` rules for any chart. A brief that needs a tool the project does not have goes to `waiting on user`.
- **Status is honest:** brief / drafted / final matches what exists on disk.

## Prose that wants to be a picture

- steps in a paragraph → numbered flow, one box per step, arrows in reading order
- "unlike X, Y does…" → side-by-side, same rows for both
- "before this change… after it…" → paired screenshots or a two-column diagram
- parts of a whole, a hierarchy, what contains what → structure diagram, ≤ 7 boxes
- a list of options and when to use each → table with a "use when" column
- any number that changes or compares → chart under the `dataviz` rules, title stating the takeaway
- a screen the learner must find something on → screenshot with one callout

## Mode notes

- **guide:** mostly screenshots; expect one per numbered step, each followed by the expected result. A guide step with no screenshot is a finding unless the step is "read this".
- **live:** visuals are slides and physical props; the slide brief states one idea per slide, and every prop appears in the Materials table.
- **online:** every asset is read on a phone without a teacher; alt text, captions and label size matter more than anywhere.
- **video:** the whole lesson is storyboarded; every segment has its storyboard rows, and the stills for pause-and-do points are specified.
- **talk:** slides carry the story; one idea per slide, headline as a sentence, and the talk's callbacks appear visually.

## Anchors

- **4:** the plan has a learn segment with no visual or only a stock image; or Media list rows with no brief; or a diagram over 7 boxes or in the wrong language; or a how-to step with no screenshot, or a screenshot with five callouts; or an asset showing a number that has no source; or alt text missing throughout.
- **7:** the plan has a mechanism visual for every learn segment and a brief for every row; Purposes mostly pass the test; icons are one family; screenshots have numbered callouts and hidden personal data; one or two text passages still want to be a picture, or one brief lacks a Replaces line or a reading order; video has a storyboard but no pause-and-do point.
- **9:** the plan has no visual that could be removed without loss and no prose that should be a picture; every brief names what it replaces, its reading or callout order, its source, its tool and its alt text; every number is sourced or marked; the assets read on a phone in both themes; someone with the named tools and no further questions could produce the whole set tomorrow.
