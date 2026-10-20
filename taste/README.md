# Taste

The brief says who the lesson is for and what they walk away with. It does not say what a good lesson feels like. Taste does, at these levels. Critics 02–09 and the editor load all of them before they read the plan, in this order; the earlier item wins where two disagree.

1. **The project's `taste.md`** (project root, see `examples/taste.md`): overrides for this one project or course. Absent → skip.
2. **The owner's taste file**: what this person likes and hates in teaching, across every course, as a log of their real decisions. Location: `$LESSON_TASTE` if set, else `~/.claude/lesson/taste.md`. Private; never in a project repo. See `owner-taste.md` for how it is seeded, captured and read. Absent → the skill offers `/lesson taste init` once, then continues.
3. **House rules** (`lesson.md`, CLAUDE.md): rules, not taste, but they bound it.
4. **`age-bands.md`** here: what works and what fails per age. A gate, not a preference.
5. **`references.md`** here: teaching that has held up, by mode and band, each with the mechanic to learn from. A bar, never a format to copy.
6. **`slop.md`** here: the tells of a default, dull lesson. Each present without a reason in the brief is an automatic finding.
7. **`defaults.md`** here: known-good segment lengths, beat shapes, feedback loops, game, story, humour, media and text defaults for when the brief is silent.
8. **Installed design skills**, when present in `~/.claude/skills/`: `uiux` (its `taste/` layer and owner file) for anything on a screen or a slide, `impeccable`, `dataviz` for charts, `diagram` for diagrams. Critic 09 and the editor read the parts that apply to the materials.

## The test taste must pass

A plan that follows the brief and has no slop can still be forgettable. Critic 06's 9 anchor is the taste bar for voice; critic 05's for engagement. To reach them the critic names, in its summary, which reference in `references.md`, the owner's file or the project's `taste.md` the plan comes closest to, and what the gap is. "Closest to nothing in particular" is a finding in itself.

## Keeping taste honest

- Taste never overrides the brief's outcome or the house rules. If the owner's file loves team quests and the brief is a one-person online mission, the brief wins and the critic says so.
- Taste never invents facts, curriculum or data. Story and jokes may be invented; facts may not.
- Taste is not a trend. `references.md` lists teaching that has worked for years, not this month's app.
- The owner's file records what the owner said and chose, quoted and dated. It never records a critic's or editor's guess about the owner.
