# Calibration: the owner's verdicts on the critics

For the owner, not for critics: critics never load this file. It explains how the owner's verdicts on real findings become the yardstick for the critics, without the loop ever stopping to ask.

No study validates an AI judge on written lesson plans against teacher ratings, so the owner's own verdicts are the only ground truth the loop has. Criteria also drift: people find their standards by grading outputs, and any model or prompt change can shift them (Shankar et al. 2024). Labelling is how both get caught.

## What the loop does (no questions, no pauses)

- Every finding gets an id: `c<cycle>-<critic NN>-<k>`, where `k` is the finding's 1-based position in `history/cycle-<cycle>/critic-<NN>.json`. Example: `c2-05-03` is critic 05's third finding in cycle 2.
- The cycle report prints the id at the end of each finding line (` · id: c2-05-03`). A finding several critics raised lists every id (` · ids: c2-05-03, c2-07-01`).
- `final.md` ends with a short "Calibrate" block: the label line format below and the path to `evals/calibration.json`. Nothing waits for an answer. The owner labels after the run, or never.

## What the owner does (optional, any time after a run)

One line per finding, prefixed with the lesson's slug:

```
<slug>/c<cycle>-<NN>-<k> valid
<slug>/c<cycle>-<NN>-<k> invalid: <optional one-line reason>
<slug>/c<cycle>-<NN>-<k> sev <1|2|3>: <optional reason>
```

- `valid`: right finding, right severity.
- `invalid`: not a real problem, or not this critic's to raise.
- `sev N`: real problem, wrong severity; N is the severity it should have had.

Examples:

```
mail-triage-1/c2-05-03 valid
mail-triage-1/c2-07-01 invalid: the brief allows a timer in this game
mail-triage-1/c1-08-04 sev 3: a long sentence here is polish, not a blocker
```

Lines go to the loop in chat (`/lesson calibrate <lines>`), or into a text file the owner keeps. Either way they end up in `evals/calibration.json` through:

```
python evals/calibrate.py add labels.txt --root <project folder>      # or: add --line "<one line>"
```

`--root` is the project that holds `docs/lessons/`; the script copies each finding's severity, location and issue from the critic's JSON so the label still makes sense after the lesson changes. A later label for the same id replaces the earlier one.

## Reading it

```
python evals/calibrate.py report
```

Per critic: labels, valid, invalid, wrong severity, **precision** (valid / all labels) and **location precision** (valid + wrong severity / all labels). A critic with at least 5 labels and precision under 80 % is listed as under threshold, and the command exits 1.

- Under 80 %: rewrite that critic's Checks and anchor examples (`critics/NN-*.md`, `critics/examples/NN-*.md`), not the loop. Then run the evals (`evals/README.md`) and label the next run's findings for that critic.
- Low precision but high location precision: the critic finds the right places and misjudges severity; fix its severity lines first.
- The 80 % line and the 5-label minimum are house defaults, not research numbers; change them in `evals/calibration.json` (`threshold`, `min_labels`).

## When to label

- First pass: about 30 findings from past cycle reports, a mix of critics. Practitioner guidance is to start with about 30 labelled examples to find failure modes (Husain), and to keep labels binary, because "people don't know what to do with a 3 or 4".
- Again after a model upgrade or a rubric rewrite. Each entry records the rubric file's git hash when it was labelled; the report warns when one critic's labels span several rubric revisions, so old labels can be retired.
- Never as a gate: an unlabelled run is a normal run.

## Where the numbers live

`evals/calibration.json`: the schema is at the top of the file; the two entries marked `"example": true` are examples and the report ignores them. The planted-defect suite in `evals/` is the other half of the check: it tests whether critics find what they should, while calibration tests whether what they find is real.
