import type {CSSProperties} from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';

import type {ChannelTheme} from './themes/types';

export type VfxFamily = 'precision' | 'snap';

export type PremiumVfxProfile = {
  cameraIntensity: number;
  glowOpacity: number;
  gridOpacity: number;
  grainOpacity: number;
  streakOpacity: number;
  transitionBoost: number;
};

export type TransitionAccentState = {
  primary: number;
  secondary: number;
  offsetPx: number;
  scale: number;
};

const clamp01 = (value: number): number => Math.max(0, Math.min(1, value));

const smoothstep = (value: number): number => {
  const x = clamp01(value);
  return x * x * (3 - 2 * x);
};

export const premiumVfxProfile = (
  family: VfxFamily,
  motionIntensity: number,
): PremiumVfxProfile => {
  const intensity = Math.max(0.35, Math.min(1.6, motionIntensity));
  if (family === 'snap') {
    return {
      cameraIntensity: intensity * 1.04,
      glowOpacity: 0.28,
      gridOpacity: 0.055,
      grainOpacity: 0.032,
      streakOpacity: 0.22 * intensity,
      transitionBoost: 1.16 * intensity,
    };
  }
  return {
    cameraIntensity: intensity * 0.82,
    glowOpacity: 0.2,
    gridOpacity: 0.075,
    grainOpacity: 0.024,
    streakOpacity: 0.07 * intensity,
    transitionBoost: 0.78 * intensity,
  };
};

export const cinematicCameraStyle = (
  frame: number,
  durationFrames: number,
  fps: number,
  family: VfxFamily,
  intensity: number,
): CSSProperties => {
  const duration = Math.max(2, durationFrames);
  const progress = clamp01(frame / (duration - 1));
  const eased = smoothstep(progress);
  const profile = premiumVfxProfile(family, intensity);
  const direction = family === 'snap' ? -1 : 1;
  const drift = Math.sin(progress * Math.PI) * 12 * profile.cameraIntensity;
  const translateX = direction * ((eased - 0.5) * 18 + drift);
  const translateY = (0.5 - eased) * 10 * profile.cameraIntensity;
  const scale = 1.01 + eased * 0.024 * profile.cameraIntensity;
  const rotateX = (0.5 - eased) * 0.24 * profile.cameraIntensity;
  const rotateY = direction * (eased - 0.5) * 0.58 * profile.cameraIntensity;
  const perspective = Math.max(1200, Math.round(fps * 52));

  return {
    transform:
      `perspective(${perspective}px) translate3d(${translateX.toFixed(3)}px, ${translateY.toFixed(3)}px, 0) ` +
      `scale(${scale.toFixed(5)}) rotateX(${rotateX.toFixed(3)}deg) rotateY(${rotateY.toFixed(3)}deg)`,
    transformOrigin: 'center center',
  };
};

export const headlineWordProgress = (
  frame: number,
  fps: number,
  order: number,
): number => {
  const delay = Math.round(Math.max(0, order) * fps * 0.075);
  const duration = Math.max(1, Math.round(fps * 0.34));
  return smoothstep((frame - delay) / duration);
};



export const editorialItemStyle = (
  frame: number,
  fps: number,
  order: number,
  family: VfxFamily,
): CSSProperties => {
  const progress = headlineWordProgress(frame, fps, order + 1);
  const direction = family === 'snap' ? (order % 2 === 0 ? 1 : -1) : 1;
  const x = (1 - progress) * 34 * direction;
  const y = (1 - progress) * 24;
  const scale = 0.955 + progress * 0.045;
  const rotate = family === 'snap' ? (1 - progress) * 1.8 * direction : (1 - progress) * 0.55;

  return {
    filter: `blur(${((1 - progress) * 5).toFixed(2)}px)`,
    opacity: progress,
    transform:
      `translate3d(${x.toFixed(2)}px,${y.toFixed(2)}px,0) ` +
      `scale(${scale.toFixed(4)}) rotateZ(${rotate.toFixed(3)}deg)`,
    transformOrigin: 'center center',
  };
};

export const transitionAccentState = (
  frame: number,
  fps: number,
  family: VfxFamily,
  intensity: number,
): TransitionAccentState => {
  const profile = premiumVfxProfile(family, intensity);
  const duration = Math.max(1, Math.round(fps * (family === 'snap' ? 0.34 : 0.46)));
  const progress = clamp01(frame / duration);
  const inverse = 1 - smoothstep(progress);
  const secondaryWave = Math.sin(clamp01(frame / Math.max(1, duration * 0.78)) * Math.PI);
  return {
    primary: clamp01(inverse * profile.transitionBoost),
    secondary: clamp01(secondaryWave * 0.68 * profile.transitionBoost),
    offsetPx: (1 - progress) * (family === 'snap' ? 180 : 112) * (family === 'snap' ? -1 : 1),
    scale: 0.96 + smoothstep(progress) * 0.04,
  };
};

export const sourceMediaStyle = (
  frame: number,
  durationFrames: number,
  fps: number,
  intensity: number,
): CSSProperties => {
  const duration = Math.max(2, durationFrames);
  const progress = clamp01(frame / (duration - 1));
  const eased = smoothstep(progress);
  const pulse = Math.sin(progress * Math.PI * 1.15);
  const translateX = (eased - 0.5) * -18 * intensity;
  const translateY = (0.5 - eased) * 12 * intensity;
  const scale = 1.025 + eased * 0.035 * intensity + pulse * 0.006;
  const contrast = 1.02 + pulse * 0.025;
  const saturation = 1.01 + pulse * 0.035;

  return {
    filter: `contrast(${contrast.toFixed(3)}) saturate(${saturation.toFixed(3)})`,
    transform:
      `translate3d(${translateX.toFixed(3)}px, ${translateY.toFixed(3)}px, 0) ` +
      `scale(${scale.toFixed(5)})`,
    transformOrigin: 'center top',
    willChange: 'transform, filter',
  };
};

export const PremiumVfxBackdrop = ({
  theme,
  format = 'long',
}: {
  theme: ChannelTheme;
  format?: 'long' | 'short';
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const profile = premiumVfxProfile(theme.transitionFamily, theme.motionIntensity);
  const seconds = frame / Math.max(1, fps);
  const gridShift = (seconds * (theme.transitionFamily === 'snap' ? 7.5 : 3.2)) % 64;
  const orbit = seconds * (theme.transitionFamily === 'snap' ? 0.55 : 0.28);
  const glowX = 72 + Math.sin(orbit) * (format === 'short' ? 13 : 8);
  const glowY = 18 + Math.cos(orbit * 0.82) * (format === 'short' ? 8 : 5);
  const streakShift = ((seconds * 240) % 2200) - 900;

  return (
    <AbsoluteFill style={{overflow: 'hidden', pointerEvents: 'none'}}>
      <div
        style={{
          background:
            `linear-gradient(rgba(255,255,255,${profile.gridOpacity}) 1px, transparent 1px), ` +
            `linear-gradient(90deg, rgba(255,255,255,${profile.gridOpacity}) 1px, transparent 1px)`,
          backgroundSize: format === 'short' ? '54px 54px' : '64px 64px',
          inset: -96,
          opacity: theme.transitionFamily === 'precision' ? 0.5 : 0.22,
          position: 'absolute',
          transform: `translate3d(${gridShift}px, ${gridShift * 0.6}px, 0) rotate(-1.2deg)`,
        }}
      />
      <div
        style={{
          background: theme.secondary,
          borderRadius: '50%',
          filter: format === 'short' ? 'blur(115px)' : 'blur(145px)',
          height: format === 'short' ? 540 : 620,
          left: `${glowX}%`,
          opacity: profile.glowOpacity,
          position: 'absolute',
          top: `${glowY}%`,
          transform: 'translate(-50%,-50%)',
          width: format === 'short' ? 540 : 620,
        }}
      />
      <div
        style={{
          background: theme.accent,
          borderRadius: '50%',
          bottom: format === 'short' ? '8%' : '-18%',
          filter: format === 'short' ? 'blur(130px)' : 'blur(165px)',
          height: format === 'short' ? 450 : 560,
          left: format === 'short' ? '-18%' : '4%',
          opacity: profile.glowOpacity * 0.72,
          position: 'absolute',
          width: format === 'short' ? 450 : 560,
        }}
      />
      <div
        style={{
          background:
            `linear-gradient(115deg, transparent 0 44%, ${theme.accent} 49%, transparent 54%), ` +
            `linear-gradient(115deg, transparent 0 51%, ${theme.secondary} 54%, transparent 58%)`,
          filter: 'blur(2px)',
          inset: '-18%',
          opacity: profile.streakOpacity,
          position: 'absolute',
          transform: `translate3d(${streakShift}px,0,0)`,
        }}
      />
      <div
        style={{
          backgroundImage:
            'repeating-radial-gradient(circle at 17% 31%, rgba(255,255,255,.8) 0 0.45px, transparent 0.65px 3px)',
          backgroundSize: '7px 7px',
          inset: 0,
          mixBlendMode: 'soft-light',
          opacity: profile.grainOpacity,
          position: 'absolute',
          transform: `translate3d(${frame % 7}px,${(frame * 3) % 7}px,0)`,
        }}
      />
      <div
        style={{
          background: 'radial-gradient(circle at center, transparent 48%, rgba(0,0,0,.18) 76%, rgba(0,0,0,.52) 118%)',
          inset: 0,
          position: 'absolute',
        }}
      />
    </AbsoluteFill>
  );
};

export const TransitionAccent = ({
  theme,
  durationInFrames,
}: {
  theme: ChannelTheme;
  durationInFrames: number;
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const edgeFrame = Math.min(frame, Math.max(0, durationInFrames - 1 - frame));
  const state = transitionAccentState(
    edgeFrame,
    fps,
    theme.transitionFamily,
    theme.motionIntensity,
  );
  if (state.primary < 0.005 && state.secondary < 0.005) return null;

  const angle = theme.transitionFamily === 'snap' ? -11 : -5;
  return (
    <AbsoluteFill style={{overflow: 'hidden', pointerEvents: 'none'}}>
      <div
        style={{
          background: theme.accent,
          boxShadow: `0 0 48px ${theme.accent}66`,
          height: '180%',
          left: theme.transitionFamily === 'snap' ? '18%' : '42%',
          opacity: state.primary * 0.24,
          position: 'absolute',
          top: '-40%',
          transform: `translateX(${state.offsetPx}px) rotate(${angle}deg) scaleX(${0.45 + state.scale * 0.55})`,
          width: theme.transitionFamily === 'snap' ? 26 : 14,
        }}
      />
      <div
        style={{
          background: `linear-gradient(90deg, transparent, ${theme.secondary}, transparent)`,
          filter: 'blur(3px)',
          height: 5,
          left: '-20%',
          opacity: state.secondary * 0.46,
          position: 'absolute',
          top: theme.transitionFamily === 'snap' ? '38%' : '26%',
          transform: `translateX(${state.offsetPx * -2.2}px) rotate(${angle * 0.4}deg)`,
          width: '140%',
        }}
      />
    </AbsoluteFill>
  );
};
