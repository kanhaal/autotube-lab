import type {CSSProperties} from 'react';
import {interpolate, spring} from 'remotion';

export type TransitionName = 'cut' | 'crossfade' | 'wipe' | 'slide' | 'stinger';
export type MotionName = 'none' | 'fade' | 'push_left' | 'push_up' | 'slow_zoom' | 'punch_in' | 'parallax';

const TRANSITIONS: Record<TransitionName, {kind: TransitionName; durationFrames: number}> = {
  cut: {kind: 'cut', durationFrames: 0},
  crossfade: {kind: 'crossfade', durationFrames: 10},
  wipe: {kind: 'wipe', durationFrames: 12},
  slide: {kind: 'slide', durationFrames: 10},
  stinger: {kind: 'stinger', durationFrames: 8},
};

export const transitionPreset = (name: TransitionName) => {
  const preset = TRANSITIONS[name];
  if (!preset) throw new Error(`Unknown transition: ${String(name)}`);
  return preset;
};

export const motionStyle = (name: MotionName, frame: number, fps: number): CSSProperties => {
  if (name === 'none') return {};
  const ease = interpolate(frame, [0, Math.max(1, Math.round(fps * 0.4))], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const pop = spring({fps, frame, config: {damping: 16, mass: 0.8, stiffness: 120}});
  switch (name) {
    case 'fade':
      return {opacity: ease};
    case 'push_left':
      return {opacity: ease, transform: `translateX(${(1 - ease) * 70}px)`};
    case 'push_up':
      return {opacity: ease, transform: `translateY(${(1 - ease) * 60}px)`};
    case 'slow_zoom':
      return {transform: `scale(${1 + Math.min(frame / Math.max(1, fps * 10), 1) * 0.035})`};
    case 'punch_in':
      return {opacity: Math.min(1, pop), transform: `scale(${0.91 + Math.min(1, pop) * 0.09})`};
    case 'parallax':
      return {transform: `translate3d(${Math.min(frame, fps * 4) * -0.18}px,0,0)`};
    default:
      throw new Error(`Unknown motion: ${String(name)}`);
  }
};
