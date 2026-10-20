# video: storyboard to captioned MP4

`storyboard.py` turns the storyboard table in a media brief (`| t | on screen | voice / caption | note |`, see `templates/media-brief.md`) into a captioned MP4. The renderer is [Revideo](https://github.com/redotvideo/revideo) (MIT, no headcount clause), chosen over Remotion because Remotion's licence costs money for companies over three people.

## Setup (once)

```
cd tools/video
npm install            # Revideo 0.11.0; uses the installed Chrome, so the Puppeteer browser download can be skipped
```

Set `PUPPETEER_SKIP_DOWNLOAD=true` before `npm install` to skip the Puppeteer browser download. Needs Node 18+, ffmpeg and ffprobe on PATH, Chrome or Edge, and Python 3.10+ with Pillow for the fallback engine. `node_modules/` and `output/` are gitignored.

## Use

```
python tools/video/storyboard.py docs/lessons/<slug>/media/M3-video.md --out out.mp4
python tools/video/storyboard.py <brief.md> --out out.mp4 --audio <narrate.py out dir>
python tools/video/storyboard.py <brief.md> --out out.mp4 --size landscape --engine ffmpeg
python tools/video/storyboard.py <brief.md> --scene-only --scene scene.json
```

| flag | meaning |
|---|---|
| `--size` | `phone` 1080x1920 (default), `landscape` 1920x1080, or `WxH` |
| `--audio <dir>` | one MP3 per row. `tools/narrate.py` output (`row-01.mp3`, ...) is matched by table row number; its joined `narration.mp3` is ignored. Any other folder: one MP3 per row in name order, or the last number in each file name. Each row then lasts its MP3 plus `--gap` (default 0.4 s), and the clips are joined into the soundtrack. A row with no MP3 is silent and keeps its t column time. An `<name>.srt` beside a row's MP3 times that row's captions |
| `--engine` | `auto` (default: Revideo, then the ffmpeg engine if Revideo fails), `revideo`, `ffmpeg` |
| `--scene` / `--scene-only` | write the scene JSON (rows, timing, caption pages, layout) |
| `--font` | font family for Revideo (default Noto Sans KR when installed, else Malgun Gothic) |
| `--keep` | keep the work folder (frames, soundtrack, scene) |

## What each row becomes

- **t**: `0–5 s`, `5-12s`, `0:05-0:12` or a bare `4 s`. Rows play back to back; a t cell that does not start where the previous row ended is a warning.
- **on screen**: the text as a centred headline. A path ending in .png, .jpg, .webp, .svg or .gif (bare, in backticks, or `![](...)`), resolved against the brief's folder, shows that image on a white card, with the rest of the cell as a headline above it. Use `.hl.png` from `highlight.py` or PNG diagrams from `tools/diagram/`. A missing file shows `[image missing: name]` and a warning.
- **voice / caption**: burned-in captions in a dark pill near the bottom. Long captions are split into pages at sentence ends, then commas, then spaces (30 characters per page on phone, 40 on landscape), timed by character count across the row. Lines break at spaces, never inside a Korean word.
- **note**: kept in the scene JSON only.

The template's placeholder row (`<…>`) is skipped. The JSON summary prints the engine used, length, resolution, codecs, caption count and warnings; when `auto` fell back, `fallback_reason` says why.

## Engines

- **revideo**: `render.mjs` passes the scene JSON to `src/project.ts` / `src/scenes/storyboard.tsx` and renders headless with the installed Chrome (fades between rows). About 13 s for a 15 s phone video on this machine. Telemetry is off (`DISABLE_TELEMETRY=true`).
- **ffmpeg**: Pillow draws one frame per caption page, ffmpeg concatenates them (hard cuts, no motion). About 2 s. Cannot draw SVG; export PNG.

Both engines use the same layout numbers from the scene JSON, so the two outputs look alike.
