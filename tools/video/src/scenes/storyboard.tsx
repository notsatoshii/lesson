import {Img, Layout, Rect, Txt, makeScene2D} from '@revideo/2d';
import {all, createRef, useScene, waitFor} from '@revideo/core';

// One storyboard row = one beat: on-screen text and/or image, plus caption
// pages shown at the times storyboard.py computed (seconds from row start).
type Caption = {text: string; start: number; end: number};
// frame: a tall-stage row (note "stage: tall"), laid out by storyboard.py in px from the top-left corner.
type Frame = {head_top: number; head_h: number; card: number[]; img: number[]; cpad: number; cap_foot: number; cap_h: number};
type Screen = {kind: 'text' | 'image'; text?: string; src?: string; head_px?: number; frame?: Frame};
type Row = {index: number; start: number; duration: number; screen: Screen; captions: Caption[]};
type Layout_ = {pad: number; head_px: number; cap_px: number; cap_bottom: number; head_w: number; cap_w: number};
type Scene = {width: number; height: number; font: string; theme?: Record<string, string>; layout?: Layout_; rows: Row[]};

const FADE = 0.25;

export default makeScene2D('storyboard', function* (view) {
  const scene = useScene().variables.get('scene', null as unknown as Scene)();
  const W = scene.width;
  const H = scene.height;
  const portrait = H > W;
  const short = portrait ? W : H;
  const theme = {bg: '#F7F5F2', ink: '#1A1A1A', card: '#FFFFFF', capBg: '#111111', capInk: '#FFFFFF', accent: '#FF4D2E', ...(scene.theme ?? {})};
  const font = `${scene.font}, 'Noto Sans KR', 'Malgun Gothic', sans-serif`;
  // Sizes come from storyboard.py (same numbers as its ffmpeg engine); fallbacks for the editor.
  const L = scene.layout ?? {
    pad: Math.round(W * 0.07),
    head_px: Math.round(short * (portrait ? 0.075 : 0.07)),
    cap_px: Math.round(short * (portrait ? 0.048 : 0.042)),
    cap_bottom: Math.round(H * (portrait ? 0.12 : 0.08)),
    head_w: W - Math.round(W * 0.07) * 2,
    cap_w: Math.round(W - W * 0.07 * 3.6),
  };
  const pad = L.pad;
  const capSize = L.cap_px;
  const capBottom = L.cap_bottom;

  view.fill(theme.bg);

  for (const row of scene.rows) {
    const stage = createRef<Layout>();
    const cap = createRef<Txt>();
    const capBox = createRef<Rect>();
    const hasImage = row.screen.kind === 'image' && !!row.screen.src;
    const headline = row.screen.text ?? '';
    const headPx = row.screen.head_px ?? L.head_px;
    const headH = headline ? headPx * 1.3 * headline.split(String.fromCharCode(10)).length + pad * 0.6 : 0;
    // Room above the caption band for the visual.
    const stageH = H - capBottom * 2 - capSize * 4;

    const fr = hasImage ? row.screen.frame : undefined;
    if (fr) {
      // Tall stage: one-line headline at the top padding, the picture card under it at its computed size
      // (scale up to 1.0), the caption bar pinned at the foot (below).
      const [cx, cy, cw, ch] = fr.card;
      view.add(
        <Layout ref={stage} width={W} height={H} opacity={0}>
          {headline && (
            <Txt text={headline} fontFamily={font} fontWeight={700} fontSize={headPx} lineHeight={'130%'}
                 fill={theme.ink} textWrap={'pre'} textAlign="center" width={L.head_w}
                 y={fr.head_top + fr.head_h / 2 - H / 2} />
          )}
          <Rect fill={theme.card} radius={24} shadowBlur={30} shadowColor={'#0000001f'}
                x={cx + cw / 2 - W / 2} y={cy + ch / 2 - H / 2} width={cw} height={ch}>
            <Img src={row.screen.src} width={fr.img[0]} height={fr.img[1]} />
          </Rect>
        </Layout>,
      );
    } else {
      view.add(
        <Layout ref={stage} layout direction="column" alignItems="center" justifyContent="center"
                gap={pad * 0.6} width={W - pad * 2} height={stageH} y={-(H - stageH) / 2 + pad} opacity={0}>
          {headline && (
            <Txt text={headline} fontFamily={font} fontWeight={700} fontSize={headPx}
                 lineHeight={'130%'} fill={theme.ink} textWrap={'pre'} textAlign="center" />
          )}
          {hasImage && (
            <Rect fill={theme.card} radius={24} padding={pad * 0.3} shadowBlur={30} shadowColor={'#0000001f'}>
              <Img src={row.screen.src} maxWidth={W - pad * 2.6} maxHeight={stageH - headH - pad} />
            </Rect>
          )}
        </Layout>,
      );
    }
    view.add(
      <Rect ref={capBox} layout fill={theme.capBg} radius={18} padding={[capSize * 0.45, capSize * 0.8]}
            y={H / 2 - (fr ? fr.cap_foot : capBottom)} offsetY={1} opacity={0} maxWidth={W - pad * 2}>
        <Txt ref={cap} text={''} fontFamily={font} fontWeight={500} fontSize={capSize} lineHeight={'135%'}
             fill={theme.capInk} textWrap={'pre'} textAlign="center" />
      </Rect>,
    );

    yield* stage().opacity(1, Math.min(FADE, row.duration / 4));
    let t = Math.min(FADE, row.duration / 4);
    for (const c of row.captions) {
      if (c.start > t) {
        yield* waitFor(c.start - t);
        t = c.start;
      }
      cap().text(c.text);
      capBox().opacity(1);
      const hold = Math.max(0, c.end - t);
      yield* waitFor(hold);
      t += hold;
      capBox().opacity(0);
    }
    const tailFade = Math.min(FADE, row.duration / 4);
    if (row.duration - tailFade > t) yield* waitFor(row.duration - tailFade - t);
    yield* all(stage().opacity(0, tailFade), capBox().opacity(0, tailFade));
    stage().remove();
    capBox().remove();
  }
});
