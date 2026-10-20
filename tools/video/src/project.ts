import {makeProject} from '@revideo/core';
import storyboard from './scenes/storyboard';

// The scene JSON written by storyboard.py arrives as the `scene` variable
// (render.mjs passes it to renderVideo). This default only shows in the editor.
export default makeProject({
  scenes: [storyboard],
  variables: {
    scene: {
      width: 1080,
      height: 1920,
      font: 'Noto Sans KR',
      rows: [
        {
          index: 1,
          start: 0,
          duration: 3,
          screen: {kind: 'text', text: '스토리보드 미리보기'},
          captions: [{text: 'storyboard.py가 장면 JSON을 넘겨 줍니다.', start: 0, end: 3}],
        },
      ],
    },
  },
});
