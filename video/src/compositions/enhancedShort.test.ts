import {describe, expect, it} from 'vitest';

import {activeShortVisual} from './EnhancedShortComposition';
import type {RenderPackageV1} from '../types';

const pkg: RenderPackageV1 = {
  root: '.',
  manifest: {
    schema_version: '1', format: 'short', channel_id: 'kernelrush', channel_name: 'KernelRush',
    title: 'Short source', width: 1080, height: 1920, fps: 30, duration_source: 'audio',
    audio_path: '', theme: {},
  },
  script: {title: 'Short source', script: 'Verified source visual.'},
  scenes: {
    schema_version: '1', channel_id: 'kernelrush', format: 'short',
    scenes: [{
      id: 's1', narration: 'Verified source visual.', purpose: 'evidence',
      scene_type: 'source_browser', headline: 'Verified source', subheadline: '',
      source_ids: ['source_1'], asset_ids: [], motion: 'push_up', emphasis: [],
      transition: 'crossfade', fallback_scene_type: 'fallback_editorial',
      data: {source_url: 'https://example.com/source'},
    }],
  },
  captions: {
    schema_version: '1',
    cues: [{start: 0, end: 30, text: 'Verified source visual.', words: ['Verified', 'source', 'visual.']}],
  },
  assets: {
    schema_version: '1',
    records: [{
      id: 'source-1', kind: 'source_screenshot', local_path: 'images/source-1.png',
      source_url: 'https://example.com/source', source_name: 'Example', usage: 'evidence',
      license_note: 'source screenshot', sha256: 'abc', captured_at: '2026-09-17T00:00:00+00:00',
    }],
  },
};

describe('enhanced Short presentation', () => {
  it('selects the active scene verified asset and applies local scene motion', () => {
    const visual = activeShortVisual(pkg, 0);
    expect(visual?.asset?.local_path).toBe('images/source-1.png');
    expect(visual?.style.opacity).toBe(0);
    expect(String(visual?.style.transform)).toContain('translateY');
  });

  it.each(['device', 'github', 'game_store'])('uses verified screenshots for %s scenes', (sceneType) => {
    const productPkg: RenderPackageV1 = {
      ...pkg,
      scenes: {
        ...pkg.scenes,
        scenes: [{...pkg.scenes.scenes[0], scene_type: sceneType}],
      },
    };
    expect(activeShortVisual(productPkg, 0)?.asset?.local_path).toBe('images/source-1.png');
  });
});
