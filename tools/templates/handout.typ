// Printable step handout for guide-mode lessons. Filled by tools/guide.py --handout.
// Compile by hand: typst compile --input data=handout.json handout.typ out.pdf
// Data (JSON): title, meta, steps: [{n, title, instruction, expected, image, missing}], labels: {notes}.
// Image paths are relative to this file; guide.py copies the template, data and images into one build folder.

#let data = json(sys.inputs.at("data", default: "handout.json"))
#let accent = rgb("#FF4D2E")
#let ink = rgb("#1A1D21")
#let muted = rgb("#6B7280")
#let rule = rgb("#D9DCE1")
#let labels = data.at("labels", default: (:))
#let notes-label = labels.at("notes", default: "메모")
#let lines-per-step = data.at("lines", default: 5)

#set document(title: data.title)
#set page(
  paper: "a4",
  margin: (x: 16mm, top: 16mm, bottom: 18mm),
  footer: context [
    #set text(8pt, fill: muted)
    #data.title #h(1fr) #counter(page).display("1 / 1", both: true)
  ],
)
// Korean first; Malgun Gothic on Windows, Noto Sans KR elsewhere. Fallback stays on so no glyph is dropped.
#set text(font: ("Malgun Gothic", "Noto Sans KR", "Apple SD Gothic Neo"), size: 10.5pt, lang: "ko", region: "kr", fill: ink)
#set par(leading: 0.8em)

// Title
#block(width: 100%, inset: (bottom: 4mm), stroke: (bottom: 1.2pt + ink))[
  #text(20pt, weight: "bold")[#data.title]
  #if data.at("meta", default: none) != none [
    #v(1mm)
    #text(10pt, fill: muted)[#data.meta]
  ]
]
#v(3mm)

#let badge(n) = box(
  circle(radius: 3.6mm, fill: accent, stroke: none)[
    #set align(center + horizon)
    #text(10pt, weight: "bold", fill: white)[#n]
  ],
)

#let shot(s) = {
  if s.at("image", default: none) != none {
    box(stroke: 0.5pt + rule, radius: 2mm, clip: true, image(s.image, width: 48mm))
  } else {
    box(width: 48mm, height: 36mm, radius: 2mm, stroke: (paint: rule, dash: "dashed"), inset: 3mm)[
      #set align(center + horizon)
      #text(8.5pt, fill: muted)[#s.at("missing", default: "")]
    ]
  }
}

#for s in data.steps {
  block(breakable: false, width: 100%, inset: (y: 4mm), stroke: (bottom: 0.5pt + rule))[
    #grid(
      columns: (48mm, 1fr),
      column-gutter: 7mm,
      shot(s),
      [
        #grid(
          columns: (auto, 1fr),
          column-gutter: 2.5mm,
          align: horizon,
          badge(s.n),
          text(13pt, weight: "bold")[#s.instruction],
        )
        #if s.at("expected", default: none) != none [
          #v(2mm)
          #block(width: 100%, fill: rgb("#EEF7F1"), radius: 1.5mm, inset: (x: 3mm, y: 2.2mm))[
            #text(fill: rgb("#17633A"))[✓ #s.expected]
          ]
        ]
        #v(4mm)
        #text(8.5pt, fill: muted)[#notes-label]
        #for i in range(lines-per-step) {
          v(7mm)
          line(length: 100%, stroke: 0.4pt + rule)
        }
      ],
    )
  ]
}
