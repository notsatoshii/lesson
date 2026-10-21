// Data-driven printable worksheet (A4 by default). Compiled by tools/worksheet.py.
// By hand: typst compile --root <dir> --input data=/<path-from-root>/x.json --input base=/<dir-of-json> worksheet.typ out.pdf
//
// Data (JSON), every key optional except blocks:
//   title, footer (small grey line at the page foot, e.g. the material id), pages (expected page count),
//   paper ("a4"), flipped (false), margin (mm, number or {x, top, bottom}), size (body pt, 11),
//   title_size (pt, 22), gap (mm between blocks, 3.5), font (list of families),
//   colors: {ink, accent, paper, grey_fill, muted, rule}, icons: {name: "path.svg"} (relative to the JSON),
//   labels: {P: "처리", T: "판단"},
//   blocks: [ ... ] (see tools/README.md, "worksheet.py"); {"type": "pagebreak"} starts the next page.
//   {"type": "rule", "thickness": 0.5, "color": "grey_fill", "width": "100%"} draws a hairline (a separator).
//   {"type": "image", "src": "pic.png", "width": 120, "height": 40, "align": "center", "alt": "...", "caption": runs}
//   places a picture (PNG, JPG, SVG; path relative to the JSON), aspect ratio kept.
//
// Inline text ("runs") is a string, or a list of strings and objects:
//   {"text": "...", "bold": true, "color": "accent"|"muted"|"#hex", "size": 12, "strike": true}
//   {"blank": 30}  write-on line, mm wide          {"box": true}  tick box
//   {"field": 14}  small write-in box, mm wide     {"mark": "P"|"T", "label": "..."}  the 처리 / 판단 chip
//   {"icon": "brain", "color": "ink", "size": 16}  (size in pt, default the text size)   {"br": true}  line break
//   {"tag": "3"}  a short value in an outlined box (a level to circle, a score)
//     optional: "fill" (a filled tag, white text), "text" (text colour), "radius" and "stroke" (pt): a chip
//   {"sp": 3}  horizontal space, mm
// Strings are printed as plain text; Typst markup is never evaluated.

#let data = json(sys.inputs.at("data", default: "worksheet.json"))
#let base = sys.inputs.at("base", default: ".")

#let colors = data.at("colors", default: (:))
#let ink = rgb(colors.at("ink", default: "#221F38"))
#let accent = rgb(colors.at("accent", default: "#D93D22"))
#let paper-tint = rgb(colors.at("paper", default: "#F6F3FB"))
#let grey-fill = rgb(colors.at("grey_fill", default: "#ECE8F4"))
#let muted = rgb(colors.at("muted", default: "#4B4864"))
#let rule-c = rgb(colors.at("rule", default: "#8E89A6"))
#let body-size = data.at("size", default: 11) * 1pt
#let title-size = data.at("title_size", default: 22) * 1pt
#let gap = data.at("gap", default: 3.5) * 1mm
#let labels = data.at("labels", default: (:))
#let icon-paths = data.at("icons", default: (:))

// ---------- helpers ----------

#let col(v, default: ink) = {
  if v == none { default }
  else if v == "ink" { ink }
  else if v == "accent" { accent }
  else if v == "paper" { paper-tint }
  else if v == "grey_fill" { grey-fill }
  else if v == "muted" { muted }
  else if v == "rule" { rule-c }
  else if v == "white" { white }
  else if v == "none" { none }
  else { rgb(v) }
}

// Numbers are mm; strings may be "1fr", "30%", "auto", "12mm", "10pt".
#let len(v) = {
  if v == none or v == "auto" { auto }
  else if type(v) == int or type(v) == float { v * 1mm }
  else if type(v) == str {
    if v.ends-with("fr") { float(v.slice(0, -2)) * 1fr }
    else if v.ends-with("%") { float(v.slice(0, -1)) * 1% }
    else if v.ends-with("mm") { float(v.slice(0, -2)) * 1mm }
    else if v.ends-with("pt") { float(v.slice(0, -2)) * 1pt }
    else { panic("worksheet: unknown length " + v) }
  } else { v }
}

#let resolve(p) = if p.starts-with("/") { p } else { base + "/" + p }

// Recolour a stroke icon (lucide and similar) and set it at the text size.
#let icon(name, color: ink, size: 1em) = {
  let p = icon-paths.at(name, default: none)
  if p == none { return [] }
  let hex = color.to-hex()
  let svg = read(resolve(p))
    .replace(regex("stroke=\"#[0-9A-Fa-f]{3,8}\""), "stroke=\"" + hex + "\"")
    .replace("currentColor", hex)
  box(height: size, baseline: 18%, image(bytes(svg), format: "svg", height: size))
}

#let tickbox(size: 1em) = box(baseline: 14%, rect(width: size, height: size, stroke: 1pt + ink, radius: 1.2pt))
#let blank(w) = box(width: len(w), height: 1.15em, baseline: 28%, stroke: (bottom: 0.8pt + ink))
#let field-box(w) = box(width: len(w), height: 1.45em, baseline: 32%, stroke: 0.8pt + ink, radius: 1pt)

// The 처리 / 판단 pair: 처리 = grey outline + word + repeat; 판단 = filled accent + word + brain.
// Colour never carries the meaning alone: the word and the icon are always printed.
#let mark(kind, label: none, size: 1em) = {
  let is-t = kind == "T"
  let lab = if label != none { label } else if is-t { labels.at("T", default: "판단") } else { labels.at("P", default: "처리") }
  let fg = if is-t { white } else { ink }
  // A box holding text keeps that text's baseline, so the chip needs no baseline shift.
  box(
    inset: (x: 0.4em, y: 0.24em),
    radius: 0.3em,
    fill: if is-t { accent } else { white },
    stroke: if is-t { 1pt + accent } else { 1pt + muted },
    {
      icon(if is-t { "brain" } else { "repeat" }, color: fg, size: 0.95em)
      h(0.22em)
      text(fill: fg, weight: "bold", size: size)[#lab]
    },
  )
}

// Korean word-break: keep-all. Typst would break a Hangul word between any two syllables, so each
// space-separated word goes in an unbreakable box and lines break only at spaces.
#let keep-all(s) = s.split(" ").map(w => box(w)).join(" ")

#let runs(r) = {
  if r == none { return [] }
  if type(r) == str or type(r) == int or type(r) == float { return keep-all(str(r)) }
  if type(r) == dictionary { r = (r,) }
  for x in r {
    if type(x) == str { keep-all(x) }
    else if type(x) == int or type(x) == float { [#str(x)] }
    else if "blank" in x { blank(x.blank) }
    else if "field" in x { field-box(x.field) }
    else if "box" in x { tickbox() }
    else if "sp" in x { h(x.sp * 1mm) }
    else if "tag" in x {
      // Optional (cycle 7): fill (a filled tag), text (its text colour; white on a fill by default),
      // radius and stroke (pt). Without them the tag is the 0.8 pt outlined box it always was.
      let c = col(x.at("color", default: none))
      let f = if "fill" in x { col(x.fill, default: none) } else { none }
      let tc = if "text" in x { col(x.text) } else if f != none { white } else { c }
      box(fill: f, stroke: x.at("stroke", default: 0.8) * 1pt + (if f != none and "color" not in x { f } else { c }),
        radius: x.at("radius", default: 1.2) * 1pt, inset: (x: 0.45em, y: 0.28em),
        text(weight: "bold", fill: tc)[#str(x.tag)])
    }
    else if "mark" in x { mark(x.mark, label: x.at("label", default: none)) }
    else if "icon" in x { icon(x.icon, color: col(x.at("color", default: none)), size: if "size" in x { x.size * 1pt } else { 1em }) }
    else if "br" in x { linebreak() }
    else if "text" in x {
      let args = (:)
      if x.at("bold", default: false) { args.insert("weight", "bold") }
      if "color" in x { args.insert("fill", col(x.color)) }
      if "size" in x { args.insert("size", x.size * 1pt) }
      let t = text(..args, keep-all(x.text))
      if x.at("strike", default: false) { strike(t) } else { t }
    }
  }
}

// A text style wrapper used by most blocks.
#let styled(b, body) = {
  let args = (:)
  if "size" in b { args.insert("size", b.size * 1pt) }
  if b.at("bold", default: false) { args.insert("weight", "bold") }
  if "color" in b { args.insert("fill", col(b.color)) }
  set text(..args)
  body
}

#let warnings = state("ws-warnings", ())

// ---------- blocks ----------

#let b-header(b) = {
  let fields = b.at("fields", default: ())
  block(width: 100%, fill: col(b.at("fill", default: "paper")), radius: 2mm, inset: (x: 5mm, y: 3.6mm), breakable: false)[
    #grid(
      columns: (1fr, auto),
      column-gutter: 6mm,
      align: (left + horizon, right + horizon),
      text(size: b.at("title_size", default: data.at("title_size", default: 22)) * 1pt, weight: "bold")[#runs(b.title)],
      if fields.len() > 0 {
        set text(size: body-size)
        fields.map(f => [#runs(f.label) #h(1.5mm) #blank(f.at("width", default: 30))]).join(h(5mm))
      },
    )
    #if b.at("meta", default: none) != none {
      v(1.2mm)
      text(size: b.at("meta_size", default: data.at("size", default: 11)) * 1pt, fill: muted)[#runs(b.meta)]
    }
  ]
}

#let b-text(b) = {
  let lines = if "lines" in b { b.lines } else { (b.at("body", default: ""),) }
  let content = styled(b, {
    set par(leading: b.at("leading", default: 0.75) * 1em, spacing: b.at("spacing", default: 0.9) * 1em)
    set align(if b.at("align", default: "left") == "center" { center } else if b.at("align", default: "left") == "right" { right } else { left })
    lines.map(l => runs(l)).join(parbreak())
  })
  if "fill" in b or "stroke" in b {
    block(width: 100%, fill: col(b.at("fill", default: "none"), default: none),
      stroke: if "stroke" in b { 0.8pt + col(b.stroke) } else { none },
      radius: 1.5mm, inset: (x: 3.5mm, y: 2.4mm), content)
  } else { block(width: 100%, content) }
}

#let b-table(b) = {
  let cols = b.columns
  let asked = b.at("row_height", default: 8)
  let rh = calc.max(asked, 7)
  if asked < 7 { warnings.update(w => w + ("table row_height " + str(asked) + " mm raised to the 7 mm minimum",)) }
  let pre = b.at("prefill", default: ())
  let n-empty = b.at("rows", default: 0)
  let total = pre.len() + n-empty
  let start = b.at("number_start", default: 1)
  let pre-h = b.at("prefill_height", default: rh)
  let head-h = len(b.at("head_height", default: "auto"))
  let cell-size = b.at("size", default: data.at("size", default: 11)) * 1pt
  let head-size = b.at("head_size", default: data.at("size", default: 11) - 1) * 1pt
  let aligns = cols.map(c => {
    let a = c.at("align", default: "left")
    (if a == "center" { center } else if a == "right" { right } else { left }) + horizon
  })
  let show-head = cols.any(c => c.at("head", default: none) != none)
  let heads = cols.map(c => table.cell(fill: col(b.at("head_fill", default: "grey_fill")), align: center + horizon,
    text(size: head-size, weight: "bold")[#runs(c.at("head", default: ""))]))
  let body = ()
  for i in range(total) {
    let row = if i < pre.len() { pre.at(i) } else { () }
    for (j, c) in cols.enumerate() {
      let v = if j < row.len() { row.at(j) } else { none }
      if v == none and c.at("number", default: false) { v = str(start + i) }
      let fill = none
      if type(v) == dictionary and "cell" in v {
        fill = col(v.at("fill", default: "none"), default: none)
        v = v.cell
      }
      body.push(table.cell(fill: fill, text(size: cell-size, fill: if c.at("number", default: false) { muted } else { ink })[#runs(v)]))
    }
  }
  // Every listed track makes a row in Typst, so add the empty-row size only when empty rows are asked for.
  let row-sizes = (if show-head { (head-h,) } else { () }) + (len(pre-h),) * pre.len() + (if n-empty > 0 { (rh * 1mm,) } else { () })
  table(
    columns: cols.map(c => len(c.at("width", default: "1fr"))),
    rows: row-sizes,
    align: aligns,
    inset: (x: 1.8mm, y: b.at("inset_y", default: 1.2) * 1mm),
    stroke: (x, y) => (
      left: 0.6pt + rule-c, right: 0.6pt + rule-c,
      top: if y == 0 { 1pt + ink } else if show-head and y == 1 { 1pt + ink } else { 0.6pt + rule-c },
      bottom: if y == total - 1 + (if show-head { 1 } else { 0 }) { 1pt + ink } else { 0.6pt + rule-c },
    ),
    ..(if show-head { (table.header(..heads),) } else { () }),
    ..body,
  )
}

#let b-checklist(b) = styled(b, {
  if b.at("title", default: none) != none { block(below: 1.6mm, text(weight: "bold")[#runs(b.title)]) }
  let items = b.items.map(it => grid(columns: (auto, 1fr), column-gutter: 1.8mm, align: horizon, tickbox(), runs(it)))
  grid(columns: (1fr,) * b.at("columns", default: 1), column-gutter: 4mm, row-gutter: b.at("row_gap", default: 2.4) * 1mm, ..items)
})

#let field-item(it, height) = {
  let lab = it.at("label", default: none)
  if "boxes" in it {
    let s = it.at("box_size", default: 6.5) * 1mm
    grid(columns: (auto, 1fr), column-gutter: 2.5mm, align: horizon,
      runs(lab),
      range(it.boxes).map(_ => box(rect(width: s, height: s, stroke: 0.8pt + ink, radius: 1pt))).join(h(1.6mm)))
  } else if it.at("lines", default: 1) > 1 {
    block(below: 0mm, runs(lab))
    for _ in range(it.lines) {
      block(above: 0mm, below: 0mm, width: 100%, height: height, stroke: (bottom: 0.7pt + rule-c))
    }
  } else {
    let w = len(it.at("width", default: "1fr"))
    let line = if it.at("style", default: "line") == "box" {
      box(width: 100%, height: height, stroke: 0.8pt + ink, radius: 1pt)
    } else {
      box(width: 100%, height: height, stroke: (bottom: 0.8pt + ink))
    }
    let has-label = lab != none and lab != "" and lab != ()
    grid(columns: (if has-label { (auto,) } else { () }) + (w,) + (if "suffix" in it { (auto,) } else { () }),
      column-gutter: 2mm, align: left + bottom,
      ..(if has-label { (box(height: height, align(bottom, pad(bottom: 1mm, runs(lab)))),) } else { () }),
      line,
      ..(if "suffix" in it { (box(height: height, align(bottom, pad(bottom: 1mm, runs(it.suffix)))),) } else { () }))
  }
}

#let b-fields(b) = styled(b, {
  let h = b.at("height", default: 8) * 1mm
  grid(columns: (1fr,) * b.at("columns", default: 1), column-gutter: b.at("gutter", default: 6) * 1mm,
    row-gutter: b.at("row_gap", default: 2.5) * 1mm,
    ..b.items.map(it => field-item(it, h)))
})

#let circled = ("①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩")
#let b-strip(b) = styled(b, {
  let n = b.at("count", default: b.at("items", default: ()).len())
  let items = b.at("items", default: ())
  let h = b.at("height", default: 9) * 1mm
  let bw = len(b.at("width", default: "1fr"))
  let sep = b.at("sep", default: "→")
  let cells = ()
  let widths = ()
  if b.at("label", default: none) != none { cells.push(runs(b.label)); widths.push(auto) }
  for i in range(n) {
    let it = if i < items.len() { items.at(i) } else { none }
    let num = text(weight: "bold", size: 1.15em)[#circled.at(i)]
    let inner = if it == none {
      box(width: 100%, height: h, stroke: 0.8pt + ink, radius: 1pt)
    } else {
      box(width: 100%, height: h, fill: col(b.at("fill", default: "paper")), radius: 1.5mm, inset: (x: 2mm),
        align(left + horizon, text(weight: "bold")[#runs(it)]))
    }
    cells.push(grid(columns: (auto, 1fr), column-gutter: 1.4mm, align: horizon, num, inner))
    widths.push(bw)
    if i < n - 1 { cells.push(text(fill: muted)[#sep]); widths.push(auto) }
  }
  grid(columns: widths, column-gutter: 1.8mm, align: horizon, ..cells)
})

#let b-oval(b) = styled(b, {
  if b.at("label", default: none) != none { block(below: 1.8mm, text(weight: "bold")[#runs(b.label)]) }
  align(center, ellipse(width: len(b.at("width", default: "100%")), height: b.at("height", default: 35) * 1mm, stroke: 1.2pt + ink))
})

#let b-lines(b) = styled(b, {
  if b.at("label", default: none) != none { block(below: 0mm, runs(b.label)) }
  for _ in range(b.at("count", default: 3)) {
    block(above: 0mm, below: 0mm, width: 100%, height: b.at("height", default: 8) * 1mm, stroke: (bottom: 0.6pt + rule-c))
  }
})

#let b-cut(b) = {
  v(1mm)
  grid(columns: (auto, 1fr), column-gutter: 2mm, align: horizon,
    text(size: 9pt, fill: muted)[#runs(b.at("label", default: "✂"))],
    line(length: 100%, stroke: (paint: rule-c, thickness: 0.8pt, dash: "dashed")))
  v(1mm)
}

// A picture (PNG, JPG or SVG; path relative to the JSON). width / height in mm or "100%"; with both,
// the picture keeps its aspect ratio inside that box (fit: contain). align: left | center | right.
#let b-image(b) = {
  let w = if "width" in b { len(b.width) } else if "height" in b { auto } else { 100% }
  let h = if "height" in b { len(b.height) } else { auto }
  let a = b.at("align", default: "center")
  let im = image(resolve(b.src), width: w, height: h, fit: "contain", alt: b.at("alt", default: none))
  let body = align(if a == "left" { left } else if a == "right" { right } else { center }, im)
  if "caption" in b {
    stack(dir: ttb, spacing: 1.6mm, body, styled(b, text(size: b.at("caption_size", default: data.at("size", default: 11) - 1) * 1pt, fill: muted)[#runs(b.caption)]))
  } else { body }
}

#let render-one(b, recurse) = {
  let t = b.at("type", default: "text")
  if t == "header" { b-header(b) }
  else if t == "text" { b-text(b) }
  else if t == "table" { b-table(b) }
  else if t == "checklist" { b-checklist(b) }
  else if t == "fields" { b-fields(b) }
  else if t == "strip" { b-strip(b) }
  else if t == "oval" { b-oval(b) }
  else if t == "lines" { b-lines(b) }
  else if t == "cut" { b-cut(b) }
  else if t == "space" { v(b.at("h", default: 4) * 1mm) }
  else if t == "rule" { line(length: len(b.at("width", default: "100%")), stroke: b.at("thickness", default: 0.5) * 1pt + col(b.at("color", default: "rule"))) }
  else if t == "image" { b-image(b) }
  else if t == "pagebreak" { pagebreak(weak: true) }
  else if t == "columns" {
    let cs = b.cols
    grid(
      columns: b.at("widths", default: (1fr,) * cs.len()).map(len),
      column-gutter: b.at("gutter", default: 5) * 1mm,
      align: top,
      ..cs.map(c => recurse(c, recurse)),
    )
  } else if t == "panel" {
    let title = b.at("title", default: none)
    block(
      width: 100%,
      height: if "height" in b { b.height * 1mm } else { auto },
      fill: col(b.at("fill", default: "none"), default: none),
      stroke: if b.at("stroke", default: "ink") == "none" { none } else { (if "stroke_width" in b { b.stroke_width * 1pt } else { 1pt }) + col(b.at("stroke", default: "ink")) },
      radius: 2mm,
      inset: b.at("inset", default: 3.6) * 1mm,
      breakable: false,
      {
        if title != none {
          block(below: 2.2mm, text(size: b.at("title_size", default: data.at("size", default: 11) + 1) * 1pt, weight: "bold")[#runs(title)])
        }
        recurse(b.at("blocks", default: ()), recurse)
      },
    )
  } else { panic("worksheet: unknown block type " + t) }
}

#let render(blocks, recurse) = {
  let out = ()
  for (i, b) in blocks.enumerate() {
    out.push(render-one(b, recurse))
    let t = b.at("type", default: "text")
    if i < blocks.len() - 1 and t != "pagebreak" and t != "space" and blocks.at(i + 1).at("type", default: "text") != "pagebreak" {
      out.push(v(if "gap_after" in b { b.gap_after * 1mm } else { gap }, weak: true))
    }
  }
  out.join()
}

// ---------- document ----------

#set document(title: data.at("title", default: "worksheet"))
#let m = data.at("margin", default: 12)
#set page(
  paper: data.at("paper", default: "a4"),
  flipped: data.at("flipped", default: false),
  margin: if type(m) == dictionary { (x: m.at("x", default: 12) * 1mm, top: m.at("top", default: 12) * 1mm, bottom: m.at("bottom", default: 12) * 1mm) } else { m * 1mm },
  footer: if data.at("footer", default: none) == none { none } else {
    context {
      set text(7.5pt, fill: muted)
      runs(data.footer)
      h(1fr)
      let total = counter(page).final().first()
      if total > 1 { counter(page).display("1 / 1", both: true) }
    }
  },
  footer-descent: 35%,
)
#set text(font: data.at("font", default: ("Malgun Gothic", "Noto Sans KR", "Apple SD Gothic Neo")), size: body-size,
  lang: "ko", region: "kr", fill: ink)
#set par(leading: 0.7em, spacing: 1.1em)
#show par: set block(spacing: 1.1em)

#render(data.blocks, render)

// Read by worksheet.py (typst query) for the page-fit check.
#context [#metadata((pages: counter(page).final().first(), warnings: warnings.final())) <ws-report>]
