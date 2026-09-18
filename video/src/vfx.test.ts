import {describe, expect, it} from 'vitest';

import {
  cinematicCameraStyle,
  editorialFocusWeight,
  editorialItemStyle,
  editorialLineProgress,
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
