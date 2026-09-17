import {describe, expect, it} from 'vitest';

import {KERNELRUSH_LONG_THEME_ID} from '../compositions/KernelRushLong';
import {LOBBYSIGNAL_LONG_THEME_ID} from '../compositions/LobbySignalLong';
import {sceneFrameWindows} from '../compositions/sceneTiming';
import type {RenderPackageV1} from '../types';
import {kernelrushTheme} from './kernelrush';
import {lobbysignalTheme} from './lobbysignal';

const packageFixture = (): RenderPackageV1 => ({
  root: '/tmp/package',
  manifest: {
    schema_version: '1',
    format: 'long',
    channel_id: 'kernelrush',
    channel_name: 'KernelRush',
    title: 'Test',
    width: 1920,
    height: 1080,
    fps: 30,
    duration_source: 'audio',
    audio_path: 'audio/narration.wav',
    theme: {},
  },
  script: {title: 'Test', script: 'One two three four five six.'},
  scenes: {
    schema_version: '1',
    channel_id: 'kernelrush',
    format: 'longform',
    scenes: [
      {
        id: 's1', narration: 'one two', purpose: 'hook', scene_type: 'hook', headline: 'One', subheadline: '', source_ids: [], asset_ids: [], motion: 'push', emphasis: [], transition: 'cut', fallback_scene_type: 'fallback_editorial', data: {},
      },
      {
        id: 's2', narration: 'three four five six', purpose: 'body', scene_type: 'headline', headline: 'Two', subheadline: '', source_ids: [], asset_ids: [], motion: 'hold', emphasis: [], transition: 'cut', fallback_scene_type: 'fallback_editorial', data: {},
      },
    ],
  },
  captions: {
    schema_version: '1',
    cues: [
      {start: 0, end: 2, text: 'one two', words: ['one', 'two']},
      {start: 2, end: 6, text: 'three four five six', words: ['three', 'four', 'five', 'six']},
    ],
  },
  assets: {schema_version: '1', records: []},
});

describe('channel themes', () => {
  it('keeps the two brands materially distinct', () => {
    expect(kernelrushTheme.id).not.toBe(lobbysignalTheme.id);
    expect(kernelrushTheme.accent).not.toBe(lobbysignalTheme.accent);
    expect(kernelrushTheme.secondary).not.toBe(lobbysignalTheme.secondary);
    expect(kernelrushTheme.motionIntensity).not.toBe(lobbysignalTheme.motionIntensity);
    expect(kernelrushTheme.transitionFamily).not.toBe(lobbysignalTheme.transitionFamily);
  });

  it('binds each long composition to its own theme', () => {
    expect(KERNELRUSH_LONG_THEME_ID).toBe(kernelrushTheme.id);
    expect(LOBBYSIGNAL_LONG_THEME_ID).toBe(lobbysignalTheme.id);
  });

  it('derives scene timing from narration weight within aligned caption duration', () => {
    const windows = sceneFrameWindows(packageFixture());
    expect(windows).toHaveLength(2);
    expect(windows[0]).toEqual({from: 0, durationInFrames: 60});
    expect(windows[1]).toEqual({from: 60, durationInFrames: 120});
    expect(windows.at(-1)!.from + windows.at(-1)!.durationInFrames).toBe(180);
  });
});
