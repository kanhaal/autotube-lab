import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber, smoothstep} from './utils';

export type UnderlineSweepEffectProps = EffectComponentProps;

export const UnderlineSweepEffect = ({effect, children, theme}: UnderlineSweepEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const start = effectNumber(effect, 'start_seconds', 0) * fps;
  const p = smoothstep((frame - start) / Math.max(1, fps * 0.35));
  return (
    <>
      {children}
      <div
        style={{
          background: `linear-gradient(90deg, ${theme.accent}, ${theme.secondary})`,
          borderRadius: 999,
          boxShadow: `0 0 18px ${theme.accent}55`,
          height: 5,
          left: `${effectNumber(effect, 'x_percent', 12)}%`,
          position: 'absolute',
          top: `${effectNumber(effect, 'y_percent', 65)}%`,
          width: `${effectNumber(effect, 'width_percent', 34) * p}%`,
          zIndex: 76,
        }}
      />
    </>
  );
};
