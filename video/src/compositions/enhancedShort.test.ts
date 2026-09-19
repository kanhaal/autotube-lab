import {describe, expect, it} from 'vitest';

import {activeShortVisual, shouldUseLegacySourceOverlay} from './EnhancedShortComposition';
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

  it('prefers the asset explicitly captured for the active scene over a same-purpose asset', () => {
    const boundPkg: RenderPackageV1 = {
      ...pkg,
      scenes: {
        ...pkg.scenes,
        scenes: [{...pkg.scenes.scenes[0], data: {}}],
      },
      assets: {
        schema_version: '1',
        records: [
          {
            id: 'wrong', kind: 'source_screenshot', local_path: 'images/wrong.png',
            source_url: 'https://example.com/wrong', source_name: 'Wrong', usage: 'evidence',
            license_note: 'source screenshot', sha256: 'wrong', captured_at: '2026-09-17T00:00:00+00:00',
            scene_id: 's2',
          },
          {
            id: 'right', kind: 'source_screenshot', local_path: 'images/right.png',
            source_url: 'https://example.com/right', source_name: 'Right', usage: 'evidence',
            license_note: 'source screenshot', sha256: 'right', captured_at: '2026-09-17T00:00:00+00:00',
            scene_id: 's1',
          },
        ],
      },
    };

    expect(activeShortVisual(boundPkg, 0)?.asset?.local_path).toBe('images/right.png');
  });

  it('renders an original fallback card when optional source capture fails', () => {
    const fallbackPkg: RenderPackageV1 = {
      ...pkg,
      scenes: {
        ...pkg.scenes,
        scenes: [{...pkg.scenes.scenes[0], data: {}}],
      },
      assets: {
        schema_version: '1',
        records: [{
          id: 'fallback-s1', kind: 'fallback_editorial', local_path: 'images/fallback-s1.png',
          source_url: null, source_name: null, usage: 'evidence', scene_id: 's1',
          license_note: 'original AutoTube generated graphic', sha256: 'fallback',
          captured_at: '2026-09-17T00:00:00+00:00',
        }],
      },
    };

    expect(activeShortVisual(fallbackPkg, 0)?.asset?.local_path).toBe('images/fallback-s1.png');
  });


  it('preloads the incoming source visual during an overlapped edit', () => {
    const transitionPkg = structuredClone(pkg);
    transitionPkg.scenes.scenes = [
      {
        ...transitionPkg.scenes.scenes[0],
        id: 's1',
        narration: 'first',
        asset_ids: ['source-1'],
      },
      {
        ...transitionPkg.scenes.scenes[0],
        id: 's2',
        narration: 'second',
        asset_ids: ['source-2'],
      },
    ];
    transitionPkg.captions.cues = [{
      start: 0,
      end: 30,
      text: 'first second',
      words: ['first', 'second'],
      word_timings: [
        {text: 'first', start: 0, end: 15},
        {text: 'second', start: 15, end: 30},
      ],
    }];
    transitionPkg.assets.records = [
      {...transitionPkg.assets.records[0], id: 'source-1', local_path: 'images/source-1.png', scene_id: 's1'},
      {...transitionPkg.assets.records[0], id: 'source-2', local_path: 'images/source-2.png', scene_id: 's2'},
    ];

    expect(activeShortVisual(transitionPkg, 447)?.scene.id).toBe('s2');
  });
});


describe('V4 Short overlay routing', () => {
  it('does not stack the legacy source card on top of V4 directed shots', () => {
    const v4 = structuredClone(pkg);
    v4.manifest.render_effects = {v4_editor: true};
    expect(shouldUseLegacySourceOverlay(v4)).toBe(false);
  });

  it('keeps the legacy overlay available for non-V4 packages', () => {
    const legacy = structuredClone(pkg);
    legacy.manifest.render_effects = {v4_editor: false};
    expect(shouldUseLegacySourceOverlay(legacy)).toBe(true);
  });
});
