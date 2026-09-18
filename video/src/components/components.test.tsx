import {describe, expect, it} from 'vitest';

import {SAFE_MARGIN_X, SAFE_MARGIN_Y} from './SafeFrame';
import {wrapText} from './Typography';
import {activeCaptionAt} from './CaptionTrack';
import {motionStyle, transitionPreset} from '../motion';

const cues = [
  {start: 0, end: 1.2, text: 'First phrase', words: ['First', 'phrase']},
  {start: 1.2, end: 2.5, text: 'Second phrase', words: ['Second', 'phrase']},
];

describe('professional visual primitives', () => {
  it('keeps long-form content inside conservative title-safe margins', () => {
    expect(SAFE_MARGIN_X).toBeGreaterThanOrEqual(96);
    expect(SAFE_MARGIN_Y).toBeGreaterThanOrEqual(64);
  });

  it('wraps headline text deterministically by character budget', () => {
    expect(wrapText('The new local AI release changes developer workflows', 18)).toEqual([
      'The new local AI',
      'release changes',
      'developer',
      'workflows',
    ]);
  });

  it('maps only registered transition names to deterministic presets', () => {
    expect(transitionPreset('cut').kind).toBe('cut');
    expect(transitionPreset('crossfade').durationFrames).toBeGreaterThan(0);
    expect(() => transitionPreset('spin' as never)).toThrow(/transition/i);
  });

  it('uses dimensional motion rather than flat linear pushes', () => {
    expect(String(motionStyle('push_up', 4, 30).transform)).toContain('scale(');
    const zoom = String(motionStyle('slow_zoom', 300, 30).transform);
    expect(zoom).toMatch(/scale\(1\.0[4-9]/);
  });

  it('selects captions using half-open timing ranges', () => {
    expect(activeCaptionAt(cues, 0.4)?.text).toBe('First phrase');
    expect(activeCaptionAt(cues, 1.2)?.text).toBe('Second phrase');
    expect(activeCaptionAt(cues, 2.5)).toBeUndefined();
  });
});
