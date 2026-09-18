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
  const pop = spring({fps, frame, config: {damping: 18, mass: 0.72, stiffness: 118}});
  const clampedSpring = Math.max(0, Math.min(1, pop));
  const springEase = clampedSpring >= 0.999 ? 1 : clampedSpring <= 0.001 ? 0 : clampedSpring;
  switch (name) {
    case 'fade':
      return {opacity: ease};
    case 'push_left':
      return {
        opacity: springEase,
        transform: `translateX(${(1 - springEase) * 92}px) scale(${0.985 + springEase * 0.015})`,
      };
    case 'push_up':
      return {
        opacity: springEase,
        transform: `translateY(${(1 - springEase) * 74}px) scale(${0.97 + springEase * 0.03})`,
      };
    case 'slow_zoom': {
      const progress = Math.max(0, Math.min(1, frame / Math.max(1, fps * 8)));
      return {transform: `translateY(${-8 * progress}px) scale(${1 + progress * 0.055})`};
    }
    case 'punch_in': {
      const overshoot = Math.max(0, Math.min(1.06, pop));
      return {opacity: springEase, transform: `scale(${0.89 + overshoot * 0.11})`};
    }
    case 'parallax': {
      const progress = Math.max(0, Math.min(1, frame / Math.max(1, fps * 5)));
      return {transform: `translate3d(${-36 * progress}px,${-6 * progress}px,0) scale(${1 + progress * 0.018})`};
    }
    default:
      throw new Error(`Unknown motion: ${String(name)}`);
  }
};
