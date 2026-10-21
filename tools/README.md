# Tools

Scripts the loop, the critics and the editor use for evidence and for producing media, instead of opinion. Python 3.10+ throughout. Each script says what is missing when a dependency is not installed.

## Gate (runs before the critics every cycle)

| script | used by | input → output |
|---|---|---|
| `timing.py <plan.md> [--mode live\|online\|video\|guide\|talk] [--band A..G] [--json]` | critic 01, critic 04, the gate | a lesson plan → minutes vs total and buffer, active vs passive, longest passive stretch and longest segment against the band caps, beats, channels. Exit 1 when a check fails. Stdlib only. |
| `lint.py <plan.md> [--house <lesson.md>] [--band A..G] [--json]` | the gate; sev-1 findings go to critic 01 | a plan plus the briefs in `media/` beside it → findings with severity, location, rule, issue and fix, plus stats. Exit 1 on any severity-1 finding. Stdlib only. |

`gate.py <plan.md> --out <history/cycle-N/gate.json> [--mode] [--band] [--house]` runs both with UTF-8 forced on the pipe (Korean otherwise breaks on Windows), saves `gate.json` with each tool's exit code and run time, prints a three-line summary and exits 1 when the cycle must be short. The loop saves both outputs to `history/cycle-N/gate.json`, passes `--house` when the project has a `lesson.md`, and runs a short cycle (critic 01 and the editor) when either fails.

## Run setup

| script | used by | input → output |
|---|---|---|
| `taste_digest.py --band B --mode M --out docs/lessons/<slug>/taste-digest.md [--owner f] [--project taste.md]` | the orchestrator at intake; every critic reads it | the owner's file whole plus the band's and mode's parts of `taste/` (band tables cut to one row) → one file, about two thirds the size of the six it replaces. Stdlib only. |

| `merge.py <history/cycle-N> [--gate gate.json] [--out merged.json] [--md merged.md]` | the orchestrator after the critics | every `critic-NN.json` (a code fence tolerated) → validated, blind pair mapped back, ids `c<N>-<NN>-<k>`, ranked, candidate duplicates listed; exit 1 when a critic file is invalid. Stdlib only. |

## Media

| script | used by | input → output |
|---|---|---|
| `highlight.py <shot.png> --spec <brief.md> [--out x.hl.png] [--scale 1] [--size 1] [--color #FF4D2E] [--no-badge] [--line …] [--pill …]` | critic 07, the editor | a screenshot plus a media brief → numbered boxes, arrows, headless tethers, label pills and blurred regions in one accent colour, `<name>.hl.png`. Pillow. |
| `capture.py <url\|file.html> --out shot.png [--width 390 --height 844] [--select CSS [--label T] [--arrow]]... [--mask CSS]... [--click\|--fill\|--press]... [--brief M2.md] [--highlight]` | the editor for screenshot briefs | a web page at phone width → the screenshot, callout lines with real coordinates written into the brief, private data masked before capture, optional `.hl.png`. Playwright on the installed Chrome. |
| `icons.py fetch <family> <name>... [--color] [--size 48] [--out dir] [--lesson plan.md] [--switch]` | the editor for icon sets | Iconify icons → SVG plus PNG at 2x, cached offline; one family per lesson, recorded in the plan header. resvg-py, or Chrome. |
| `diagram/render.py <file.mmd\|brief.md> --out x.png [--block 1] [--scale 2] [--landscape]` | the editor for diagram briefs | a Mermaid block → PNG at 2x with the house theme and a Korean font; warns over 7 boxes, on left-to-right flowcharts (top-down ones with `--landscape`, for a projected 16:9 slide, where a tall chain shrinks to unreadable) and on SVG output. mermaid-cli. |
| `guide.py <plan.md> --out guide.pdf [--png-dir dir] [--handout [file.pdf]] [--steps S1,S2]` | guide mode | a guide plan plus its `.hl.png` shots → a Marp step deck (PDF and phone PNGs) and a printable Typst handout; gaps become visible `[needs …]` placeholders. marp-cli, Typst. |
| `worksheet.py <data.json> --out x.pdf [--png] [--ppi 144]` | the editor for printable handout, worksheet and card briefs | a JSON sheet (header band, text, ruled table, checklist, fill-in fields, numbered strip, columns, panel, oval, writing lines, cut line, image, page break) → an A4 PDF through `templates/worksheet.typ`, one PNG per page, and a fit check that exits 2 when the sheet runs past its `pages` value. Typst. |
| `narrate.py <brief.md\|script.txt> --out <dir> [--voice ko-KR-SunHiNeural] [--engine edge\|google\|elevenlabs] [--trim-tail S]` | video and animation briefs | the storyboard's voice column → one MP3 per row, a joined MP3, an SRT taken from the script (never speech recognition) and a manifest. edge-tts for drafts; `--trim-tail S` cuts each clip's trailing silence (edge leaves ~0.95 s) down to S seconds. |
| `quiz_export.py <plan.md> [--kahoot out.xlsx] [--forms out.json] [--anki out.txt] [--list]` | quiz briefs, the owner after a run | the plan's Q/A/W check items → Kahoot import sheet (95/60 character limits), Google Forms quiz body, Anki import file. openpyxl. |
| `video/storyboard.py <brief.md> --out x.mp4 [--audio <dir>] [--size phone\|landscape\|WxH] [--engine auto\|revideo\|ffmpeg] [--theme k=#hex,…] [--bg #hex] [--srt x.srt]` | video briefs, critic 07 | the storyboard table → a captioned MP4 (1080x1920 by default) timed by the t column or by `narrate.py` MP3s; `--srt` writes the burned-in caption pages as an SRT on the final timeline (gaps and silent holds included); `stage: tall` in a row's note gives one tall picture the frame's height (caption bar pinned at the foot), and the scene JSON records each picture's scale. Revideo (MIT) with the installed Chrome; ffmpeg fallback. `npm install` in `tools/video` first. |
| `interactive/lia.py <plan.md> --out lesson.lia.md [--bundle]` | online mode | a plan → a LiaScript course with quizzes from the check items; SCORM via `npx @liascript/exporter@3.4.2--2.1.0 -i lesson.lia.md -f scorm1.2 -o lesson-scorm`. |
| `interactive/twine.py <scenario.md> --out scenario.html [--fetch] [--check]` | branching decision segments | a scenario (passages, choices, consequence, then verdict) → Twee 3 and HTML via tweego (`--fetch` downloads it). |

Setup on a new machine, once:

```bash
pip install pillow playwright resvg-py edge-tts openpyxl
npm i -g @mermaid-js/mermaid-cli @marp-team/marp-cli
winget install --id Typst.Typst
cd tools/video && npm install
```

Run marp-cli from a script or a non-interactive shell with `--no-stdin` (it otherwise waits on stdin and hangs; `guide.py` already passes it) and `CHROME_PATH` pointing at the installed Chrome. Set `PUPPETEER_SKIP_DOWNLOAD=1` before the npm installs to reuse the installed Chrome instead of downloading a browser. Korean text needs Malgun Gothic or Noto Sans KR; every tool looks for both.

Run from anywhere: `python <skill-dir>/tools/timing.py docs/lessons/mail-triage-1/plan.md`.

## timing.py

Reads the plan's header line (`mode:`, `age band:`, `total: N min`, optional `buffer: N %`; `--mode` and `--band` override) and the Segments table: every row starting with `| S<n> |`, with the `min`, `beat` and `modalities` columns found by header name and falling back to position. A segment is active when its modalities include `do` or its beat is try / apply / check; everything else is passive. Buffers are live 10 %, talk 5 %, others none, unless the header sets `buffer: N %` (a fixed program rhythm with no slack); an `open` beat (break, free talk, Q&A the learners lead) counts as neither active nor passive, ends a passive stretch and is exempt from the single-segment cap; a total that misses the budget by more than one minute fails. Band caps (passive stretch / single segment) mirror `taste/age-bands.md`: A 3/8, B 5/12, C 7/15, D 10/20, E 12/20, F 15/25, G 10/15. Missing beats, an active-to-passive ratio under the band floor, unknown beats and rows without a modalities cell (treated as passive) are printed as `warn:` lines and do not change the exit code; timing and the two caps print `FAIL:` lines and exit 1. `--json` prints the same as one dict (`ok`, `failures`, `warnings`, per-segment rows) for the loop.

## highlight.py

Draws on a screenshot: rounded boxes (3 px stroke), arrows with a filled head, numbered circular badges (white number on the accent, at the box's top-left corner or the arrow's tail), an optional label next to a box (white text on an accent pill, above the box when there is room), blurred regions for personal data (box blur, radius 12), and an optional crop applied first. All coordinates are measured on the original screenshot; after a crop the tool shifts them for you. `--scale 2` multiplies every coordinate for a 2x capture, and `--size 2` doubles strokes, badges and labels so a 2x shot does not look thin. Arrow labels sit beside the badge at the tail, never on top of it. `--line x1,y1,x2,y2[,x3,y3...]` draws a plain polyline with no head and no badge (a tether from a box to its label, with square corners at each turn), `--line-width px` sets its width in output pixels (default: the box stroke), and `--pill x,y,"label"` draws a label pill alone with its left end at x and its top at y, exactly where it is put; together they hang a label below text that has no room above it. `--no-badge` drops the number badges on boxes and arrows (explicit `--badge` items still draw) for briefs whose callouts are label pills only: a box label then starts at the box's left edge, and an arrow label sits on the arrow's tail on the side away from the head (below or above for a steep arrow, left or right for a flat one). Without the switch the output is unchanged.

With `--spec` it reads the brief's `screenshot+highlights` section and its numbered `callouts` list. Lines it understands, with `·` or `|` as the separator and quotes optional:

```
1. box 120,80,300,40 · "로그인 버튼을 누르세요"
2. arrow 400,300 -> 520,340 · "여기"
blur 10,10,200,30
crop 0,60,800,440
badge 640,120,3
```

A numbered line without coordinates (the template's placeholder) is skipped with a warning. The same shapes work inline without a brief: `--box x,y,w,h[,"label"]`, `--arrow x1,y1,x2,y2[,"label"]`, `--line x1,y1,x2,y2[,…]`, `--pill x,y,"label"`, `--badge x,y,n`, `--blur x,y,w,h`, `--crop x,y,w,h`; inline callouts number on after the spec's. `--demo` renders a grey 800×500 test image with sample callouts (to `highlight-demo.hl.png` in the current directory, or `--out`) so the tool can be checked without a real screenshot.

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

## worksheet.py and templates/worksheet.typ

A printable sheet as data. The JSON names `title`, `footer` (a small grey line, such as the material id), `pages` (the page count it must fit; the A4 fit check), `paper` (`a4`), `flipped`, `margin` (mm, a number or `{x, top, bottom}`), `size` (body pt, 11), `gap` (mm between blocks, 3.5), `colors` (`ink` #221F38, `accent` #D93D22, `paper`, `grey_fill`, `muted`, `rule`), `icons` (`{"brain": "icons/brain.svg"}`, paths relative to the JSON; stroke icons are recoloured on the fly) and `blocks`:

- `header` (title, meta, optional `fields` such as 이름 / 날짜 as write-on lines), `text` (`body`, or `lines` for several paragraphs; `fill`, `stroke`, `size`, `bold`, `color`)
- `table`: `columns` (`head`, `width` in mm or `"1fr"`, `align`, `number: true` for an auto row number), `prefill` rows, then `rows` empty rows at `row_height` (8 mm by default; anything under 7 mm is raised to 7 and reported)
- `checklist` (tick boxes), `fields` (labelled write-on lines, boxed fields, tally `boxes`, multi-line `lines`), `strip` (①[ ] → ②[ ] …, empty or with `items`), `oval`, `lines`, `cut`, `space`, `rule` (a hairline separator: `thickness` in pt, default 0.5, `color`, `width`)
- `image`: `src` (PNG, JPG or SVG, relative to the JSON), `width` and / or `height` (mm or `"100%"`; with both the picture keeps its aspect ratio inside that box), `align` (`left`, `center`, `right`), optional `alt` and `caption` (runs, in the muted colour). Use it for a picture drawn elsewhere (a `capture.py` shot of an HTML diagram, a `highlight.py` crop) so a slide and a sheet show the same picture
- `columns` (`widths`, `cols`: a block list each) and `panel` (`title`, `blocks`, `fill`, `stroke`, `height`) nest other blocks; `pagebreak` starts the next page, so a front and a back are one JSON

Text is a string or a list of runs: `{"text", "bold", "color", "size", "strike"}`, `{"blank": mm}`, `{"field": mm}`, `{"box": true}`, `{"tag": "3"}` (a value in an outlined box, to circle; optional `fill` for a filled tag with white text, `text` for the text colour, `radius` and `stroke` in pt for a rounded outline chip), `{"mark": "P"|"T"}` (the 처리 / 판단 chip: outline + word + repeat icon, filled accent + word + brain icon, so colour never carries the meaning alone), `{"icon": name, "size": pt}` (size optional, default the text size), `{"sp": mm}`, `{"br": true}`. Strings are printed as plain text, never as Typst markup, and Hangul breaks only at spaces (word-break: keep-all). Keys starting with `_` are ignored, so a JSON can carry its brief, its `[needs fact]` notes or a block held back until a fact arrives.

`worksheet.py` compiles with `typst compile --root` set to the folder shared by the template and the JSON, writes `<out>-1.png`, `<out>-2.png` … with `--png` (144 ppi, 2x), then reads the page count back with `typst query` and warns (exit 2) when the sheet runs to more pages than `pages`. Look at every PNG anyway: the fit check catches overflow onto a new page, not a cramped row.

## narrate.py

Reads the first table with a voice / caption column; rows with an empty voice cell are skipped and reported. The voice is `--voice`, else the brief's `voice:` line when it names a voice id, else `ko-KR-SunHiNeural`. Each row becomes one MP3; the joined file puts `--gap` seconds between rows. Caption text is the script; caption times come from the measured audio, and long rows split at sentence ends, then commas, then spaces. A row whose audio runs past its storyboard slot prints a `warn:` line. `edge` is free but GPL-3.0 and uses an undocumented Microsoft service, so it is for drafts. `google` (Chirp 3 HD) and `elevenlabs` are stubs that read keys from environment variables only and say what to set. `--trim-tail S` (off by default) cuts each clip's trailing silence (under -45 dB) down to S seconds with ffmpeg before anything is timed: edge ends every clip with about 0.95 s of silence, which adds up across a storyboard.

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

Full docs: [video/README.md](video/README.md) and [interactive/README.md](interactive/README.md). `storyboard.py` pages long captions and breaks lines only at spaces, so Korean words never split; with `--audio`, `narrate.py`'s `row-NN.mp3` files set each row's length and become the soundtrack. Ship the SRT that `--srt` writes, not `narrate.py`'s `narration.srt`: the latter is per-voice timing without the video's gaps and holds. `lia.py` turns Q/A/W items into LiaScript quizzes (one A is single choice, several is multiple choice, no W is a text box) and marks missing media visibly. `twine.py` shows the consequence first and hides the verdict and the next choices behind a reveal link; it errors on links to unknown passages and warns on unreachable ones.

These are helpers. A critic still reads the plan and looks at the output; the scripts give it numbers to point at and assets to look at.
