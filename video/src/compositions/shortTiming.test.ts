import {describe, expect, it} from 'vitest';

import type {RenderPackageV1} from '../types';
import {shortDurationFrames, validateShortPackage} from './shortTiming';

const shortPackage = (end = 36): RenderPackageV1 => ({
  root: '/tmp/package',
  manifest: {
    schema_version: '1',
    format: 'short',
    channel_id: 'kernelrush',
    channel_name: 'KernelRush',
    title: 'Short story',
    width: 1080,
    height: 1920,
    fps: 30,
    duration_source: 'audio',
    audio_path: 'audio/narration.wav',
    theme: {},
  },
  script: {title: 'Short story', script: 'Verified short narration.'},
  scenes: {
    schema_version: '1',
    channel_id: 'kernelrush',
    format: 'short',
    scenes: Array.from({length: 6}, (_, index) => ({
      id: `scene-${index + 1}`,
      narration: 'Verified short narration.',
      purpose: index === 0 ? 'hook' : 'explain',
      scene_type: index === 0 ? 'hook' : 'headline',
      headline: `Beat ${index + 1}`,
      subheadline: '',
      source_ids: ['source_1'],
      asset_ids: [],
      motion: 'snap',
      emphasis: [],
      transition: 'cut',
      fallback_scene_type: 'fallback_editorial',
      data: {},
    })),
  },
  captions: {
    schema_version: '1',
    cues: [{start: 0, end, text: 'Verified short narration.', words: ['Verified', 'short', 'narration.']}],
  },
  assets: {schema_version: '1', records: []},
});

describe('native Shorts render contract', () => {
  it('accepts a 1080x1920, 30-45 second, 5-12 scene package', () => {
    const pkg = shortPackage(36);
    expect(() => validateShortPackage(pkg)).not.toThrow();
    expect(shortDurationFrames(pkg)).toBe(1080);
  });

  it('rejects duration outside 30-45 seconds', () => {
    expect(() => validateShortPackage(shortPackage(29.9))).toThrow(/30-45/);
    expect(() => validateShortPackage(shortPackage(45.1))).toThrow(/30-45/);
  });

  it('rejects non-vertical dimensions or an invalid scene count', () => {
    const wrongSize = shortPackage();
    wrongSize.manifest.width = 1920;
    wrongSize.manifest.height = 1080;
    expect(() => validateShortPackage(wrongSize)).toThrow(/1080x1920/);

    const tooFew = shortPackage();
    tooFew.scenes.scenes = tooFew.scenes.scenes.slice(0, 4);
    expect(() => validateShortPackage(tooFew)).toThrow(/5-12/);
  });
});
