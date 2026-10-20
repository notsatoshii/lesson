# Evals: do the critics find what they should?

A rubric edit or a model upgrade can make a critic miss things, or invent them. This folder is the check: six fixed lesson plans with planted defects plus a clean control, in the `claude plugin eval` layout, and a calibration file of the owner's verdicts on real findings.

## The cases

| case | critics run (`--only`) | planted defect | graders expect |
|---|---|---|---|
| `planted-overtime-lecture` | 01, 04 | band C live plan 12 min over budget; S2 is a 20-minute lecture | sev-1 timing finding; sev 1 or 2 at S2 |
| `planted-agenda-leaderboard` | 05 | band B: the hook is an agenda read aloud; 10 points for attendance; S6 public individual leaderboard | sev 1 or 2 at S1 (hook), on attendance points, at S6 or Game layer (leaderboard) |
| `planted-statistic-guarantee` | 01, 08 | Korean band E: an invented statistic in S2; a 보장 promise in S6 (forbidden in `lesson.md`) | sev 1 at S2; sev 1 at S6 |
| `planted-media-no-brief` | 01, 07 | Media list row M3 has no `media/M3.md` | sev 1 or 2 at M3 |
| `planted-translationese` | 01, 08 | Korean band E written as translated English: 당신 (forbidden) in every instruction, noun stacks, 되어지다 | sev 1 at S1; sev 1 or 2 at S2 |
| `control-clean` | all nine | none; written to sit at a true 8 | no sev-1 anywhere (regex and an `llm` judge) |

Each case folder holds:

- `prompt.md`: runs `/lesson docs/lessons/<slug>/plan.md --skip-interview --cycles 1 --only <critics>`.
- `case.yaml` + `scaffold.sh`: copies `workspace/` (plan, brief, media briefs, `lesson.md` where the case has house rules) into the run's empty workspace. `scaffold.sh` is generated; edit `workspace/` and run `python evals/check_fixtures.py --build`.
- `workspace/`: the fixture. Every fixture has its own `brief.md`, so `--skip-interview` never needs to ask anything. All people, companies and scenarios are fictional; the one invented statistic is planted on purpose and is labelled as invented in that case's grader, not in the fixture.
- `graders/`: `cycle-report-exists` (`file_exists` on `cycle-1.md`), `ran-timing` (`tool_used` Bash with `timing.py`), `found-*` (`regex` on the cycle report: a finding line with the expected severity and location), `critic-NN-*` (`regex` on that critic's `history/cycle-1/critic-NN.json`, so each critic is graded on its own planted defect), and for the control `no-sev1-regex` plus `no-sev1-judge` (`llm`, passes on two of three votes). The comments at the top of each grader say what was planted.

The regex graders assume the cycle report's finding lines start `- [<severity>] ...` with the location on the same line, as `templates/cycle-report.md` shows. If that template changes, update the patterns and the samples in `check_fixtures.py`.

## Check the fixtures without Claude

```
python evals/check_fixtures.py
```

Runs `tools/timing.py` and `tools/lint.py` on every fixture and confirms the mechanical defects are exactly the planted ones (only the over-time fixture fails timing; lint finds the 보장, 당신 and missing-brief hits; the control is clean), checks every `scaffold.sh` against its `workspace/`, runs each regex grader against a sample finding line it must match and planted graders against a control sample they must not match, and checks the trigger queries. Exit 0 when all hold. Run it after editing any fixture, grader or tool.

## Run the suite

Needs Claude Code 2.1.269 or later, and the repo loadable as a plugin (a `.claude-plugin/plugin.json`; check with `claude plugin validate .`). From the repo root:

```
claude plugin eval . --scaffold --allow-tools Write Edit Bash --ablation none --runs 3
```

- `--scaffold` is required: without it the workspace is empty and every case fails.
- `--allow-tools Write Edit Bash`: the loop writes the cycle report and critic files and runs `timing.py` and `lint.py` through Bash.
- **Bash on Windows needs WSL2.** A run that grants Bash is refused on native Windows (no sandbox backend), so run the suite from WSL2, with the repo on a path outside the WSL home folder (for example `/mnt/c/Users/<you>/innovlabs/lesson`), because the sandbox hides the home folder. On Linux, install `bubblewrap` and `socat` first.
- `--ablation none` skips the no-plugin baseline. The baseline cannot run `/lesson` at all, so it only adds cost here.
- One case while iterating: `claude plugin eval . --case planted-media-no-brief --runs 1 --scaffold --allow-tools Write Edit Bash --ablation none`.
- Cost: each run is a real loop cycle (the control runs all nine critics). Set `--max-cost-usd`, and pin `--model` and `--judge-model` when comparing runs over time, so a model change is not mistaken for a rubric change.

Read `evals/results/<timestamp>/report.html` (git-ignored). A `found-*` grader that fails means the defect was missed by every critic; a `critic-NN-*` grader that fails means that critic missed its own defect.

Known interaction: when `timing.py` or `lint.py` fails, `loop/orchestration.md` runs a short cycle with critic 01 only. Four fixtures fail the gate on purpose, so `--only` has to take precedence over the short-cycle rule for the `critic-04`, `critic-07` and `critic-08` graders to pass. If they fail while the `found-*` graders pass, check that rule first.

## Score spread on the control

A critic whose score on the unchanged control moves by more than one point across three runs has anchors too vague to gate on. Keep the run folders and compare:

```
claude plugin eval . --case control-clean --runs 3 --scaffold --allow-tools Write Edit Bash --ablation none --keep-temp
python evals/spread.py <run folder 1> <run folder 2> <run folder 3>
```

`spread.py` prints each critic's scores and flags any spread above 1 (exit 1).

## Trigger test

`trigger-queries.json` holds 20 realistic requests, 10 that should start `/lesson` and 10 near misses (translation, the design loop, a Kahoot quiz with no lesson, a deck, grilling) that should not. It is in the format of skill-creator's trigger scripts:

```
PYTHONUTF8=1 python <skill-creator>/scripts/run_eval.py --eval-set evals/trigger-queries.json --skill-path . --runs-per-query 3
```

`PYTHONUTF8=1` matters on Windows: the script reads the file without an encoding, and the Korean queries fail under the default code page. To tune the skill's `description`, use the same file with `run_loop.py` (it splits train and test sets itself).

## Calibration

`calibration.json` holds the owner's verdicts on real findings (valid, invalid, wrong severity); `calibrate.py report` turns them into per-critic precision and lists critics under 80 %. How and when to label: `taste/calibration.md`.

```
python evals/calibrate.py add labels.txt --root <project folder>
python evals/calibrate.py report
```
