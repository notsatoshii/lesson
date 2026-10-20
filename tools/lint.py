#!/usr/bin/env python3
"""Mechanical lint of a lesson plan and its media briefs (stdlib only).

Usage: python lint.py <plan.md> [--house <lesson.md>] [--band A..G] [--json]

Runs before the critics each cycle. Checks the plan and the briefs in `media/` beside it for:
forbidden words and banned product names from the house rules, 당신 (translationese), media rows
without briefs and briefs without rows, names that differ between the plan and its briefs,
segments without a detail block or a written instruction, words per screen and sentence length
per age band on learner-facing lines, Oak-style field limits (outcome, prior knowledge,
misconceptions), and counts `[needs fact:` markers. Severity 1 findings go to critic 01 and make
the exit code 1; severity 2 findings are reported and do not change it.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Words per screen / words (Korean: 어절, counted by spaces) per sentence on learner-facing lines.
# House defaults derived from taste/age-bands.md (A: one short sentence per screen, B: <= 40 words
# per screen, G: one idea per screen); not research numbers. The house file can override them
# with "words per screen: N" and "sentence length: N" lines. Findings on these are severity 2.
READ_CAPS = {"A": (12, 8), "B": (40, 12), "C": (50, 15), "D": (60, 20), "E": (50, 15), "F": (60, 20), "G": (30, 12)}
DEFAULT_BAND = "E"
# Oak National Academy's lesson-plan field limits (Aila body.ts): outcome <= 30 words,
# <= 5 prior-knowledge statements, 1-3 misconceptions.
OUTCOME_MAX_WORDS = 30
PRIOR_MAX_ITEMS = 5
MISCONCEPTIONS_RANGE = (1, 3)
# Used only when the house file has a "product names:" rule that bans names but lists none.
BUILTIN_PRODUCTS = [
    "ChatGPT", "OpenAI", "GPT-4o", "GPT-4", "GPT-5", "Claude", "Anthropic", "Gemini", "Bard",
    "Copilot", "Perplexity", "Midjourney", "Notion AI", "Clova X", "HyperCLOVA", "Wrtn",
    "챗GPT", "챗지피티", "클로드", "제미나이", "코파일럿", "퍼플렉시티", "뤼튼",
]
TRANSLATIONESE = {"당신": "Drop the pronoun (Korean leaves the subject out) or use the role, e.g. 여러분 or 팀장님."}
PROMISE_FIX = {w: "Rewrite as a range or a measurement; no absolute promise." for w in ("보장", "반드시", "확실히", "100%")}
SKIP_SECTIONS = re.compile(r"facts used|facts shown|appendix|부록|sources", re.I)
PLACEHOLDER = re.compile(r"^\s*[<\[(]?\s*(…|\.\.\.)?\s*[>\])]?\s*$|^\s*<[^>]*>\s*$")
QUOTE_RX = re.compile(r'"([^"\n]+)"|“([^”\n]+)”|「([^」\n]+)」|『([^』\n]+)』')
SEG_ROW = re.compile(r"^\s*\|\s*\**\s*(S\d+)\b")
MEDIA_ROW = re.compile(r"^\s*\|\s*\**\s*(M\d+)\b")
DETAIL_HEAD = re.compile(r"^(#{2,6})\s*\**\s*(S\d+)\b")
HEADING = re.compile(r"^(#{1,6})\s+(.*)")


def words(text):
    return len(text.split())


def strip_md(text):
    return re.sub(r"\*\*|__|`", "", text).strip()


def is_placeholder(text):
    t = strip_md(text).strip(" \"'“”")
    return not t or bool(PLACEHOLDER.match(t)) or bool(re.fullmatch(r"(<[^>]*>[\s,./·]*)+", t))


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [strip_md(c) for c in line.split("|")]


def is_separator(line):
    return re.match(r"^\s*\|[\s:\-|]+\|?\s*$", line) is not None


def table_header(lines, i):
    for j in range(i - 1, max(-1, i - 8), -1):
        if lines[j].strip().startswith("|") and not is_separator(lines[j]) and not SEG_ROW.match(lines[j]) and not MEDIA_ROW.match(lines[j]):
            return [c.lower() for c in split_row(lines[j])]
    return []


def col(header, name, default):
    for k, h in enumerate(header):
        if h == name or h.startswith(name):
            return k
    return default


def ids_in(cell, prefix):
    return re.findall(rf"\b{prefix}\d+\b", cell or "")


# ---------- house rules ----------

def parse_house(path):
    house = {"path": str(path) if path else None, "forbidden": [], "products": [], "products_source": "none",
             "replacement": None, "words_per_screen": None, "sentence_length": None}
    if not path:
        return house
    text = Path(path).read_text(encoding="utf-8-sig")
    for line in text.splitlines():
        m = re.match(r"^\s*[-*]?\s*forbidden words?\s*:\s*(.*)$", line, re.I)
        if m:
            value = re.sub(r"\([^)]*\)", "", m.group(1))
            house["forbidden"] += [w.strip(" `\"'“”.") for w in re.split(r"[,、/;]", value) if w.strip(" `\"'“”.")]
            continue
        m = re.match(r"^\s*[-*]?\s*product names?\s*:\s*(.*)$", line, re.I)
        if m:
            value = m.group(1)
            r = re.search(r"\bsay\s+[`\"'“]?([^\s.,;`\"'”]+)", value)
            if r:
                house["replacement"] = r.group(1)
            names = [a or b for a, b in re.findall(r"`([^`]+)`|[\"“]([^\"”]+)[\"”]", value)]
            for grp in re.findall(r"(?:\(|banned:|e\.g\.|such as|names:)\s*([^);]*)", value, re.I):
                if "," in grp:
                    names += [n.strip(" .") for n in grp.split(",") if 0 < len(n.split()) <= 3]
            if not names and not re.search(r"\b(never|no|not|avoid)\b", value, re.I) and "," in value:
                names = [n.strip(" .") for n in value.split(",") if 0 < len(n.split()) <= 3]
            if names:
                house["products"] += names
                house["products_source"] = "house"
            elif re.search(r"\b(never|no|not|avoid)\b", value, re.I):
                house["products"] = list(BUILTIN_PRODUCTS)
                house["products_source"] = "built-in (house rule bans names but lists none)"
            continue
        m = re.match(r"^\s*[-*]?\s*words per screen\s*:\s*(\d+)", line, re.I)
        if m:
            house["words_per_screen"] = int(m.group(1))
        m = re.match(r"^\s*[-*]?\s*sentence length\s*:\s*(\d+)", line, re.I)
        if m:
            house["sentence_length"] = int(m.group(1))
    house["forbidden"] = list(dict.fromkeys(house["forbidden"]))
    house["products"] = list(dict.fromkeys(house["products"]))
    return house


# ---------- document walk ----------

def walk(text, file_label):
    """Yield one record per line: number, text, section heading, segment context, code flag."""
    out, section, seg, in_code = [], "", None, False
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            out.append({"n": n, "line": line, "section": section, "seg": seg, "code": True, "file": file_label})
            continue
        h = HEADING.match(line) if not in_code else None
        if h:
            d = DETAIL_HEAD.match(line)
            if d:
                seg = d.group(2).upper()
            else:
                seg = None
                section = h.group(2).strip()
        row = SEG_ROW.match(line)
        out.append({"n": n, "line": line, "section": section, "seg": (row.group(1).upper() if row else seg),
                    "code": in_code, "file": file_label})
    return out


def location(rec, media_id=None):
    where = f"line {rec['n']}" if rec["file"] == "plan" else f"{rec['file']} line {rec['n']}"
    tag = media_id or rec["seg"]
    return f"{tag} | {where}" if tag else where


def learner_units(records):
    """Learner-facing text: instruction lines (whole value) and quoted strings elsewhere."""
    units = []
    for rec in records:
        if rec["code"] or SKIP_SECTIONS.search(rec["section"] or ""):
            continue
        line = rec["line"]
        m = re.match(r"^\s*[-*]?\s*\**instruction\**\s*:\s*(.*)$", line, re.I)
        if m:
            value = m.group(1).strip()
            if not is_placeholder(value):
                units.append((rec, value.strip(" \"“”"), "instruction"))
            continue
        for g in QUOTE_RX.findall(re.sub(r"<[^<>\n]*>", " ", line)):
            q = next(x for x in g if x)
            if not is_placeholder(q):
                units.append((rec, q, "quote"))
    return units


# ---------- plan structure ----------

def parse_plan(text):
    lines = text.splitlines()
    plan = {"slug": None, "band": None, "segments": [], "seg_media": {}, "media": {}, "details": {}}
    for line in lines[:15]:
        m = re.search(r"\bslug\s*:\s*\**\s*([^\s·|*]+)", line, re.I)
        if m and not plan["slug"] and not m.group(1).startswith("<"):
            plan["slug"] = m.group(1)
        m = re.search(r"\bband\s*:\s*\**\s*([A-G])\b", line, re.I)
        if m and not plan["band"]:
            plan["band"] = m.group(1).upper()
    seg_header = media_header = None
    for i, line in enumerate(lines):
        m = SEG_ROW.match(line)
        if m:
            if seg_header is None:
                seg_header = table_header(lines, i)
            cells = split_row(line)
            sid = m.group(1).upper()
            if sid not in plan["segments"]:
                plan["segments"].append(sid)
            k = col(seg_header, "media", None)
            if k is not None and k < len(cells):
                plan["seg_media"].setdefault(sid, []).extend(ids_in(cells[k], "M"))
            plan.setdefault("seg_lines", {})[sid] = i + 1
            continue
        m = MEDIA_ROW.match(line)
        if m:
            if media_header is None:
                media_header = table_header(lines, i)
            cells = split_row(line)
            ti = col(media_header, "type", 1)
            si = col(media_header, "segment", 2)
            plan["media"][m.group(1).upper()] = {
                "type": cells[ti] if ti < len(cells) else "",
                "segment": cells[si] if si < len(cells) else "",
                "line": i + 1,
            }
    # segment detail blocks
    cur, level = None, 0
    for i, line in enumerate(lines):
        d = DETAIL_HEAD.match(line)
        h = HEADING.match(line)
        if d:
            cur, level = d.group(2).upper(), len(d.group(1))
            plan["details"][cur] = {"line": i + 1, "instruction": None, "instruction_line": None}
            continue
        if h and cur and len(h.group(1)) <= level:
            cur = None
            continue
        if cur:
            m = re.match(r"^\s*[-*]?\s*\**instruction\**\s*:\s*(.*)$", line, re.I)
            if m and plan["details"][cur]["instruction"] is None:
                plan["details"][cur]["instruction"] = m.group(1).strip()
                plan["details"][cur]["instruction_line"] = i + 1
    return plan


def parse_brief(path):
    text = path.read_text(encoding="utf-8-sig")
    brief = {"file": path.name, "text": text, "id": None, "lesson": None, "segment": None, "type": None,
             "tool": None, "voice": None, "icon_family": None, "storyboard": False}
    m = re.search(r"^#\s*Media brief\s*:\s*(M\d+)", text, re.I | re.M)
    brief["heading_id"] = m.group(1).upper() if m else None
    fm = re.match(r"(M\d+)", path.stem, re.I)
    brief["file_id"] = fm.group(1).upper() if fm else None
    brief["id"] = brief["heading_id"] or brief["file_id"]
    for line in text.splitlines()[:20]:
        for key, rx in (("lesson", r"\blesson\s*:\s*([^·|\n]+)"), ("segment", r"\bsegment\s*:\s*([^·|\n]+)"),
                        ("type", r"\btype\s*:\s*([^·|\n]+)")):
            mm = re.search(rx, line, re.I)
            if mm and brief[key] is None and not is_placeholder(mm.group(1)):
                brief[key] = mm.group(1).strip()
        for key, rx in (("tool", r"^\s*[-*]?\s*tool\s*:\s*(.*)$"), ("voice", r"^\s*[-*]?\s*voice\s*:\s*(.*)$"),
                        ("icon_family", r"^\s*[-*]?\s*icon family\s*:\s*(.*)$")):
            mm = re.match(rx, line, re.I)
            if mm and brief[key] is None:
                brief[key] = mm.group(1).strip()
    brief["storyboard"] = bool(re.search(r"^\|\s*t\s*\|\s*on screen", text, re.I | re.M))
    return brief


def norm_type(t):
    t = (t or "").lower().strip()
    t = re.sub(r"\d.*$", "", t).strip()  # "video 40 s" -> "video"
    return t


# ---------- checks ----------

def run(plan_path, house_path=None, band=None):
    plan_path = Path(plan_path)
    text = plan_path.read_text(encoding="utf-8-sig")
    house = parse_house(house_path)
    plan = parse_plan(text)
    findings = []

    def add(sev, loc, rule, issue, fix):
        findings.append({"severity": sev, "location": loc, "rule": rule, "issue": issue, "fix": fix})

    records = {"plan": walk(text, "plan")}
    media_dir = plan_path.parent / "media"
    briefs = []
    if media_dir.is_dir():
        for p in sorted(media_dir.glob("*.md")):
            b = parse_brief(p)
            briefs.append(b)
            records[f"media/{p.name}"] = walk(b["text"], f"media/{p.name}")
    brief_by_label = {f"media/{b['file']}": b for b in briefs}

    # 1. words: forbidden, product names, translationese
    for label, recs in records.items():
        mid = brief_by_label[label]["id"] if label in brief_by_label else None
        units = learner_units(recs)
        learner_lines = {u[0]["n"] for u in units}
        for rec in recs:
            if rec["code"] or SKIP_SECTIONS.search(rec["section"] or ""):
                continue
            for w in house["forbidden"]:
                if w and w in rec["line"]:
                    if rec["n"] in learner_lines:
                        add(1, location(rec, mid), "forbidden-word",
                            f'"{w}" is forbidden by the house rules and appears in a learner-facing line.',
                            TRANSLATIONESE.get(w, PROMISE_FIX.get(w, "Rewrite the line without it.")))
                    else:
                        add(2, location(rec, mid), "forbidden-word",
                            f'"{w}" (forbidden by the house rules) appears outside a quoted or instruction line.',
                            "Check whether learners see this line; if they do, rewrite it.")
        for rec, unit, kind in units:
            for name in house["products"]:
                rx = re.escape(name)
                hit = re.search(rf"(?<![A-Za-z0-9]){rx}(?![A-Za-z0-9])", unit, re.I) if re.search(r"[A-Za-z]", name) else (name in unit)
                if hit:
                    repl = f' Say "{house["replacement"]}".' if house["replacement"] else ""
                    add(1, location(rec, mid), "product-name",
                        f'Product name "{name}" in a learner-facing line.',
                        f"Replace it with the generic term.{repl} Named tools go in the dated tool appendix only.")
            for word, fix in TRANSLATIONESE.items():
                if word in unit and word not in house["forbidden"]:  # a forbidden word is already a sev-1 above
                    add(2, location(rec, mid), "translationese", f'"{word}" in a learner-facing line reads as translated Korean.', fix)

    # 2. media rows vs briefs, names that differ
    seg_set = set(plan["segments"])
    by_id = {}
    for b in briefs:
        if b["id"]:
            by_id.setdefault(b["id"], []).append(b)
        if b["heading_id"] and b["file_id"] and b["heading_id"] != b["file_id"]:
            add(1, f"{b['heading_id']} | media/{b['file']}", "name-mismatch",
                f"File name says {b['file_id']} but the heading says {b['heading_id']}.",
                "Rename the file or fix the heading so both carry the same id.")
    for mid_, row in plan["media"].items():
        loc = f"{mid_} | line {row['line']}"
        if mid_ not in by_id:
            add(1, loc, "media-brief-missing", f"Media list row {mid_} has no brief in media/.",
                f"Write media/{mid_}.md from templates/media-brief.md.")
        row_segs = set(ids_in(row["segment"], "S"))
        for s in sorted(row_segs - seg_set):
            add(1, loc, "name-mismatch", f"{mid_} points at segment {s}, which is not in the Segments table.",
                "Point the row at an existing segment or add the segment.")
        for b in by_id.get(mid_, []):
            bloc = f"{mid_} | media/{b['file']}"
            if b["lesson"] and plan["slug"] and b["lesson"].strip() != plan["slug"]:
                add(1, bloc, "name-mismatch", f"Brief says lesson \"{b['lesson']}\", the plan's slug is \"{plan['slug']}\".",
                    "Use the plan's slug in the brief header.")
            b_segs = set(ids_in(b["segment"] or "", "S"))
            if b_segs and row_segs and b_segs != row_segs:
                add(1, bloc, "name-mismatch",
                    f"Brief says segment {', '.join(sorted(b_segs))}, the Media list says {', '.join(sorted(row_segs))}.",
                    "Make the brief header and the Media list row name the same segment.")
            bt, rt = norm_type(b["type"]), norm_type(row["type"])
            if bt and rt and not (bt.startswith(rt) or rt.startswith(bt)):
                add(2, bloc, "name-mismatch", f"Brief type \"{b['type']}\" differs from the Media list type \"{row['type']}\".",
                    "Use one type name in both places.")
    for b in briefs:
        if b["id"] and b["id"] not in plan["media"]:
            add(1, f"{b['id']} | media/{b['file']}", "media-row-missing", f"Brief {b['file']} has no row in the Media list.",
                "Add a Media list row for it or delete the brief.")
        elif not b["id"]:
            add(1, f"media/{b['file']}", "media-row-missing", f"Brief {b['file']} has no M-id in its heading or file name.",
                "Name the file media/M<n>.md and put the id in the heading.")
    for sid, mids in plan["seg_media"].items():
        for m_ in mids:
            if m_ not in plan["media"]:
                add(1, f"{sid} | line {plan['seg_lines'][sid]}", "name-mismatch",
                    f"{sid} uses {m_}, which has no row in the Media list.", f"Add {m_} to the Media list or fix the id.")
    families = {}
    for b in briefs:
        fam = (b["icon_family"] or "").strip()
        if fam and not is_placeholder(fam) and fam.lower() not in ("none", "n/a", "-", "–"):
            key = re.split(r"[,\s]", fam.lower())[0]
            families.setdefault(key, []).append(b["id"] or b["file"])
        if b["tool"] is None or is_placeholder(b["tool"] or ""):
            add(2, f"{b['id'] or b['file']} | media/{b['file']}", "brief-tool", "Brief has no tool: line.",
                "Name the script that produces it (see templates/media-brief.md).")
        talks = b["storyboard"] or norm_type(b["type"]) in ("video", "animation")
        if talks and (b["voice"] is None or is_placeholder(b["voice"] or "")):
            add(2, f"{b['id'] or b['file']} | media/{b['file']}", "brief-voice", "Brief with narration or a storyboard has no voice: line.",
                "Name the voice and register (draft and final if they differ).")
    if len(families) > 1:
        detail = "; ".join(f"{k}: {', '.join(v)}" for k, v in families.items())
        add(2, "media/", "icon-family", f"More than one icon family across briefs ({detail}).",
            "Pick one family for the lesson and use it on every brief.")

    # 3. segments: detail block and written instruction
    for sid in plan["segments"]:
        d = plan["details"].get(sid)
        if d is None:
            add(1, f"{sid} | line {plan['seg_lines'][sid]}", "segment-detail-missing",
                f"{sid} has no '#### {sid}' detail block.", "Add the detail block with instruction, materials, fast / slow / wrong and transition.")
        elif d["instruction"] is None:
            add(1, f"{sid} | line {d['line']}", "instruction-missing", f"{sid}'s detail block has no instruction: line.",
                "Write the exact instruction the learner hears or reads.")
        elif is_placeholder(d["instruction"]):
            add(1, f"{sid} | line {d['instruction_line']}", "instruction-missing", f"{sid}'s instruction is still a placeholder.",
                "Write the exact instruction the learner hears or reads.")
    for sid, d in plan["details"].items():
        if sid not in seg_set and plan["segments"]:
            add(2, f"{sid} | line {d['line']}", "name-mismatch", f"Detail block {sid} has no row in the Segments table.",
                "Add the row or rename the block.")

    # 4. readability per band on learner-facing lines
    used_band = band or plan["band"] or DEFAULT_BAND
    band_note = "header" if plan["band"] and not band else ("--band" if band else f"default {DEFAULT_BAND} (no band in header)")
    per_screen, per_sentence = READ_CAPS[used_band]
    per_screen = house["words_per_screen"] or per_screen
    per_sentence = house["sentence_length"] or per_sentence
    all_units, longest_screen, longest_sentence = [], 0, 0
    for label, recs in records.items():
        mid = brief_by_label[label]["id"] if label in brief_by_label else None
        for rec, unit, kind in learner_units(recs):
            all_units.append(unit)
            n = words(unit)
            longest_screen = max(longest_screen, n)
            if n > per_screen:
                add(2, location(rec, mid), "words-per-screen",
                    f"{n} words on one screen; band {used_band} default is {per_screen}.",
                    "Cut to one idea; move the rest to the voice, a second screen or the teacher.")
            sentences = [s for s in re.split(r"(?<=[.?!。])\s+", unit) if s.strip()]
            if used_band == "A" and len(sentences) > 1:
                add(2, location(rec, mid), "words-per-screen", f"{len(sentences)} sentences on one screen; band A allows one short sentence.",
                    "Keep one sentence; read the rest aloud.")
            for s in sentences:
                sn = words(s)
                longest_sentence = max(longest_sentence, sn)
                if sn > per_sentence:
                    add(2, location(rec, mid), "sentence-length",
                        f"Sentence of {sn} words (Korean: 어절); band {used_band} default is {per_sentence}.",
                        "Split into two sentences, one idea each.")

    # 5. Oak-style field limits
    lines = text.splitlines()
    sec_start = next((i for i, l in enumerate(lines) if re.match(r"^##\s+outcome", l, re.I)), None)
    if sec_start is not None:
        body = []
        for i in range(sec_start + 1, len(lines)):
            if HEADING.match(lines[i]) or re.match(r"^\s*prior knowledge", lines[i], re.I):
                break
            body.append(lines[i])
        outcome = strip_md(" ".join(body)).split("Evidence:")[0].strip()
        ow = words(outcome)
        if ow > OUTCOME_MAX_WORDS:
            add(2, f"line {sec_start + 1}", "field-limit", f"Outcome is {ow} words; the limit is {OUTCOME_MAX_WORDS}.",
                "Cut to one observable verb phrase and the artifact.")
    else:
        ow = None
    prior_items = None
    for i, l in enumerate(lines):
        m = re.match(r"^\s*[-*]?\s*\**prior knowledge(?: assumed)?\**\s*:\s*(.*)$", l, re.I)
        if not m:
            continue
        value = re.split(r"\.\s+Prerequisite", m.group(1), flags=re.I)[0].strip().rstrip(".")
        if value and not is_placeholder(value):
            prior_items = 0 if value.lower() in ("none", "없음") else len([x for x in re.split(r"[;,]", value) if x.strip()])
        else:
            bullets = []
            for j in range(i + 1, len(lines)):
                if re.match(r"^\s+[-*]\s+\S", lines[j]) or (not value and re.match(r"^\s*[-*]\s+\S", lines[j])):
                    bullets.append(lines[j])
                else:
                    break
            prior_items = len(bullets) if bullets else None
        if prior_items is not None and prior_items > PRIOR_MAX_ITEMS:
            add(2, f"line {i + 1}", "field-limit", f"{prior_items} prior-knowledge items; the limit is {PRIOR_MAX_ITEMS}.",
                "Keep the ones the lesson actually builds on.")
        break
    mis_count, mis_line = None, None
    for i, l in enumerate(lines):
        h = HEADING.match(l)
        if h and "misconception" in h.group(2).lower():
            level = len(h.group(1))
            items = []
            for j in range(i + 1, len(lines)):
                hh = HEADING.match(lines[j])
                if hh and len(hh.group(1)) <= level:
                    break
                if re.match(r"^\s*([-*]|\d+\.|\|)\s*\S", lines[j]) and not is_separator(lines[j]):
                    items.append(lines[j])
            rows = [x for x in items if x.strip().startswith("|")]
            if rows:  # a table: drop the header row
                items = [x for x in items if not x.strip().startswith("|")] + rows[1:]
            def first_cell(x):
                if x.strip().startswith("|"):
                    return (split_row(x) or [""])[0]
                return re.sub(r"^\s*([-*]|\d+\.)\s*", "", x)
            items = [x for x in items if not is_placeholder(first_cell(x))]
            mis_count, mis_line = len(items), i + 1
            break
    if mis_count is None:
        for i, l in enumerate(lines):
            m = re.match(r"^\s*[-*]?\s*[^:]*misconception[^:]*:\s*(.*)$", l, re.I)
            if not m:
                continue
            value = m.group(1).strip()
            if value and not is_placeholder(value):
                mis_count = len([x for x in value.split(";") if x.strip() and not is_placeholder(x)])
            else:
                sub = []
                for j in range(i + 1, len(lines)):
                    if re.match(r"^\s+[-*]\s+\S", lines[j]):
                        sub.append(lines[j])
                    else:
                        break
                mis_count = len([x for x in sub if not is_placeholder(re.sub(r"^\s*[-*]\s*", "", x))])
            mis_line = i + 1
            break
    lo, hi = MISCONCEPTIONS_RANGE
    if mis_count is None:
        add(2, "plan", "field-limit", "No misconceptions named anywhere in the plan.",
            f"Name {lo} to {hi} misconceptions, each with its fixing line and the segment where it surfaces.")
    elif not lo <= mis_count <= hi:
        issue = "No misconception is filled in." if mis_count == 0 else f"{mis_count} misconceptions; the range is {lo} to {hi}."
        add(2, f"line {mis_line}", "field-limit", issue,
            f"Name {lo} to {hi} misconceptions, each with its fixing line and the segment where it surfaces.")

    # 6. stats
    needs = []
    for label, recs in records.items():
        mid = brief_by_label[label]["id"] if label in brief_by_label else None
        for rec in recs:
            for _ in re.finditer(r"\[needs fact:", rec["line"], re.I):
                needs.append(location(rec, mid))
    findings.sort(key=lambda f: (f["severity"], f["location"]))
    stats = {
        "plan": str(plan_path),
        "house": house["path"],
        "forbidden_words": house["forbidden"],
        "product_names_source": house["products_source"],
        "band": used_band,
        "band_source": band_note,
        "caps": {"words_per_screen": per_screen, "words_per_sentence": per_sentence},
        "segments": len(plan["segments"]),
        "detail_blocks": len(plan["details"]),
        "media_rows": len(plan["media"]),
        "media_briefs": len(briefs),
        "learner_lines": len(all_units),
        "longest_screen_words": longest_screen,
        "longest_sentence_words": longest_sentence,
        "outcome_words": ow,
        "prior_knowledge_items": prior_items,
        "misconceptions": mis_count,
        "needs_fact": len(needs),
        "needs_fact_locations": needs,
        "sev1": sum(1 for f in findings if f["severity"] == 1),
        "sev2": sum(1 for f in findings if f["severity"] == 2),
    }
    return {"findings": findings, "stats": stats}


def main():
    ap = argparse.ArgumentParser(description="Lint a lesson plan and its media briefs before the critics run.")
    ap.add_argument("plan")
    ap.add_argument("--house", help="house rules file (default: lesson.md in the current folder, if any)")
    ap.add_argument("--band", choices=list("ABCDEFG"), type=str.upper)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    house = a.house
    if house is None and Path("lesson.md").is_file():
        house = "lesson.md"
    if house and not Path(house).is_file():
        print(f"house rules file not found: {house}", file=sys.stderr)
        sys.exit(2)
    if not Path(a.plan).is_file():
        print(f"plan not found: {a.plan}", file=sys.stderr)
        sys.exit(2)
    result = run(a.plan, house, a.band)
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        s = result["stats"]
        print(f"lint: {s['plan']}")
        print(f"house: {s['house'] or 'none'} · forbidden: {', '.join(s['forbidden_words']) or 'none'} · product names: {s['product_names_source']}")
        print(f"band: {s['band']} ({s['band_source']}) · caps: {s['caps']['words_per_screen']} words per screen, {s['caps']['words_per_sentence']} per sentence")
        for f in result["findings"]:
            tag = "FAIL" if f["severity"] == 1 else "warn"
            print(f"{tag} sev-{f['severity']} [{f['rule']}] {f['location']}: {f['issue']} Fix: {f['fix']}")
        print(f"stats: {s['segments']} segments, {s['detail_blocks']} detail blocks, {s['media_rows']} media rows, "
              f"{s['media_briefs']} briefs, {s['learner_lines']} learner-facing lines (longest {s['longest_screen_words']} words, "
              f"longest sentence {s['longest_sentence_words']}), outcome {s['outcome_words']} words, "
              f"prior knowledge {s['prior_knowledge_items']}, misconceptions {s['misconceptions']}, needs fact {s['needs_fact']}")
        print(f"result: {s['sev1']} sev-1, {s['sev2']} sev-2 -> {'FAIL' if s['sev1'] else 'OK'}")
    sys.exit(1 if result["stats"]["sev1"] else 0)


if __name__ == "__main__":
    main()
