import {describe, expect, it} from 'vitest';

import {SCENE_REGISTRY, sceneComponentFor} from './SceneRenderer';
import {resolveSceneAsset, scenePresentationStyle} from './presentation';
import type {AssetRecordV1, SceneSpecV1} from '../types';

const EXPECTED_SCENES = [
  'hook',
  'headline',
  'source_browser',
  'device',
  'github',
  'game_store',
  'stat',
  'chart',
  'timeline',
  'before_after',
  'comparison',
  'quote',
  'list',
  'process',
  'code',
  'map',
  'social_context',
  'chapter',
  'conclusion',
  'fallback_editorial',
].sort();

const scene: SceneSpecV1 = {
  id: 'source-scene',
  narration: 'Verified source context.',
  purpose: 'evidence',
  scene_type: 'source_browser',
  headline: 'Verified source',
  subheadline: '',
  source_ids: ['source_1'],
  asset_ids: [],
  motion: 'push_left',
  emphasis: [],
  transition: 'crossfade',
  fallback_scene_type: 'fallback_editorial',
  data: {source_url: 'https://example.com/source'},
};

const asset: AssetRecordV1 = {
  id: 'source-1',
  kind: 'source_screenshot',
  local_path: 'images/source-1.png',
  source_url: 'https://example.com/source',
  source_name: 'Example',
  usage: 'evidence',
  license_note: 'source-page screenshot',
  sha256: 'abc',
  captured_at: '2026-09-17T00:00:00+00:00',
};

describe('professional scene registry', () => {
  it('has exact parity with the Python scene vocabulary', () => {
    expect(Object.keys(SCENE_REGISTRY).sort()).toEqual(EXPECTED_SCENES);
  });

  it('maps every registered type to a component', () => {
    for (const type of EXPECTED_SCENES) {
      expect(sceneComponentFor(type)).toBeTypeOf('function');
    }
  });

  it('rejects renderer schema drift instead of guessing', () => {
    expect(() => sceneComponentFor('unknown_scene')).toThrow(/scene type/i);
  });

  it('resolves a verified source asset by source URL when the planner did not provide an asset id', () => {
    expect(resolveSceneAsset(scene, [asset])).toEqual(asset);
  });

  it('applies both scene motion and transition presentation', () => {
    const opening = scenePresentationStyle(scene, 0, 30);
    expect(opening.opacity).toBe(0);
    expect(String(opening.transform)).toContain('translateX');

    const settled = scenePresentationStyle(scene, 30, 30);
    expect(settled.opacity).toBe(1);
  });
});
