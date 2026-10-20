# Tools

Scripts the loop, the critics and the editor use for evidence and for producing media, instead of opinion. Python 3.10+ throughout. Each script says what is missing when a dependency is not installed.

## Gate (runs before the critics every cycle)

| script | used by | input → output |
|---|---|---|
| `timing.py <plan.md> [--mode live\|online\|video\|guide\|talk] [--band A..G] [--json]` | critic 01, critic 04, the gate | a lesson plan → minutes vs total and buffer, active vs passive, longest passive stretch and longest segment against the band caps, beats, channels. Exit 1 when a check fails. Stdlib only. |
| `lint.py <plan.md> [--house <lesson.md>] [--band A..G] [--json]` | the gate; sev-1 findings go to critic 01 | a plan plus the briefs in `media/` beside it → findings with severity, location, rule, issue and fix, plus stats. Exit 1 on any severity-1 finding. Stdlib only. |

The loop saves both outputs to `history/cycle-N/gate.json`, passes `--house` when the project has a `lesson.md`, and runs a short cycle (critic 01 and the editor) when either fails.

## Media

| script | used by | input → output |
|---|---|---|
| `highlight.py <shot.png> --spec <brief.md> [--out x.hl.png] [--scale 1] [--size 1] [--color #FF4D2E]` | critic 07, the editor | a screenshot plus a media brief → numbered boxes, arrows, label pills and blurred regions in one accent colour, `<name>.hl.png`. Pillow. |
| `capture.py <url\|file.html> --out shot.png [--width 390 --height 844] [--select CSS [--label T] [--arrow]]... [--mask CSS]... [--click\|--fill\|--press]... [--brief M2.md] [--highlight]` | the editor for screenshot briefs | a web page at phone width → the screenshot, callout lines with real coordinates written into the brief, private data masked before capture, optional `.hl.png`. Playwright on the installed Chrome. |
| `icons.py fetch <family> <name>... [--color] [--size 48] [--out dir] [--lesson plan.md] [--switch]` | the editor for icon sets | Iconify icons → SVG plus PNG at 2x, cached offline; one family per lesson, recorded in the plan header. resvg-py, or Chrome. |
| `diagram/render.py <file.mmd\|brief.md> --out x.png [--block 1] [--scale 2]` | the editor for diagram briefs | a Mermaid block → PNG at 2x with the house theme and a Korean font; warns over 7 boxes, on left-to-right flowcharts and on SVG output. mermaid-cli. |
| `guide.py <plan.md> --out guide.pdf [--png-dir dir] [--handout [file.pdf]] [--steps S1,S2]` | guide mode | a guide plan plus its `.hl.png` shots → a Marp step deck (PDF and phone PNGs) and a printable Typst handout; gaps become visible `[needs …]` placeholders. marp-cli, Typst. |
| `narrate.py <brief.md\|script.txt> --out <dir> [--voice ko-KR-SunHiNeural] [--engine edge\|google\|elevenlabs]` | video and animation briefs | the storyboard's voice column → one MP3 per row, a joined MP3, an SRT taken from the script (never speech recognition) and a manifest. edge-tts for drafts. |
| `quiz_export.py <plan.md> [--kahoot out.xlsx] [--forms out.json] [--anki out.txt] [--list]` | quiz briefs, the owner after a run | the plan's Q/A/W check items → Kahoot import sheet (95/60 character limits), Google Forms quiz body, Anki import file. openpyxl. |
| `video/storyboard.py <brief.md> --out x.mp4 [--audio <dir>] [--size phone\|landscape\|WxH] [--engine auto\|revideo\|ffmpeg]` | video briefs, critic 07 | the storyboard table → a captioned MP4 (1080x1920 by default) timed by the t column or by `narrate.py` MP3s. Revideo (MIT) with the installed Chrome; ffmpeg fallback. `npm install` in `tools/video` first. |
| `interactive/lia.py <plan.md> --out lesson.lia.md [--bundle]` | online mode | a plan → a LiaScript course with quizzes from the check items; SCORM via `npx @liascript/exporter@3.4.2--2.1.0 -i lesson.lia.md -f scorm1.2 -o lesson-scorm`. |
| `interactive/twine.py <scenario.md> --out scenario.html [--fetch] [--check]` | branching decision segments | a scenario (passages, choices, consequence, then verdict) → Twee 3 and HTML via tweego (`--fetch` downloads it). |

Setup on a new machine, once:

```bash
pip install pillow playwright resvg-py edge-tts openpyxl
npm i -g @mermaid-js/mermaid-cli @marp-team/marp-cli
winget install --id Typst.Typst
cd tools/video && npm install
```

Set `PUPPETEER_SKIP_DOWNLOAD=1` before the npm installs to reuse the installed Chrome instead of downloading a browser. Korean text needs Malgun Gothic or Noto Sans KR; every tool looks for both.

Run from anywhere: `python <skill-dir>/tools/timing.py docs/lessons/mail-triage-1/plan.md`.

## timing.py

Reads the plan's header line (`mode:`, `age band:`, `total: N min`, optional `buffer: N %`; `--mode` and `--band` override) and the Segments table: every row starting with `| S<n> |`, with the `min`, `beat` and `modalities` columns found by header name and falling back to position. A segment is active when its modalities include `do` or its beat is try / apply / check; everything else is passive. Buffers are live 10 %, talk 5 %, others none, unless the header sets `buffer: N %` (a fixed program rhythm with no slack); an `open` beat (break, free talk, Q&A the learners lead) counts as neither active nor passive, ends a passive stretch and is exempt from the single-segment cap; a total that misses the budget by more than one minute fails. Band caps (passive stretch / single segment) mirror `taste/age-bands.md`: A 3/8, B 5/12, C 7/15, D 10/20, E 12/20, F 15/25, G 10/15. Missing beats, an active-to-passive ratio under the band floor, unknown beats and rows without a modalities cell (treated as passive) are printed as `warn:` lines and do not change the exit code; timing and the two caps print `FAIL:` lines and exit 1. `--json` prints the same as one dict (`ok`, `failures`, `warnings`, per-segment rows) for the loop.

## highlight.py

Draws on a screenshot: rounded boxes (3 px stroke), arrows with a filled head, numbered circular badges (white number on the accent, at the box's top-left corner or the arrow's tail), an optional label next to a box (white text on an accent pill, above the box when there is room), blurred regions for personal data (box blur, radius 12), and an optional crop applied first. All coordinates are measured on the original screenshot; after a crop the tool shifts them for you. `--scale 2` multiplies every coordinate for a 2x capture, and `--size 2` doubles strokes, badges and labels so a 2x shot does not look thin. Arrow labels sit beside the badge at the tail, never on top of it.

With `--spec` it reads the brief's `screenshot+highlights` section and its numbered `callouts` list. Lines it understands, with `·` or `|` as the separator and quotes optional:

```
1. box 120,80,300,40 · "로그인 버튼을 누르세요"
2. arrow 400,300 -> 520,340 · "여기"
blur 10,10,200,30
crop 0,60,800,440
badge 640,120,3
```

A numbered line without coordinates (the template's placeholder) is skipped with a warning. The same shapes work inline without a brief: `--box x,y,w,h[,"label"]`, `--arrow x1,y1,x2,y2[,"label"]`, `--badge x,y,n`, `--blur x,y,w,h`, `--crop x,y,w,h`; inline callouts number on after the spec's. `--demo` renders a grey 800×500 test image with sample callouts (to `highlight-demo.hl.png` in the current directory, or `--out`) so the tool can be checked without a real screenshot.

Korean labels need a font with Hangul: the tool tries `C:/Windows/Fonts/malgun.ttf`, then Noto Sans KR in the usual Windows, Linux and macOS font folders, then Pillow's built-in font, which has no Hangul and will draw boxes instead of letters. Pass `--font <path.ttf>` to pick one yourself. The JSON it prints names the font it used.

## lint.py

Runs before the critics each cycle and turns mechanical problems into findings, so no critic spends tokens on them. House rules come from `--house`, else `lesson.md` in the current folder, else none (word checks off). The band comes from `--band`, else the plan header, else E.

Severity 1 (exit 1, handed to critic 01): a word the house rules forbid in a learner-facing line (an `instruction:` line or quoted text); a banned product name in a learner-facing line (names from the house "product names:" line; if it bans names but lists none, a built-in list of common AI product names is used and the output says so; Facts used and appendix sections are skipped); a Media list row without a `media/M<n>.md` brief, or a brief without a row; names that differ between a brief and the plan (slug, segment, file name vs heading, an M-id with no row); a segment without a `#### S<n>` detail block or without a real `instruction:` line.

Severity 2 (reported, exit code unchanged): 당신 as translationese; words per screen and per sentence over the band default (Korean counts 어절): A 12/8, B 40/12, C 50/15, D 60/20, E 50/15, F 60/20, G 30/12, house defaults that `words per screen: N` and `sentence length: N` lines in the house file override; Oak-style field limits (outcome over 30 words, more than 5 prior-knowledge items, misconceptions outside 1 to 3); a brief whose type differs from its row; more than one icon family; a brief without `tool:`; a narrated brief without `voice:`.

Stats, never failures: counts, the longest screen and sentence, outcome words, `[needs fact:` markers with locations. `--json` prints `{"findings":[...],"stats":{...}}`.

## capture.py

Phone-width screenshots in the installed Chrome (then Edge, then Playwright's Chromium) with a ko-KR locale. Each `--select` becomes one numbered callout line that `highlight.py` parses, such as `1. box 29,114,332,59 · "제목을 적으세요"`; `--label` and `--arrow` apply to the `--select` before them. Coordinates are screenshot pixels padded by `--pad` (6), so `highlight.py` needs no `--scale`. `--click`, `--fill` and `--press` run in the order given, so one page can produce every step of a flow. Masking happens in the page before the shot, so the raw PNG never holds the private data (blur by default, `--mask-mode paint` for a grey box). `--brief` replaces the callouts in the brief and writes a `- captured:` line; `--highlight` writes `<shot>.hl.png`. It warns on a selector that matches nothing, several elements or something outside the shot, and on more than three callouts per shot. Native desktop apps still need a manual capture plus `highlight.py`.

## icons.py

Families: lucide, ph (phosphor), tabler, heroicons, iconoir, material-symbols, ri (remix). `fetch` downloads from the Iconify API, caches to `tools/.cache/icons/`, and writes `<name>.svg` and `<name>@2x.png`. With `--lesson`, the first fetch records `icon family: <prefix>` in the plan header and a different family is refused (exit 2) unless `--switch` is given. An unknown name exits 1; `icons.py search <family> <query>` finds the right one.

## diagram/

`mermaid.json` sets the base theme, Malgun Gothic then Noto Sans KR, a white background, 20px type and top-down spacing. `theme.css` adds 2px strokes, rounded boxes, `word-break: keep-all`, `A:::accent` for the box to look at first and `B:::muted` for context boxes. A puppeteer config pointing at the installed Chrome or Edge is written to `tools/.cache/` on first run.

## guide.py and templates/handout.typ

Each Segments-table row becomes one step: the `- instruction:` line is the headline, the `- expected:` line is the result line, and the step's media `.hl.png` is the picture (found from the brief, then `media/<id>.hl.png` and its variants). A missing instruction or image becomes a visible placeholder and a warning; the tool never stops on a gap. The deck is an editable Marp file plus a 720x1280 portrait theme, rendered to PDF and, with `--png-dir`, one 1080x1920 PNG per slide. `--handout` fills `templates/handout.typ` (A4, `lang: "ko"`, a screenshot, badge, instruction, result line and writing lines per step) and compiles it with Typst.

## narrate.py

Reads the first table with a voice / caption column; rows with an empty voice cell are skipped and reported. The voice is `--voice`, else the brief's `voice:` line when it names a voice id, else `ko-KR-SunHiNeural`. Each row becomes one MP3; the joined file puts `--gap` seconds between rows. Caption text is the script; caption times come from the measured audio, and long rows split at sentence ends, then commas, then spaces. A row whose audio runs past its storyboard slot prints a `warn:` line. `edge` is free but GPL-3.0 and uses an undocumented Microsoft service, so it is for drafts. `google` (Chirp 3 HD) and `elevenlabs` are stubs that read keys from environment variables only and say what to set.

## quiz_export.py

Reads quiz items inside a segment's detail block (see `templates/lesson-plan.md`):

```
Q: <question>
A: <correct answer>                 two or more makes a pick-all question
W: <wrong option> (misconception: <the wrong belief it catches>)
T: 20                               optional seconds
F: <feedback that says what to do next>
```

`--kahoot` writes an .xlsx in Kahoot's import layout and leaves out (and lists, exit 1) any item over 95 characters for the question or 60 for an answer; Hangul counts one per syllable. `--forms` writes a Google Forms `batchUpdate` body plus a `.create.json`, with misconceptions labelled "흔한 오해" so they never read as fact. `--anki` writes a tab-separated import file tagged by slug and segment.

## video/ and interactive/

Full docs: [video/README.md](video/README.md) and [interactive/README.md](interactive/README.md). `storyboard.py` pages long captions and breaks lines only at spaces, so Korean words never split; with `--audio`, `narrate.py`'s `row-NN.mp3` files set each row's length and become the soundtrack. `lia.py` turns Q/A/W items into LiaScript quizzes (one A is single choice, several is multiple choice, no W is a text box) and marks missing media visibly. `twine.py` shows the consequence first and hides the verdict and the next choices behind a reveal link; it errors on links to unknown passages and warns on unreachable ones.

These are helpers. A critic still reads the plan and looks at the output; the scripts give it numbers to point at and assets to look at.
