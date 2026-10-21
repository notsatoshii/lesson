#!/usr/bin/env python3
"""Callouts on a screenshot (Pillow only).

Usage: python highlight.py <screenshot.png> --spec <brief.md> [--out <path>] [--scale 1.0] [--size 1.0] [--color #FF4D2E]
       python highlight.py <screenshot.png> --box x,y,w,h[,"label"] --arrow x1,y1,x2,y2 --badge x,y,n
                                            --blur x,y,w,h --crop x,y,w,h [--no-badge]
                                            --line x1,y1,x2,y2[,x3,y3...] [--line-width px] --pill x,y,"label"
       python highlight.py --demo [--out <path>]

Draws rounded boxes, arrows with a filled head, numbered badges, label pills and blurred regions on a
screenshot, in one accent colour. --spec reads the numbered callouts list from a media brief's
screenshot+highlights section; the inline flags do the same by hand. All coordinates are measured on
the original screenshot; a crop is applied first and later shapes are shifted to match. --no-badge
keeps the label pills but drops the number badges on boxes and arrows. --line draws a plain polyline with no
head and no badge (a tether from a box to a label); --line-width sets its width in output px (default: the
box stroke). --pill draws a label pill alone, its left end at x and its top at y. Output goes
to <name>.hl.png beside the input unless --out is given.
"""
import argparse
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ACCENT = "#FF4D2E"
STROKE = 3
RADIUS = 8
BADGE = 28
BLUR_RADIUS = 12
FONT_SIZE = 16
SIZE = 1.0  # --size multiplier for strokes, badges, labels (2 for a dpr-2 capture)
FONT_PATHS = [
    "C:/Windows/Fonts/malgun.ttf",
    "C:/Windows/Fonts/NotoSansKR-Regular.ttf",
    "C:/Windows/Fonts/NotoSansKR-Regular.otf",
    os.path.expanduser("~/.fonts/NotoSansKR-Regular.ttf"),
    os.path.expanduser("~/.fonts/NotoSansKR-Regular.otf"),
    "/usr/share/fonts/truetype/noto/NotoSansKR-Regular.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/Library/Fonts/NotoSansKR-Regular.otf",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
]
NUM = r"(-?\d+(?:\.\d+)?)"
SEP = r"\s*,\s*"
RECT_RE = re.compile(r"\b(box|rect|rectangle)\s+" + SEP.join([NUM] * 4), re.I)
ARROW_RE = re.compile(r"\barrow\s+" + NUM + SEP + NUM + r"\s*(?:->|→|=>|to|~>)\s*" + NUM + SEP + NUM, re.I)
BLUR_RE = re.compile(r"\bblur\s+" + SEP.join([NUM] * 4), re.I)
CROP_RE = re.compile(r"\bcrop\s+" + SEP.join([NUM] * 4), re.I)
BADGE_RE = re.compile(r"\bbadge\s+" + NUM + SEP + NUM + SEP + r"(\d+)", re.I)
QUOTE_RE = re.compile(r"[\"“”「『]([^\"“”」』]+)[\"“”」』]")


def load_font(size, explicit=None):
    for path in ([explicit] if explicit else []) + FONT_PATHS:
        if path and os.path.exists(path):
            try:
                return ImageFont.truetype(path, size), path
            except OSError:
                continue
    try:
        return ImageFont.load_default(size=size), "pillow-default"
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default(), "pillow-default"


def floats(groups):
    return [float(g) for g in groups]


def label_after(line, end):
    """Label text after a shape: text after the last · or | separator, else the first quoted run."""
    rest = line[end:]
    parts = re.split(r"\s[·|]\s|[·|]", rest)
    tail = parts[-1].strip() if len(parts) > 1 else ""
    tail = re.sub(r"^(label|text)\s*[:：]?\s*", "", tail, flags=re.I)
    m = QUOTE_RE.search(tail) or (QUOTE_RE.search(rest) if not tail else None)
    if m:
        return m.group(1).strip()
    return tail.strip() or None


def parse_spec(text):
    """Return (items, warnings). Items are dicts with kind box|arrow|blur|crop|badge."""
    lines = text.splitlines()
    start, end = 0, len(lines)
    for i, line in enumerate(lines):
        if re.match(r"^\s*#{1,6}\s*.*screenshot\s*\+\s*highlights", line, re.I):
            start = i + 1
            level = len(re.match(r"^\s*(#+)", line).group(1))
            for j in range(start, len(lines)):
                m = re.match(r"^\s*(#+)\s", lines[j])
                if m and len(m.group(1)) <= level:
                    end = j
                    break
            break
    warnings = []
    if start == 0:
        warnings.append("no 'screenshot+highlights' heading found; reading the whole file")
    items, n = [], 0
    for raw in lines[start:end]:
        line = re.sub(r"\*\*|__|`", "", raw).strip()
        m_num = re.match(r"^(\d+)[.)]\s+", line)
        body = line[m_num.end():] if m_num else re.sub(r"^[-*+]\s+", "", line)
        if not body:
            continue
        m = RECT_RE.search(body)
        if m:
            n = int(m_num.group(1)) if m_num else n + 1
            x, y, w, h = floats(m.groups()[1:])
            items.append({"kind": "box", "x": x, "y": y, "w": w, "h": h, "n": n, "label": label_after(body, m.end())})
            continue
        m = ARROW_RE.search(body)
        if m:
            n = int(m_num.group(1)) if m_num else n + 1
            x1, y1, x2, y2 = floats(m.groups())
            items.append({"kind": "arrow", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "n": n, "label": label_after(body, m.end())})
            continue
        m = BLUR_RE.search(body)
        if m:
            x, y, w, h = floats(m.groups())
            items.append({"kind": "blur", "x": x, "y": y, "w": w, "h": h})
            continue
        m = CROP_RE.search(body)
        if m:
            x, y, w, h = floats(m.groups())
            items.append({"kind": "crop", "x": x, "y": y, "w": w, "h": h})
            continue
        m = BADGE_RE.search(body)
        if m:
            x, y = floats(m.groups()[:2])
            items.append({"kind": "badge", "x": x, "y": y, "n": int(m.group(3))})
            continue
        if m_num:
            warnings.append(f"callout {m_num.group(1)} has no coordinates, skipped: {body[:60]}")
    return items, warnings


def parse_inline(a, start=0):
    items = []
    if a.crop:
        x, y, w, h = floats(a.crop.split(",")[:4])
        items.append({"kind": "crop", "x": x, "y": y, "w": w, "h": h})
    for spec in a.blur or []:
        x, y, w, h = floats(spec.split(",")[:4])
        items.append({"kind": "blur", "x": x, "y": y, "w": w, "h": h})
    n = start  # numbering continues after the spec's callouts
    for spec in a.box or []:
        parts = [p.strip() for p in spec.split(",", 4)]
        x, y, w, h = floats(parts[:4])
        label = parts[4].strip("\"'“”") if len(parts) > 4 and parts[4].strip() else None
        n += 1
        items.append({"kind": "box", "x": x, "y": y, "w": w, "h": h, "n": n, "label": label})
    for spec in a.arrow or []:
        parts = [p.strip() for p in spec.split(",", 4)]
        x1, y1, x2, y2 = floats(parts[:4])
        label = parts[4].strip("\"'“”") if len(parts) > 4 and parts[4].strip() else None
        n += 1
        items.append({"kind": "arrow", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "n": n, "label": label})
    for spec in a.badge or []:
        x, y, k = spec.split(",")[:3]
        items.append({"kind": "badge", "x": float(x), "y": float(y), "n": int(k)})
    for spec in getattr(a, "line", None) or []:
        pts = floats(spec.split(","))
        if len(pts) < 4 or len(pts) % 2:
            raise SystemExit(f"--line needs x1,y1,x2,y2[,x3,y3...]: {spec}")
        items.append({"kind": "line", "points": list(zip(pts[0::2], pts[1::2])), "width": getattr(a, "line_width", None)})
    for spec in getattr(a, "pill", None) or []:
        parts = [p.strip() for p in spec.split(",", 2)]
        if len(parts) < 3 or not parts[2].strip("\"'“”"):
            raise SystemExit(f'--pill needs x,y,"label": {spec}')
        items.append({"kind": "pill", "x": float(parts[0]), "y": float(parts[1]), "label": parts[2].strip("\"'“”")})
    return items


def arrow_head(d, x1, y1, x2, y2, color, length=14, half=7):
    length, half = length * SIZE, half * SIZE
    dx, dy = x2 - x1, y2 - y1
    dist = (dx * dx + dy * dy) ** 0.5 or 1.0
    ux, uy = dx / dist, dy / dist
    bx, by = x2 - ux * length, y2 - uy * length  # base of the head
    px, py = -uy, ux
    d.polygon([(x2, y2), (bx + px * half, by + py * half), (bx - px * half, by - py * half)], fill=color)
    return bx, by


def draw_badge(d, cx, cy, n, color, font):
    r = BADGE * SIZE / 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color, outline="white", width=max(2, round(2 * SIZE)))
    text = str(n)
    l, t, rgt, b = d.textbbox((0, 0), text, font=font)
    d.text((cx - (rgt - l) / 2 - l, cy - (b - t) / 2 - t), text, font=font, fill="white")


def pill_size(d, text, font, pad=(10, 5)):
    """Width and height of a label pill for this text at the current --size."""
    l, t, rgt, b = d.textbbox((0, 0), text, font=font)
    return (rgt - l) + pad[0] * SIZE * 2, (b - t) + pad[1] * SIZE * 2


def draw_pill(d, x, y, text, color, font, pad=(10, 5)):
    """A label pill with its left end at x and its top at y (no clamping: --pill places it exactly)."""
    pad = (pad[0] * SIZE, pad[1] * SIZE)
    l, t, rgt, b = d.textbbox((0, 0), text, font=font)
    pw, ph = (rgt - l) + pad[0] * 2, (b - t) + pad[1] * 2
    d.rounded_rectangle([x, y, x + pw, y + ph], radius=ph / 2, fill=color)
    d.text((x + pad[0] - l, y + pad[1] - t), text, font=font, fill="white")
    return pw, ph


def draw_label(d, img_w, img_h, x, y, w, h, text, color, font, pad=(10, 5), arrow=False, badge=True, head=None):
    pad = (pad[0] * SIZE, pad[1] * SIZE)
    l, t, rgt, b = d.textbbox((0, 0), text, font=font)
    tw, th = rgt - l, b - t
    pw, ph = tw + pad[0] * 2, th + pad[1] * 2
    gap = 6 * SIZE
    if badge:
        px = x + BADGE * SIZE / 2 + gap  # right of the badge at the top-left corner
    elif arrow:
        px = x - pw / 2  # no badge: the pill sits on the arrow's tail, centred on it
    else:
        px = x  # no badge: the pill starts at the box's left edge
    if arrow and not badge and head:  # the tail touches the pill on the side away from the head
        hx, hy = head
        if abs(hy - y) >= abs(hx - x):
            py = y if hy < y else y - ph
        else:
            px, py = (x - pw if hx > x else x), y - ph / 2
    elif arrow:  # beside the badge at the arrow's tail, vertically centred, so the two never overlap
        py = y - ph / 2
    else:
        py = y - ph - gap if y - ph - gap >= 0 else y + h + gap  # above the box, else below
    px = min(max(px, 0), img_w - pw)
    py = max(py, 0)
    py = min(py, img_h - ph)
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=ph / 2, fill=color)
    d.text((px + pad[0] - l, py + pad[1] - t), text, font=font, fill="white")


def render(img, items, color=ACCENT, scale=1.0, font_path=None, size=1.0, badges_on=True):
    """badges_on=False (--no-badge) drops the number badge on boxes and arrows; explicit badge items stay."""
    global SIZE
    SIZE = size
    stroke = max(1, round(STROKE * SIZE))
    img = img.convert("RGB")
    sc = lambda v: v * scale  # noqa: E731
    ox = oy = 0.0
    crop = next((i for i in items if i["kind"] == "crop"), None)
    if crop:
        x, y, w, h = sc(crop["x"]), sc(crop["y"]), sc(crop["w"]), sc(crop["h"])
        img = img.crop((int(x), int(y), int(x + w), int(y + h)))
        ox, oy = x, y
    W, H = img.size
    for it in items:  # blur first so strokes stay crisp
        if it["kind"] != "blur":
            continue
        x, y, w, h = sc(it["x"]) - ox, sc(it["y"]) - oy, sc(it["w"]), sc(it["h"])
        box = (max(0, int(x)), max(0, int(y)), min(W, int(x + w)), min(H, int(y + h)))
        if box[2] > box[0] and box[3] > box[1]:
            img.paste(img.crop(box).filter(ImageFilter.BoxBlur(BLUR_RADIUS)), box)
    d = ImageDraw.Draw(img)
    font, used = load_font(round(FONT_SIZE * SIZE), font_path)
    badge_font, _ = load_font(round(15 * SIZE), font_path)
    badges, labels = [], []
    for it in items:
        if it["kind"] == "box":
            x, y, w, h = sc(it["x"]) - ox, sc(it["y"]) - oy, sc(it["w"]), sc(it["h"])
            d.rounded_rectangle([x, y, x + w, y + h], radius=RADIUS * SIZE, outline=color, width=stroke)
            if it.get("n") and badges_on:
                badges.append((x, y, it["n"]))
            if it.get("label"):
                labels.append((x, y, w, h, it["label"], False, None))
        elif it["kind"] == "arrow":
            x1, y1, x2, y2 = sc(it["x1"]) - ox, sc(it["y1"]) - oy, sc(it["x2"]) - ox, sc(it["y2"]) - oy
            bx, by = arrow_head(d, x1, y1, x2, y2, color)
            d.line([(x1, y1), (bx, by)], fill=color, width=stroke)
            if it.get("n") and badges_on:
                badges.append((x1, y1, it["n"]))
            if it.get("label"):
                labels.append((x1, y1, 0, 0, it["label"], True, (x2, y2)))
        elif it["kind"] == "badge":
            badges.append((sc(it["x"]) - ox, sc(it["y"]) - oy, it["n"]))
        elif it["kind"] == "line":  # a plain tether: no head, no badge, square joints
            pts = [(sc(x) - ox, sc(y) - oy) for x, y in it["points"]]
            w = max(1, round(it["width"])) if it.get("width") else stroke
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                d.line([(x1, y1), (x2, y2)], fill=color, width=w)
            for x, y in pts[1:-1]:  # fill the corner so an L-turn has no notch
                d.rectangle([x - (w - 1) / 2, y - (w - 1) / 2, x + w / 2, y + w / 2], fill=color)
    for x, y, w, h, text, is_arrow, head in labels:
        draw_label(d, W, H, x, y, w, h, text, color, font, arrow=is_arrow, badge=badges_on, head=head)
    for it in items:
        if it["kind"] == "pill":
            draw_pill(d, sc(it["x"]) - ox, sc(it["y"]) - oy, it["label"], color, font)
    for x, y, n in badges:
        draw_badge(d, x, y, n, color, badge_font)
    return img, used


def demo_image():
    img = Image.new("RGB", (800, 500), "#E4E4E4")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 800, 56], fill="#2B2F36")  # top bar
    d.rectangle([24, 90, 376, 134], fill="white", outline="#B5B5B5")  # input
    d.rectangle([400, 90, 560, 134], fill="#3B6EF5")  # primary button
    d.rectangle([24, 170, 776, 300], fill="white", outline="#B5B5B5")  # card
    d.rectangle([24, 330, 300, 470], fill="white", outline="#B5B5B5")  # side card
    for i, yy in enumerate(range(190, 290, 24)):
        d.rectangle([44, yy, 44 + 480 - i * 60, yy + 10], fill="#C8C8C8")
    d.text((40, 350), "user@example.com", fill="#333333", font=load_font(18)[0])
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("screenshot", nargs="?")
    ap.add_argument("--spec", help="media brief (.md) with a screenshot+highlights section")
    ap.add_argument("--out")
    ap.add_argument("--scale", type=float, default=1.0, help="multiply all coordinates (e.g. 2 for a 2x capture)")
    ap.add_argument("--size", type=float, default=1.0, help="multiply stroke, badge and label sizes (2 for a dpr-2 capture)")
    ap.add_argument("--color", default=ACCENT)
    ap.add_argument("--font", help="TTF/OTF to use for labels (default: Malgun, then Noto Sans KR, then Pillow's)")
    ap.add_argument("--box", action="append", metavar='x,y,w,h[,"label"]')
    ap.add_argument("--arrow", action="append", metavar='x1,y1,x2,y2[,"label"]')
    ap.add_argument("--badge", action="append", metavar="x,y,n")
    ap.add_argument("--blur", action="append", metavar="x,y,w,h")
    ap.add_argument("--crop", metavar="x,y,w,h")
    ap.add_argument("--line", action="append", metavar="x1,y1,x2,y2[,x3,y3...]",
                    help="a plain polyline with no head (a tether from a box to a pill)")
    ap.add_argument("--line-width", type=float, metavar="px", help="--line width in output px (default: the box stroke)")
    ap.add_argument("--pill", action="append", metavar='x,y,"label"',
                    help="a label pill alone, its left end at x and its top at y")
    ap.add_argument("--demo", action="store_true", help="render a grey 800x500 test image with sample callouts")
    ap.add_argument("--no-badge", action="store_true",
                    help="draw boxes and arrows with their label pill but no number badge (explicit --badge stays)")
    a = ap.parse_args()

    warnings = []
    if a.demo:
        img = demo_image()
        items = [
            {"kind": "blur", "x": 30, "y": 340, "w": 220, "h": 40},
            {"kind": "box", "x": 24, "y": 90, "w": 352, "h": 44, "n": 1, "label": "이메일을 입력하세요"},
            {"kind": "box", "x": 400, "y": 90, "w": 160, "h": 44, "n": 2, "label": "로그인 버튼을 누르세요"},
            {"kind": "arrow", "x1": 480, "y1": 400, "x2": 420, "y2": 250, "n": 3, "label": "여기"},
            {"kind": "box", "x": 24, "y": 170, "w": 752, "h": 130, "n": 4, "label": None},
        ]
        out = a.out or os.path.join(os.getcwd(), "highlight-demo.hl.png")
        source = "demo"
    else:
        if not a.screenshot:
            ap.error("a screenshot path is required unless --demo is given")
        img = Image.open(a.screenshot)
        items = []
        if a.spec:
            with open(a.spec, encoding="utf-8") as f:
                items, warnings = parse_spec(f.read())
        items += parse_inline(a, max([it.get("n", 0) for it in items] + [0]))
        if not items:
            warnings.append("no callouts found; writing the screenshot unchanged")
        root, _ = os.path.splitext(a.screenshot)
        out = a.out or root + ".hl.png"
        source = a.screenshot

    result, font_used = render(img, items, a.color, a.scale, a.font, a.size, badges_on=not a.no_badge)
    result.save(out)
    counts = {}
    for it in items:
        counts[it["kind"]] = counts.get(it["kind"], 0) + 1
    report = {"source": source, "out": out, "size": list(result.size), "drawn": counts, "font": font_used, "warnings": warnings}
    sys.stdout.buffer.write((json.dumps(report, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
