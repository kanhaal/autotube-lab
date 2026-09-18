import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {clamp, effectBox, effectNumber, frameProgress, smoothstep} from './utils';

export type AutoZoomEffectProps = EffectComponentProps;

export const AutoZoomEffect = ({effect, children}: AutoZoomEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const target = effectBox(effect);
  const scale = clamp(effectNumber(effect, 'scale', 1.18), 1.1, 1.3);
  const start = Math.max(0, effectNumber(effect, 'start_seconds', 0));
  const duration = Math.max(0.18, effectNumber(effect, 'duration_seconds', 0.55));
  const hold = Math.max(0, effectNumber(effect, 'hold_seconds', 0.5));
  const enter = smoothstep(frameProgress(frame, fps, start, duration));
  const exitStart = start + duration + hold;
  const exit = 1 - smoothstep(frameProgress(frame, fps, exitStart, duration));
  const amount = Math.min(enter, exit);
  const applied = 1 + (scale - 1) * amount;
  const originX = (target.x + target.width / 2) * 100;
  const originY = (target.y + target.height / 2) * 100;

  return (
    <div
      style={{
        height: '100%',
        transform: `scale(${applied.toFixed(4)})`,
        transformOrigin: `${originX.toFixed(2)}% ${originY.toFixed(2)}%`,
        width: '100%',
      }}
    >
      {children}
    </div>
  );
};
