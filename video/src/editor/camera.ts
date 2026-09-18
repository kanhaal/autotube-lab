import type {CSSProperties} from 'react';

import type {CameraPreset} from '../types';

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));

const smoothstep = (value: number) => {
  const x = clamp01(value);
  return x * x * (3 - 2 * x);
};

const cameraProgress = (frame: number, durationInFrames: number) =>
  smoothstep(frame / Math.max(1, durationInFrames - 1));

export const microBeatEnvelope = (
  frame: number,
  fps: number,
  atSeconds: number,
  widthSeconds = 0.24,
): number => {
  const center = atSeconds * Math.max(1, fps);
  const halfWidth = Math.max(1, widthSeconds * Math.max(1, fps));
  const distance = Math.abs(frame - center) / halfWidth;
  if (distance >= 1) return 0;
  const local = 1 - distance;
  return Math.sin(local * Math.PI * 0.5);
};

export const cameraRigStyle = (
  preset: CameraPreset,
  frame: number,
  durationInFrames: number,
  fps: number,
  intensity = 1,
  target: {x?: number; y?: number} = {},
): CSSProperties => {
  const p = cameraProgress(frame, durationInFrames);
  const safeIntensity = Math.max(0, Math.min(1.8, intensity));
  const targetX = Math.max(0, Math.min(1, Number(target.x ?? 0.5)));
  const targetY = Math.max(0, Math.min(1, Number(target.y ?? 0.5)));
  const centerShiftX = (0.5 - targetX) * 80 * p * safeIntensity;
  const centerShiftY = (0.5 - targetY) * 56 * p * safeIntensity;
  let x = centerShiftX;
  let y = centerShiftY;
  let scale = 1;
  let rotateX = 0;
  let rotateY = 0;
  let rotateZ = 0;

  switch (preset) {
    case 'dolly_in':
      scale = 1 + 0.085 * p * safeIntensity;
      y -= 6 * p * safeIntensity;
      break;
    case 'dolly_out':
      scale = 1.07 - 0.07 * p * safeIntensity;
      break;
    case 'orbit_left':
      x += 32 * (p - 0.5) * safeIntensity;
      rotateY = -3.8 * (p - 0.5) * safeIntensity;
      rotateX = 0.7 * (0.5 - p) * safeIntensity;
      scale = 1.025 + 0.02 * p;
      break;
    case 'orbit_right':
      x -= 32 * (p - 0.5) * safeIntensity;
      rotateY = 3.8 * (p - 0.5) * safeIntensity;
      rotateX = 0.7 * (0.5 - p) * safeIntensity;
      scale = 1.025 + 0.02 * p;
      break;
    case 'whip_pan': {
      const entryFrames = Math.max(2, Math.round(fps * 0.26));
      const entry = smoothstep(frame / entryFrames);
      x += (1 - entry) * -220 * safeIntensity;
      rotateZ = (1 - entry) * -2.2 * safeIntensity;
      scale = 1.03 + (1 - entry) * 0.035;
      break;
    }
    case 'handheld_micro': {
      const seconds = frame / Math.max(1, fps);
      x += Math.sin(seconds * 7.3) * 3.6 * safeIntensity;
      y += Math.cos(seconds * 5.7) * 2.4 * safeIntensity;
      rotateZ = Math.sin(seconds * 4.1) * 0.16 * safeIntensity;
      scale = 1.018;
      break;
    }
    case 'rack_push':
      scale = 1 + 0.065 * p * safeIntensity;
      y -= 10 * p * safeIntensity;
      rotateY = 1.2 * (p - 0.5) * safeIntensity;
      break;
    case 'crane_down':
      y += (1 - p) * -46 * safeIntensity;
      scale = 1.045 - p * 0.02;
      rotateX = (0.5 - p) * 1.5 * safeIntensity;
      break;
    case 'locked':
    default:
      break;
  }

  return {
    transform:
      'perspective(1500px) translate3d(' +
      x.toFixed(3) +
      'px,' +
      y.toFixed(3) +
      'px,0) scale(' +
      scale.toFixed(5) +
      ') rotateX(' +
      rotateX.toFixed(3) +
      'deg) rotateY(' +
      rotateY.toFixed(3) +
      'deg) rotateZ(' +
      rotateZ.toFixed(3) +
      'deg)',
    transformOrigin: (targetX * 100).toFixed(2) + '% ' + (targetY * 100).toFixed(2) + '%',
    willChange: 'transform',
  };
};
