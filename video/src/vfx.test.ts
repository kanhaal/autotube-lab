import {describe, expect, it} from 'vitest';

import {
  cinematicCameraStyle,
  editorialItemStyle,
  headlineWordProgress,
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
