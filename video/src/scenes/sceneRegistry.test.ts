import {describe, expect, it} from 'vitest';

import {SCENE_REGISTRY, sceneComponentFor} from './SceneRenderer';

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
});
