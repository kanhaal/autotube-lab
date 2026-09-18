import {interpolate} from 'remotion';

import type {CaptionCueV1} from './types';

export type EditorialLayout = 'hero' | 'source' | 'data' | 'story';

const clamp01 = (value: number): number => Math.max(0, Math.min(1, value));

const smoothstep = (value: number): number => {
  const x = clamp01(value);
  return x * x * (3 - 2 * x);
};

export const activeWordIndex = (cue: CaptionCueV1, seconds: number): number => {
  if (seconds < cue.start || seconds >= cue.end) return -1;
  if (cue.word_timings?.length) {
    const exact = cue.word_timings.findIndex(
      (word) => seconds >= word.start && seconds < word.end,
    );
    if (exact >= 0) return exact;
  }

  const words = cue.words.length
    ? cue.words
    : cue.text.trim().split(/\s+/).filter(Boolean);
  if (!words.length || cue.end <= cue.start) return -1;
  const progress = clamp01((seconds - cue.start) / (cue.end - cue.start));
  return Math.min(words.length - 1, Math.floor(progress * words.length));
};

export const sceneEnvelope = (
  frame: number,
  durationFrames: number,
  transitionFrames = 10,
): number => {
  if (durationFrames <= 1) return 1;
  const transition = Math.max(1, Math.min(transitionFrames, Math.floor(durationFrames / 3)));
  const enter = smoothstep(frame / transition);
  const exitStart = durationFrames - transition;
  const leave = frame < exitStart ? 1 : smoothstep((durationFrames - 1 - frame) / transition);
  return clamp01(Math.min(enter, leave));
};

export const staggerProgress = (
  frame: number,
  fps: number,
  order: number,
): number => {
  const delayFrames = Math.max(0, Math.round(order * fps * 0.12));
  const duration = Math.max(1, Math.round(fps * 0.42));
  return interpolate(frame - delayFrames, [0, duration], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: (value) => smoothstep(value),
  });
};

export const layoutForScene = (
  sceneType: string,
  format: 'long' | 'short',
): EditorialLayout => {
  if (['source_browser', 'device', 'github', 'game_store'].includes(sceneType)) {
    return 'source';
  }
  if (['stat', 'chart', 'timeline', 'before_after', 'comparison', 'list', 'process'].includes(sceneType)) {
    return 'data';
  }
  if (['hook', 'headline', 'chapter', 'conclusion', 'fallback_editorial'].includes(sceneType)) {
    return 'hero';
  }
  return format === 'short' ? 'hero' : 'story';
};


export type OverlappedSceneWindow = {
  from: number;
  durationInFrames: number;
  preRoll: number;
  postRoll: number;
};

export const overlappedSceneWindow = (
  window: {from: number; durationInFrames: number},
  index: number,
  count: number,
  overlapFrames = 8,
): OverlappedSceneWindow => {
  const half = Math.max(0, Math.floor(overlapFrames / 2));
  const preRoll = index > 0 ? half : 0;
  const postRoll = index < count - 1 ? half : 0;
  return {
    from: Math.max(0, window.from - preRoll),
    durationInFrames: window.durationInFrames + preRoll + postRoll,
    preRoll,
    postRoll,
  };
};
