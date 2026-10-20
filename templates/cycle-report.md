# <lesson title> · cycle <N>

date: <YYYY-MM-DD HH:MM> · bar: <N> · cap: <N> cycles · mode: <…> · band: <…> · active critics: <ids> · run: <full | short (gate failed)> · snapshot: docs/lessons/<slug>/history/cycle-<N>/

gate: timing <OK | OVER n | UNDER n> (<s> s) · lint <clean | n sev-1, n sev-2, n sev-3> (<s> s) · active:passive <a:b> · longest passive <n> min (<ids>)
words: <n> (Δ <+/-n> vs cycle <N-1>) · tokens: <this cycle> / <run total> / <cap>
best so far: cycle <K> (<n> sev-1, <n> sev-2, score sum <n>)

## Scores

Comparison is the blind A/B verdict mapped back: `better` only when both reads agree.

| critic | run | cycle N-1 | cycle N | checks pass / fail / n/a | comparison | anchor quoted | weakest |
|---|---|---|---|---|---|---|---|
| 01 runnable | full/delta | | | | better/same/worse | "…" | S? · why |
| 02 learning design | | | | | | | |
| 03 practical | | | | | | | |
| 04 modalities | | | | | | | |
| 05 engagement | | – | | | | | |
| 06 story | | – | | | | | |
| 07 media | | – | | | | | |
| 08 clarity | | | | | | | |
| 09 design | | – | | | | | |

## Findings

Votes = how many critics raised it independently (owner first).

### Fixed this cycle
- [sev] [votes] [owner, +others] location · issue → what was done · new text at <segment · field> · id: c<N>-<NN>-<k> (ids: … when merged)

### Open (carried to next cycle)
- [sev] [votes] [owner, +others] location · issue · why still open · id: c<N>-<NN>-<k>

### Closure of last cycle's fixes
closed <n> · still open <n> · regressed <n>
- regressed: location · what broke

### Disagreements
| location | critic | says | critic | says | settled by |
|---|---|---|---|---|---|
| <S?> | <NN> | <…> | <NN> | <…> | hard limit / brief / lower number |

## Decisions the loop made

One line each. Listed again, deduped, in `final.md` for review after the run.

- <call> · chose: <option> · why: <rule or source> · affects: <segment>

## Needs fact

- <S? | M?> · [needs fact: <what>] · where it would come from: <file or person>

## Proposed rewrites (locked copy, not applied)

- <location> · current: "<…>" · proposed: "<…>" · why: <…>

## Media

| id | type | segment | status | produced with |
|---|---|---|---|---|

## Editor's note
<segments changed, minutes moved from where to where, conflicts and the rule that settled each, decisions it made itself, timing and lint output, what it noticed>

## Ideas (from 09, not built)
- <what> · <why it serves the outcome> · <cost>

## Decision
<continue to cycle N+1 | stop: bar | stop: plateau | stop: cap (cycles) | stop: cap (tokens)> · <one line of reason> · <delivered: this cycle | restored cycle K>
