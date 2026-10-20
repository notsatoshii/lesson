# Tools

Small scripts the critics and the editor use for evidence instead of opinion. Both need Python 3.10+; `highlight.py` also needs Pillow (`pip install pillow`), nothing else. `timing.py` is stdlib only.

| script | used by | input → output |
|---|---|---|
| `timing.py <plan.md> [--mode live\|online\|video\|guide\|talk] [--band A..G] [--json]` | critic 01 (runnable), critic 04 (modalities), the loop gate | a lesson plan → segment minutes vs total and mode buffer (OK / OVER by n / UNDER by n), active vs passive minutes and ratio, longest passive stretch and longest segment against the band caps, beats present and missing, segments per channel (do / see / read / listen). Exit 1 when a check fails. |
| `highlight.py <shot.png> --spec <brief.md> [--out x.hl.png] [--scale 1.0] [--color #FF4D2E]` | critic 07 (media), the editor when it produces M-assets | a screenshot plus a media brief → the screenshot with numbered boxes, arrows, label pills and blurred regions drawn in one accent colour, written to `<name>.hl.png` beside the input |

Run from anywhere: `python <skill-dir>/tools/timing.py docs/lessons/mail-triage-1/plan.md`.

## timing.py

Reads the plan's header line (`mode:`, `age band:`, `total: N min`; `--mode` and `--band` override) and the Segments table: every row starting with `| S<n> |`, with the `min`, `beat` and `modalities` columns found by header name and falling back to position. A segment is active when its modalities include `do` or its beat is try / apply / check; everything else is passive. Buffers are live 10 %, talk 5 %, others none; a total that misses the budget by more than one minute fails. Band caps (passive stretch / single segment) mirror `taste/age-bands.md`: A 3/8, B 5/12, C 7/15, D 10/20, E 12/20, F 15/25, G 10/15. Missing beats, an active-to-passive ratio under the band floor, unknown beats and rows without a modalities cell (treated as passive) are printed as `warn:` lines and do not change the exit code; timing and the two caps print `FAIL:` lines and exit 1. `--json` prints the same as one dict (`ok`, `failures`, `warnings`, per-segment rows) for the loop.

## highlight.py

Draws on a screenshot: rounded boxes (3 px stroke), arrows with a filled head, numbered circular badges (white number on the accent, at the box's top-left corner or the arrow's tail), an optional label next to a box (white text on an accent pill, above the box when there is room), blurred regions for personal data (box blur, radius 12), and an optional crop applied first. All coordinates are measured on the original screenshot; after a crop the tool shifts them for you. `--scale 2` multiplies every coordinate for a 2x capture.

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

These are helpers. A critic still reads the plan and looks at the image; the script gives it numbers to point at.
