import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {clamp, effectNumber, smoothstep} from './utils';

export type SpeedRampEffectProps = EffectComponentProps;

export const speedRampPlaybackRate = (
  frame: number,
  fps: number,
  effect: EffectComponentProps['effect'],
): number => {
  const start = Math.max(0, effectNumber(effect, 'start_seconds', 0) * fps);
  const end = Math.max(start + 1, effectNumber(effect, 'end_seconds', start / fps + 1) * fps);
  const minRate = clamp(effectNumber(effect, 'min_rate', 0.5), 0.35, 0.8);
  const edge = Math.max(1, Math.round(fps * 0.2));
  if (frame < start - edge || frame > end + edge) return 1;
  if (frame >= start && frame <= end) return minRate;
  if (frame < start) {
    const p = smoothstep((frame - (start - edge)) / edge);
    return 1 + (minRate - 1) * p;
  }
  const p = smoothstep((frame - end) / edge);
  return minRate + (1 - minRate) * p;
};

export const SpeedRampEffect = ({effect, children}: SpeedRampEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const rate = speedRampPlaybackRate(frame, fps, effect);
  const blur = Math.max(0, (1 - rate) * 1.8);
  return (
    <div
      data-playback-rate={rate.toFixed(3)}
      style={{filter: `blur(${blur.toFixed(2)}px)`, height: '100%', width: '100%'}}
    >
      {children}
    </div>
  );
};
