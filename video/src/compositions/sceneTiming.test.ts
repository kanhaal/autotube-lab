import {describe, expect, it} from 'vitest';

import {sceneFrameWindows} from './sceneTiming';
import type {RenderPackageV1} from '../types';

const pkg: RenderPackageV1 = {
  root: '.',
  manifest: {
    schema_version: '1',
    format: 'long',
    channel_id: 'kernelrush',
    channel_name: 'KernelRush',
    title: 'Timing',
    width: 1920,
    height: 1080,
    fps: 30,
    duration_source: 'audio',
    audio_path: '',
    theme: {},
  },
  script: {title: 'Timing', script: 'one two three four'},
  scenes: {
    schema_version: '1',
    channel_id: 'kernelrush',
    format: 'longform',
    scenes: [
      {
        id: 's1',
        narration: 'one two',
        purpose: 'first',
        scene_type: 'headline',
        headline: 'First',
        subheadline: '',
        source_ids: [],
        asset_ids: [],
        motion: 'none',
        emphasis: [],
        transition: 'cut',
        fallback_scene_type: 'fallback_editorial',
        data: {},
      },
      {
        id: 's2',
        narration: 'three four',
        purpose: 'second',
        scene_type: 'headline',
        headline: 'Second',
        subheadline: '',
        source_ids: [],
        asset_ids: [],
        motion: 'none',
        emphasis: [],
        transition: 'cut',
        fallback_scene_type: 'fallback_editorial',
        data: {},
      },
    ],
  },
  captions: {
    schema_version: '1',
    cues: [
      {start: 0, end: 1, text: 'one two', words: ['one', 'two']},
      {start: 1, end: 4, text: 'three four', words: ['three', 'four']},
    ],
  },
  assets: {schema_version: '1', records: []},
};

describe('scene timing', () => {
  it('uses aligned caption timing rather than proportional scene word counts', () => {
    const windows = sceneFrameWindows(pkg);
    expect(windows).toEqual([
      {from: 0, durationInFrames: 30},
      {from: 30, durationInFrames: 90},
    ]);
  });

  it('cuts at the exact aligned narration word instead of evenly interpolating the cue', () => {
    const exactPkg = structuredClone(pkg) as RenderPackageV1 & {
      captions: {
        schema_version: '1';
        cues: Array<RenderPackageV1['captions']['cues'][number] & {
          word_timings?: Array<{text: string; start: number; end: number}>;
        }>;
      };
    };
    exactPkg.captions.cues = [{
      start: 0,
      end: 4,
      text: 'one two three four',
      words: ['one', 'two', 'three', 'four'],
      word_timings: [
        {text: 'one', start: 0, end: 0.35},
        {text: 'two', start: 0.4, end: 0.8},
        {text: 'three', start: 2.8, end: 3.2},
        {text: 'four', start: 3.5, end: 4},
      ],
    }];

    expect(sceneFrameWindows(exactPkg)).toEqual([
      {from: 0, durationInFrames: 24},
      {from: 24, durationInFrames: 96},
    ]);
  });


  it('uses packaged audio duration as the authoritative minimum render length', () => {
    const audioTimed = structuredClone(pkg) as RenderPackageV1 & {
      manifest: RenderPackageV1['manifest'] & {duration_seconds: number};
    };
    audioTimed.manifest.duration_seconds = 5;
    audioTimed.captions.cues = [
      {start: 0, end: 1, text: 'one two', words: ['one', 'two']},
    ];

    expect(sceneFrameWindows(audioTimed).at(-1)).toEqual({
      from: expect.any(Number),
      durationInFrames: expect.any(Number),
    });
    const windows = sceneFrameWindows(audioTimed);
    const end = windows.at(-1)!;
    expect(end.from + end.durationInFrames).toBe(150);
  });
});
