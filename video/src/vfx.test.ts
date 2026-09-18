import {describe, expect, it} from 'vitest';

import {
  cinematicCameraStyle,
  editorialFocusWeight,
  editorialItemStyle,
  editorialLineProgress,
  headlineWordProgress,
  narrationEmphasisBeat,
  premiumVfxProfile,
  sourceMediaStyle,
  transitionAccentState,
} from './vfx';

describe('premium editorial VFX', () => {
  it('gives scenes a subtle dimensional camera move without ever becoming flat', () => {
    const opening = cinematicCameraStyle(0, 180, 30, 'precision', 0.8);
    const middle = cinematicCameraStyle(90, 180, 30, 'precision', 0.8);

    expect(String(opening.transform)).toContain('perspective(');
    expect(String(opening.transform)).toContain('scale(');
    expect(String(middle.transform)).toContain('rotateY(');
    expect(middle.transform).not.toBe(opening.transform);
  });

  it('stagger-reveals headline words fast enough for editorial typography', () => {
    expect(headlineWordProgress(0, 30, 0)).toBe(0);
    expect(headlineWordProgress(8, 30, 0)).toBeGreaterThan(0.5);
    expect(headlineWordProgress(8, 30, 3)).toBeLessThan(headlineWordProgress(8, 30, 0));
    expect(headlineWordProgress(30, 30, 3)).toBeCloseTo(1, 3);
  });

  it('uses different VFX art direction for precision and snap channels', () => {
    const precision = premiumVfxProfile('precision', 0.72);
    const snap = premiumVfxProfile('snap', 1.15);

    expect(precision.gridOpacity).toBeGreaterThan(0);
    expect(snap.streakOpacity).toBeGreaterThan(precision.streakOpacity);
    expect(snap.transitionBoost).toBeGreaterThan(precision.transitionBoost);
  });

  it('gives repeated cards staggered physical motion instead of appearing as a block', () => {
    const first = editorialItemStyle(0, 30, 0, 'precision');
    const later = editorialItemStyle(12, 30, 2, 'snap');

    expect(first.opacity).toBe(0);
    expect(String(first.transform)).toContain('translate3d(');
    expect(Number(later.opacity)).toBeGreaterThan(0);
    expect(String(later.transform)).toContain('scale(');
  });

  it('keeps editorial cards dimensional with channel-specific restrained perspective', () => {
    const precision = editorialItemStyle(9, 30, 0, 'precision');
    const snap = editorialItemStyle(9, 30, 0, 'snap');

    expect(String(precision.transform)).toContain('perspective(');
    expect(String(precision.transform)).toContain('rotateY(');
    expect(String(snap.transform)).toContain('perspective(');
    expect(snap.transform).not.toBe(precision.transform);
  });

  it('hands process attention forward instead of pinning focus to the first step', () => {
    const firstEarly = editorialFocusWeight(18, 180, 0, 3);
    const thirdEarly = editorialFocusWeight(18, 180, 2, 3);
    const firstLate = editorialFocusWeight(150, 180, 0, 3);
    const thirdLate = editorialFocusWeight(150, 180, 2, 3);

    expect(firstEarly).toBeGreaterThan(thirdEarly);
    expect(thirdLate).toBeGreaterThan(firstLate);
    expect(firstEarly).toBeLessThanOrEqual(1);
    expect(thirdLate).toBeLessThanOrEqual(1);
  });

  it('reveals editorial code and quote lines with measured channel-aware cadence', () => {
    const firstPrecision = editorialLineProgress(12, 30, 0, 'precision');
    const fourthPrecision = editorialLineProgress(12, 30, 3, 'precision');
    const firstSnap = editorialLineProgress(12, 30, 0, 'snap');

    expect(firstPrecision).toBeGreaterThan(fourthPrecision);
    expect(firstSnap).toBeGreaterThan(firstPrecision);
    expect(editorialLineProgress(0, 30, 0, 'precision')).toBe(0);
    expect(editorialLineProgress(60, 30, 4, 'precision')).toBeCloseTo(1, 3);
  });

  it('only emits narration micro-beats for emphasized words and spoken numbers', () => {
    const cues = [{
      start: 1,
      end: 3,
      text: 'The model jumps 42 percent today',
      words: ['The', 'model', 'jumps', '42', 'percent', 'today'],
      word_timings: [
        {text: 'The', start: 1.0, end: 1.2},
        {text: 'model', start: 1.2, end: 1.6},
        {text: 'jumps', start: 1.6, end: 1.9},
        {text: '42', start: 1.9, end: 2.2},
        {text: 'percent', start: 2.2, end: 2.55},
        {text: 'today', start: 2.55, end: 3.0},
      ],
    }];

    expect(narrationEmphasisBeat(cues, 1.4, ['jumps'])).toEqual({word: '', strength: 0});
    expect(narrationEmphasisBeat(cues, 1.75, ['jumps']).word).toBe('jumps');
    expect(narrationEmphasisBeat(cues, 1.75, ['jumps']).strength).toBeGreaterThan(0.5);
    expect(narrationEmphasisBeat(cues, 2.05, []).word).toBe('42');
    expect(narrationEmphasisBeat(cues, 2.05, []).strength).toBeGreaterThan(0.5);
  });

  it('creates a multi-layer transition accent instead of a single flat fade', () => {
    const opening = transitionAccentState(0, 30, 'snap', 1.1);
    const active = transitionAccentState(4, 30, 'snap', 1.1);

    expect(opening.primary).toBeGreaterThan(0);
    expect(active.secondary).toBeGreaterThan(0);
    expect(active.offsetPx).not.toBe(0);
  });

  it('gives source footage a living push-in and slight perspective drift', () => {
    const start = sourceMediaStyle(0, 180, 30, 0.8);
    const later = sourceMediaStyle(120, 180, 30, 0.8);

    expect(String(start.transform)).toContain('scale(');
    expect(String(later.transform)).toContain('translate3d(');
    expect(later.transform).not.toBe(start.transform);
  });
});
