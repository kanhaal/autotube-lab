import {describe, expect, it} from 'vitest';

import {
  CORE_EFFECT_KINDS,
  clampMemeFlashSeconds,
  effectRegistry,
  mediaPlaybackRateForScene,
  sceneHasEffect,
  transitionRegistry,
} from './effectRegistry';

describe('V3.5 effect registry', () => {
  it('registers every requested core effect in one lookup', () => {
    expect(Object.keys(effectRegistry).sort()).toEqual([...CORE_EFFECT_KINDS].sort());
  });

  it('registers the selectable V3.5 transition-out effects', () => {
    expect(Object.keys(transitionRegistry).sort()).toEqual(
      ['glitch_rgb_split', 'whoosh_zoom'].sort(),
    );
  });

  it('centralizes effect-presence and gameplay speed-ramp lookup', () => {
    const scene = {
      id: 's1',
      narration: 'Gameplay slows here.',
      purpose: 'demo',
      scene_type: 'source_browser',
      headline: '',
      subheadline: '',
      source_ids: [],
      asset_ids: [],
      motion: 'none',
      emphasis: [],
      transition: 'cut',
      fallback_scene_type: 'fallback_editorial',
      data: {},
      effects: [
        {kind: 'speed_ramp' as const, start_seconds: 1, end_seconds: 2, min_rate: 0.5},
      ],
    };

    expect(sceneHasEffect(scene, 'speed_ramp')).toBe(true);
    expect(sceneHasEffect(scene, 'kinetic_word_reveal')).toBe(false);
    expect(mediaPlaybackRateForScene(scene, 45, 30)).toBeLessThan(1);
    expect(mediaPlaybackRateForScene(scene, 150, 30)).toBe(1);
  });

  it('hard-caps meme flashes in render code', () => {
    expect(clampMemeFlashSeconds(0.1)).toBe(0.5);
    expect(clampMemeFlashSeconds(0.9)).toBe(0.9);
    expect(clampMemeFlashSeconds(8)).toBe(1.5);
  });
});
