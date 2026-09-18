import {describe, expect, it} from 'vitest';

import {
  CORE_EFFECT_KINDS,
  clampMemeFlashSeconds,
  effectRegistry,
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

  it('hard-caps meme flashes in render code', () => {
    expect(clampMemeFlashSeconds(0.1)).toBe(0.5);
    expect(clampMemeFlashSeconds(0.9)).toBe(0.9);
    expect(clampMemeFlashSeconds(8)).toBe(1.5);
  });
});
