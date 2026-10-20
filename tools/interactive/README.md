# interactive: LiaScript course and Twine scenario pilots

Two text-to-interactive routes: a plan becomes a LiaScript online course (SCORM for a company LMS), and a branching decision scenario becomes a playable Twine story. Python 3.10+, stdlib only.

## lia.py: plan to LiaScript

```
python tools/interactive/lia.py docs/lessons/<slug>/plan.md --out docs/lessons/<slug>/lia/lesson.lia.md --bundle
```

One section per row of the plan's Segments table: title, what happens, the instruction from Segment detail (as a quote), the segment's media, its check items as quizzes, and the transition line. Teacher-only fields (materials, fast / slow / wrong) are left out. The header sets `language: ko` and `narrator: Korean Female` (change with `--language`, `--narrator`).

Check items go in a segment's detail block, one field per line or on one line joined with ` / `:

```
- check:
  - Q: 규칙을 만들 때 가장 먼저 볼 기준은 무엇인가요?
  - A: 보낸 사람
  - W: 메일 길이 :: 길이는 같은 사람이 보내도 매번 달라집니다.
  - H: 매번 바뀌지 않는 것을 고르세요.
  - why: 보낸 사람은 메일마다 바뀌지 않아서 첫 기준으로 가장 안정적입니다.
- check: Q: 안 읽은 메일은 몇 통이었나요? / A: 128
```

| field | becomes |
|---|---|
| `Q:` | the question (bold) |
| `A:` | correct option; one A = single choice `[(X)]`, two or more = multiple choice `[[X]]`; A with no W = text input `[[answer]]` |
| `W:` | wrong option; `text :: feedback` adds answer-specific feedback |
| `H:` | hint `[[?]]`, any number |
| `why:` | explanation in the solution block, shown once the quiz is solved |

Options are written in a stable shuffled order and marked `<!-- data-randomize -->`, so LiaScript shuffles them again per learner.

Media ids come from the segment's media cell and the Media list. Files are looked up in `media/` beside the plan (or `--media-dir`): `<id>.hl.png`, then `<id>*.png/.jpg/.webp/.svg/.gif`, then `.mp4` (embedded as video `!?[]()`) and `.mp3` (audio `?[]()`). Alt text comes from the brief's `## Alt text` section (`media/<id>*.md`), else the Media list purpose. A missing file becomes a visible `[media needed: M9 · purpose]` line and a warning. `--bundle` copies the media used into `<out folder>/media/`, so that folder holds only the course.

### Export to SCORM

```
npx @liascript/exporter@3.4.2--2.1.0 -i docs/lessons/<slug>/lia/lesson.lia.md -f scorm1.2 -o lesson-scorm
```

Tested 2026-10-20: writes `lesson-scorm.zip` (7.8 MB, 660 files, UTF-8 Korean title in `imsmanifest.xml`, media included). The exporter packs the input file's whole folder, so export from a folder that holds only the course (use `--bundle`). Other formats: `-f scorm2004`, `-f web`, `-f pdf`, `-f epub`; `-f presets --moodle` lists LMS presets. The first `npx` run downloads the exporter (about 45 s).

## twine.py: scenario to Twine

```
python tools/interactive/twine.py scenario.md --out scenario.html --fetch
python tools/interactive/twine.py scenario.md --check
```

Scenario format:

```
# 회의록 요약 맡기기
start: 시작
format: sugarcube
reveal label: 판정 보기
verdict labels: 좋은 선택 / 아쉬운 선택 / 생각해 볼 선택

## 시작 · 금요일 오후 5시
팀장님이 회의록 요약을 30분 안에 달라고 합니다.
- 초안을 그대로 보낸다 -> 그대로
- 숫자만 원문과 맞춰 본다 -> 확인

## 그대로 · 월요일 회의
consequence: 팀장님이 회의에서 틀린 숫자를 그대로 읽었습니다.
verdict: bad · 숫자는 원문과 한 번 맞춰 봐야 합니다.
- 처음부터 다시 -> 시작
```

- `## <id> · <title>`: a passage. The id is the link target; the title is shown as a heading.
- Plain lines: the body.
- `consequence:` what happened because of the choice that led here. Shown first.
- `verdict: good|bad|mixed · <why>`: hidden behind the reveal link, shown after the consequence. When a passage has a verdict, its choices appear only after the reveal.
- `- <label> -> <target id>`: a choice. A passage without choices is an ending.
- Header lines (all optional): `start:` (default the first passage), `format:` `sugarcube` (default) or `harlowe`, `reveal label:`, `verdict labels:` (good / bad / mixed).

Errors (exit 1): a choice to an unknown passage, a missing start passage, duplicate ids. Warnings: unreachable passages, endings without a verdict, a verdict without a consequence.

Output: `<out>.twee` (Twee 3, stable IFID per title, a stylesheet with Korean fonts and coloured consequence and verdict boxes) and, when tweego is found, the compiled HTML. tweego is looked up at `--tweego`, then `tools/interactive/bin/tweego.exe`, then PATH. `--fetch` downloads the tweego 2.1.1 release zip from github.com/tmedwards/tweego into `bin/` (gitignored; includes SugarCube 2, Harlowe 3 and other story formats). Without tweego the reply prints the compile command: `tweego -o scenario.html scenario.twee`.

Default Korean labels (`판정 보기`, `좋은 선택`, `아쉬운 선택`, `생각해 볼 선택`) are placeholders for review; override them in the scenario header.
