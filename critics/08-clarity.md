# 08 Clarity and age fit

Lens: is every learner-facing word understandable for the band, unambiguous, in the right language and register, and does the learner always know where they are and what to do next? Runs from cycle 1. Reading level applies to learner-facing text only; teacher and app notes are exempt from the reading level but not from clarity.

Clear is not the same as smooth. In a 364-student randomised study, physics videos that stated and refuted the common wrong belief beat clear exposition (effect sizes 0.79 and 0.83), even though students called the better versions "confusing" (Muller et al.). Do not reward a segment for reading easily if it never names the idea learners walk in with.

## Checks

- **Reading level per band:** the reading column of `taste/age-bands.md`. Sentence length, word choice, concrete over abstract. A: pictures first, one short sentence per screen. B: ≤ 40 words per screen, concrete nouns. C: plain prose, every term defined once. E: plain language, phone-readable, jargon only after it is defined. G: larger type, one idea per screen, no acronyms. Quote the longest sentence and the most abstract noun in the plan.
- **Korean by structure, not by score:** for Korean text, judge with structural proxies only: the 어절 count of the longest learner-facing sentences (quote the sentence and its count; `tools/lint.py` reports sentence length per band), 한자어 and 외래어 density against the band, terms defined on first use, and the translationese tells below. Never state or imply a Korean readability score or grade: no public, validated Korean readability formula exists (the best research model, KAIST's KRIT, reaches 0.746 accuracy on textbook grades), and the skill cannot compute one. Any 어절 threshold the loop applies is a house default; say so.
- **One idea per sentence:** each learner-facing sentence carries one idea (문장당 하나의 정보). A sentence that joins two instructions, a rule and its exception, or a definition and an example with ~고 / ~며 / ~는데 chains is a finding at its line; give the split as the fix.
- **Terms defined once, before use:** every new term has a definition the first time it appears, and an ELI5 analogy where the band (C, E, G) or the house rules ask for one and the brief's prior-knowledge line says the learner is new to it. A term defined after its third use, or defined twice differently, is a finding.
- **No undefined acronyms:** none at all for A, B and G. For the rest, expanded on first use.
- **Wrong idea voiced:** for each misconception the plan names (critic 02's misconceptions check), the learner-facing text states the common wrong idea out loud before the explanation (a line such as "많은 분이 처음에는 ~라고 생각하십니다", a character who holds it, a prediction that invites it) and then shows why it fails. A smooth, correct explanation that never voices the wrong idea is a finding: severity 2 when the check segment depends on that misconception, 3 otherwise. Ask "is the common wrong idea voiced?", not only "is the right idea clear?".
- **Instructions are imperative:** one action per sentence, in the order the learner does it, addressed to the learner. "You will want to open the settings before you save" is two actions in the wrong order. "Discuss" and "explore" are not actions.
- **Numbers and steps always visible:** in guide and online modes the step number and the total are on every step and screen. A learner who looks up from the phone and back must find their place in one glance.
- **Where am I, what is next:** every segment shows its title, progress and time left (online) or the teacher says them (live); every transition line names what comes next. A learner should never wonder whether the activity has started.
- **House-rule language and register, natively:** obey `lesson.md` and CLAUDE.md. For Korean: 존댓말 where required; no 당신; no noun stacks carried from English; no idioms translated word for word; no 보장 / 반드시 promises where forbidden; sentence rhythm a Korean writer would produce from the intent, not from an English draft. Quote the line and give the native rewrite as the fix. When the copy is the user's under a "copy may not change" rule, the line stays unchanged: list the rewrite as a proposal the loop does not apply, so it reaches final.md for review.
- **Forbidden words and banned product names:** absent from every learner-facing line, caption, label and alt text. Check the media briefs too. Severity-1 hits from `tools/lint.py` go to critic 01; confirm here only what lint cannot see (a forbidden idea phrased without the forbidden word).
- **Ambiguity hunt:** any sentence a learner could read two ways; any pronoun with two possible referents; any instruction that depends on something not yet shown ("click the button" before the screenshot that shows it); any "it" or "this" opening a step. Quote each.
- **Consistency of names:** the same thing is called the same thing everywhere: plan, instructions, media labels, callouts, worksheet, app copy. A button named 저장 in the screenshot and 저장하기 in the step is a finding.
- **Examples from the band's world:** B examples are not office examples; E examples are the learner's work this week, not a school project; G examples do not assume a smartphone habit the brief did not state.
- **Text accessibility:** contrast assumptions stated for screens; captions on all video; meaning never carried by colour alone; screen-reader order matches the visual order on online screens; type size per band (bigger for A–B and G).
- **Words per screen:** the text on a screen or slide fits the band's cap. 01 owns the clock; this critic owns the word count.
- **Pilot reader named:** the plan names one pilot reader at the younger edge of the band who reads the learner-facing text before delivery: a person, or a role and age the owner can fill (for example "a first-year employee on the target team, 24"), plus what they read and what counts as passing (they can say what each step asks without help). This is the only real test of reading level the loop cannot run itself. Missing is severity 2; the editor closes it by adding the line, with a marked placeholder if no person is known.

## Translationese tells (Korean house rules)

- 당신 or 그 / 그녀 standing in for an English subject or pronoun
- a stack of ~의 / ~에 대한 nouns where a Korean writer would use a verb
- ~되어지다 and other doubled passives
- "~할 수 있습니다" on every line as a filler for "you can"
- an English idiom carried over word for word
- exclamation marks and cheer where 존댓말 would stay level
- a sentence that only makes sense once you reconstruct the English behind it

## Mode notes

- **live:** the teacher's spoken lines are learner-facing; check them as text. Slides carry fewer words than the teacher says. The wrong idea can be voiced by the teacher asking the room to predict before the explanation.
- **online:** every screen is read alone on a phone; no sentence may rely on a teacher to explain it.
- **video:** captions are the text; check the caption track at the band's reading pace, and check that on-screen text uses the same names as the voice. A refutation (wrong idea stated, then tested) beats a polished monologue.
- **guide:** numbered steps, one action each, the expected result after each step in a sentence the learner can compare with their own screen.
- **talk:** slides are the learner-facing text; speaker notes are teacher notes and exempt from the reading level.

## Anchors

Each anchor has quoted example segments in `critics/examples/08-clarity.md` (sections `## 4`, `## 7`, `## 9`) and good / bad pairs per check under `## Pairs`. Compare the plan with those segments before placing it.

- **4** (see `critics/examples/08-clarity.md` `## 4`): the plan has learner-facing text above the band's reading level (quoted sentence), or a term used before it is defined, or an undefined acronym in a band that allows none; or instructions that bundle actions or run out of order; or Korean that reads as translated (당신, a noun stack, a carried idiom, a 보장 promise); or a forbidden word or banned product name present; or a step that depends on something not yet shown; or a Korean readability score claimed that nothing computed.
- **7** (see `critics/examples/08-clarity.md` `## 7`): the plan has text at the band's level with terms defined on first use; instructions are imperative and ordered; language and register obeyed, with one or two lines that still read as translated, carry two ideas, or one name that changes between step and screenshot; the learner knows where they are in most segments; one ambiguity found; the explanation is clear but the main wrong idea is not voiced, or no pilot reader is named.
- **9** (see `critics/examples/08-clarity.md` `## 9`): the plan has no sentence a learner in the band could read two ways; one idea per sentence, with 어절 counts quoted for the longest lines; every term is defined once, before use, with the analogy the band asks for; each named misconception is voiced in learner-facing words before it is corrected; every step shows its number and its expected result; names match across plan, media and app copy to the character; the Korean (or house language) reads as written by a native from the intent; a named pilot reader at the younger edge of the band could follow it alone on a phone without asking anyone.
