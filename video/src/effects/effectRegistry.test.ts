import {describe, expect, it} from 'vitest';

import {
  EFFECT_KINDS,
  effectRegistry,
  memeFlashDurationFrames,
  transitionRegistry,
} from './effectRegistry';

describe('effectRegistry', () => {
  it('registers every supported effect kind centrally', () => {
    expect(Object.keys(effectRegistry).sort()).toEqual([...EFFECT_KINDS].sort());
  });

  it('registers both selectable transition_out effects', () => {
    expect(Object.keys(transitionRegistry).sort()).toEqual(['glitch_rgb_split', 'whoosh_zoom']);
  });

  it('hard clamps meme flashes to 0.5-1.5 seconds', () => {
    expect(memeFlashDurationFrames(0.1, 30)).toBe(15);
    expect(memeFlashDurationFrames(0.9, 30)).toBe(27);
    expect(memeFlashDurationFrames(4, 30)).toBe(45);
  });
});
