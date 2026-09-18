import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectBox, effectNumber, frameProgress, smoothstep} from './utils';

export type SpotlightDimEffectProps = EffectComponentProps;

export const SpotlightDimEffect = ({effect, children}: SpotlightDimEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const target = effectBox(effect);
  const dim = Math.min(0.86, Math.max(0.15, effectNumber(effect, 'dim', 0.68)));
  const progress = smoothstep(
    frameProgress(
      frame,
      fps,
      Math.max(0, effectNumber(effect, 'start_seconds', 0)),
      Math.max(0.12, effectNumber(effect, 'fade_seconds', 0.22)),
    ),
  );

  return (
    <>
      {children}
      <AbsoluteFill style={{pointerEvents: 'none'}}>
        <div
          style={{
            border: '1px solid rgba(255,255,255,0.18)',
            borderRadius: effectNumber(effect, 'radius', 18),
            boxShadow: `0 0 0 2200px rgba(0,0,0,${(dim * progress).toFixed(3)}), 0 0 48px rgba(255,255,255,0.06)`,
            height: `${target.height * 100}%`,
            left: `${target.x * 100}%`,
            position: 'absolute',
            top: `${target.y * 100}%`,
            width: `${target.width * 100}%`,
          }}
        />
      </AbsoluteFill>
    </>
  );
};
