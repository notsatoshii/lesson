// Render a scene JSON (written by storyboard.py) to a silent MP4 with Revideo.
// Usage: node render.mjs <scene.json> <out.mp4>
// storyboard.py calls this; audio is muxed afterwards with the system ffmpeg.
import {renderVideo} from '@revideo/renderer';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

process.env.DISABLE_TELEMETRY = 'true';
const here = path.dirname(fileURLToPath(import.meta.url));
process.chdir(here); // renderVideo resolves projectFile against cwd

const [sceneFile, outArg] = process.argv.slice(2);
if (!sceneFile || !outArg) {
  console.error('usage: node render.mjs <scene.json> <out.mp4>');
  process.exit(2);
}
const scene = JSON.parse(fs.readFileSync(sceneFile, 'utf8'));
const out = path.resolve(outArg);

const chromeCandidates = [
  process.env.CHROME_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  '/usr/bin/google-chrome',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
].filter(Boolean);
const executablePath = chromeCandidates.find(p => fs.existsSync(p));
// Prefer the system ffmpeg when it is on PATH; Revideo falls back to its bundled one.
if (scene.ffmpeg && fs.existsSync(scene.ffmpeg)) process.env.FFMPEG_PATH = scene.ffmpeg;

const file = await renderVideo({
  projectFile: './src/project.ts',
  variables: {scene},
  settings: {
    outFile: path.basename(out).replace(/\.[^.]+$/, '') + '.mp4',
    outDir: path.dirname(out),
    logProgress: false,
    workers: 1,
    projectSettings: {
      size: {x: scene.width, y: scene.height},
      background: scene.theme?.bg ?? '#F7F5F2',
      exporter: {name: '@revideo/core/ffmpeg', options: {format: 'mp4'}},
    },
    puppeteer: executablePath ? {executablePath, headless: true} : {headless: true},
  },
});
console.log(JSON.stringify({ok: true, file}));
process.exit(0);
