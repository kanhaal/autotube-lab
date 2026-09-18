import {describe, expect, it} from 'vitest';

import {cameraRigStyle, microBeatEnvelope} from './camera';
import {resolveShotStyle} from './shotDirector';
import type {SceneSpecV1} from '../types';

const scene = (scene_type: string, shot_style?: SceneSpecV1['shot_style']): SceneSpecV1 => ({
  id: 's1',
  narration: 'A verified source explains the change.',
  purpose: 'evidence',
  scene_type,
  headline: 'Verified change',
  subheadline: '',
  source_ids: [],
  asset_ids: [],
  motion: 'none',
  emphasis: [],
  transition: 'cut',
  fallback_scene_type: 'fallback_editorial',
  data: {},
  shot_style,
});

describe('V4 shot director', () => {
  it('uses explicit editorial shot direction when present', () => {
    expect(resolveShotStyle(scene('stat', 'source_detail'))).toBe('source_detail');
  });

  it('defaults source scenes to full-bleed media instead of cards', () => {
    expect(resolveShotStyle(scene('source_browser'))).toBe('source_full');
    expect(resolveShotStyle(scene('github'))).toBe('source_full');
    expect(resolveShotStyle(scene('game_store'))).toBe('source_full');
  });

  it('uses different visual grammar for text, data and comparisons', () => {
    expect(resolveShotStyle(scene('hook'))).toBe('kinetic_text');
    expect(resolveShotStyle(scene('chart'))).toBe('data_full');
    expect(resolveShotStyle(scene('comparison'))).toBe('split_screen');
    expect(resolveShotStyle(scene('code'))).toBe('graphic_3d');
  });
});

describe('V4 camera rig', () => {
  it('creates purposeful 3D camera transforms', () => {
    const dolly = cameraRigStyle('dolly_in', 30, 120, 30, 0.9);
    const orbit = cameraRigStyle('orbit_left', 30, 120, 30, 0.9);
    expect(String(dolly.transform)).toContain('perspective(');
    expect(String(dolly.transform)).toContain('translate3d(');
    expect(dolly.transform).not.toEqual(orbit.transform);
  });

  it('micro-beat impulse is local to the requested edit point', () => {
    expect(microBeatEnvelope(0, 30, 1)).toBe(0);
    expect(microBeatEnvelope(30, 30, 1)).toBeGreaterThan(0.8);
    expect(microBeatEnvelope(75, 30, 1)).toBe(0);
  });
});
