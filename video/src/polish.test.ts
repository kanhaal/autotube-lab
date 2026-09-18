import {describe, expect, it} from 'vitest';

import {
  activeWordIndex,
  layoutForScene,
  sceneEnvelope,
  staggerProgress,
} from './polish';
import type {CaptionCueV1} from './types';

const cue: CaptionCueV1 = {
  start: 1,
  end: 3,
  text: 'A much cleaner caption',
  words: ['A', 'much', 'cleaner', 'caption'],
  word_timings: [
    {text: 'A', start: 1, end: 1.2},
    {text: 'much', start: 1.2, end: 1.7},
    {text: 'cleaner', start: 1.7, end: 2.3},
    {text: 'caption', start: 2.3, end: 3},
  ],
};

describe('production visual polish helpers', () => {
  it('tracks the currently spoken word from aligned word timings', () => {
    expect(activeWordIndex(cue, 0.9)).toBe(-1);
    expect(activeWordIndex(cue, 1.05)).toBe(0);
    expect(activeWordIndex(cue, 1.45)).toBe(1);
    expect(activeWordIndex(cue, 2.05)).toBe(2);
    expect(activeWordIndex(cue, 2.8)).toBe(3);
    expect(activeWordIndex(cue, 3)).toBe(-1);
  });

  it('creates a scene envelope that eases in and out instead of only entering', () => {
    expect(sceneEnvelope(0, 120, 10)).toBe(0);
    expect(sceneEnvelope(10, 120, 10)).toBeCloseTo(1, 4);
    expect(sceneEnvelope(60, 120, 10)).toBeCloseTo(1, 4);
    expect(sceneEnvelope(119, 120, 10)).toBeLessThan(0.2);
  });

  it('stagger-reveals internal scene elements deterministically', () => {
    expect(staggerProgress(0, 30, 0)).toBe(0);
    expect(staggerProgress(6, 30, 0)).toBeGreaterThan(0);
    expect(staggerProgress(6, 30, 2)).toBe(0);
    expect(staggerProgress(30, 30, 2)).toBeCloseTo(1, 3);
  });

  it('uses denser layouts for source and data scenes', () => {
    expect(layoutForScene('source_browser', 'long')).toBe('source');
    expect(layoutForScene('chart', 'long')).toBe('data');
    expect(layoutForScene('comparison', 'short')).toBe('data');
    expect(layoutForScene('headline', 'short')).toBe('hero');
  });
});
