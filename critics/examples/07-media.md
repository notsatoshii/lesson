# 07 Media: examples

Fictional lesson for every example: band E office workers, online mode, "메일 세 폴더로 정리하기" (sort the inbox into three folders). Learner-facing lines are Korean because the example house rules ask for Korean. No facts or numbers here are real; any number in an asset is marked.

## 4

```
| S2 | 9 | learn | 세 폴더 규칙 | Narrator explains the three folders over one slide | see · listen | M2, M3 | – | – |

## Media list
| M2 | slide | S2 | shows the rules | brief |
| M3 | video 8 min | S2 | walkthrough of the inbox | brief |

M2 on screen: "받은편지함의 메일을 먼저 읽고, 답장이 필요한 메일은 '답장' 폴더로, 나중에 읽을 메일은 '보관' 폴더로 옮깁니다."
M3: record a walkthrough of sorting the inbox. Voice reads the M2 slide, then keeps going.
(no media/ folder beside the plan)
```

Why a 4: two rows with no brief at all; the slide is a paragraph the voice reads word for word (redundancy); an 8-minute block with no storyboard, no pause and no question at the end; the Purpose "shows the rules" says nothing the learner can now do; the process in the slide text wants to be a three-box flow.

## 7

```
M2 · diagram · S2 · tool: tools/diagram/render.py · icon family: lucide, 2 px · export: PNG at 2x
- shows: 받은편지함 → 답장 / 보관 / 삭제, one arrow per rule
- labels: in a legend under the diagram (1 = 답장, 2 = 보관, 3 = 삭제)
- reading order: top box, then left to right

M3 · video 50 s · S2 · tool: tools/video/
| 0–8 s  | inbox with 12 unread | "메일이 쌓이면 어디부터 보시나요?" | hook |
| 8–40 s | three folders fill   | "답장이 필요한 메일은 답장 폴더로 옮깁니다." | captions on |
| 40–50 s| folder names         | "다음은 보관 기준을 보겠습니다." | ends on a tease |
(no voice: line)
```

Why a 7: briefs exist with tools, one icon family, PNG at 2x, captions on and a short storyboard; the gaps are a legend instead of labels on the boxes (contiguity), a block that ends on "다음은…" instead of a retrieval question, and no `voice:` line.

## 9

```
M1 · icon set · S1 · tool: tools/icons.py · icon family: lucide, 2 px
- icons: 답장 → reply, 보관 → archive, 삭제 → trash-2; each used in S1, S2, S4 and the handout

M3 · video 45 s · S2 · tool: tools/narrate.py, then tools/video/ · voice: Korean neural voice, 존댓말, calm (draft) / final voice picked at publish
| 0–6 s   | M1 icons with their names     | "오늘 쓸 폴더는 세 개입니다."               | parts first |
| 6–30 s  | one mail moves to 답장, label on the folder | "답장이 필요하면 여기로 옮깁니다."  | on screen: 답장 only |
| 30–45 s | question: 이 메일은 어디로?    | "직접 골라 보세요."                        | learner taps a folder before S3 opens |
Facts shown: the inbox count on screen is [needs fact: sample inbox size from the client's example account] · alt text: 메일 한 통이 답장 폴더로 옮겨지는 장면입니다.
```

Why a 9: part names arrive before the process; the label sits on the folder it names; on-screen text is the key term while the voice carries the sentence, captions on; the block ends in an on-screen question the learner answers before going on; `tool:`, `voice:`, icon family and alt text are all present; the one number on screen is marked, not invented.

## Pairs

- **Every learn segment carries a mechanism visual:** good: "S2 learn → M2 flow: 받은편지함 → 답장 / 보관 / 삭제". bad: "S2 learn → M2 photo of an office worker smiling at a laptop".
- **Every row has a brief:** good: "Media list M3 ↔ media/M3.md, same id in the heading". bad: "Media list M3, no media/M3.md; media/M5.md with no row".
- **Purpose passes the test:** good: "After this, the learner can say which folder a mail goes to from its first line." bad: "Breaks up the text and adds energy."
- **Replaces line is real:** good: "Replaces the 90-second spoken explanation of the three rules in S2." bad: "Replaces: nothing, shown alongside the talk."
- **Segmenting:** good: "Three 15-second chunks, each ends with a 계속 button the learner taps." bad: "One continuous recording, no pause points."
- **Video blocks about 6 minutes or less, each ending in a retrieval question:** good: "Block 1 ends: 이 메일은 어느 폴더로 갈까요? (tap to answer)". bad: "Block 1 runs on for the whole lesson and ends: 다음 시간에 계속하겠습니다."
- **Contiguity:** good: "The word 보관 sits on the archive folder in the diagram." bad: "Numbers on the boxes, a legend below explains them."
- **Pre-training:** good: "S1 shows the three folder icons with their names before the S2 animation." bad: "The animation names the folders as mails fly into them."
- **Redundancy, captions kept:** good: "On screen: 답장 · voice: 답장이 필요하면 여기로 옮깁니다 · captions on." bad: "On screen: the full sentence, voice reads it aloud, captions turned off to reduce clutter."
- **Icons:** good: "icon family: lucide, 2 px on every brief; each icon used three times." bad: "M1 uses lucide, M4 uses a filled set; trash appears once."
- **PNG at 2x, not system-font SVG:** good: "export: PNG at 2x, Malgun Gothic rendered in." bad: "export: SVG, font-family: sans-serif."
- **Voice and tool lines:** good: "tool: tools/narrate.py then tools/video/ · voice: Korean neural voice, 존댓말, calm". bad: "Video brief with a storyboard and no tool or voice line."
- **Screenshots for install and how-to:** good: "One shot per step, callouts 1 to 3 in action order, account name blurred, light theme, Korean UI." bad: "One shot for five steps with seven callouts and the learner's email address visible."
- **Numbers have sources:** good: "Inbox count on screen: [needs fact: sample inbox size], placeholder visible." bad: "Chart title: 이 방법으로 하루 1시간을 아낍니다 (no source)."
- **Alt text present:** good: "메일 한 통이 답장 폴더로 옮겨지는 장면입니다." bad: "diagram"
- **Producible with the named tooling:** good: "tool: tools/diagram/render.py, 5 boxes, top to bottom." bad: "tool: a designer will make something nice."
