import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber} from './utils';

export type VignettePulseEffectProps = EffectComponentProps;

export const VignettePulseEffect = ({effect, children}: VignettePulseEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const at = effectNumber(effect, 'at_seconds', 0) * fps;
  const pulse = Math.max(0, 1 - Math.abs(frame - at) / Math.max(1, fps * 0.22));
  return (
    <>
      {children}
      <AbsoluteFill
        style={{
          boxShadow: `inset 0 0 ${Math.round(160 + pulse * 170)}px rgba(0,0,0,${(0.25 + pulse * 0.34).toFixed(3)})`,
          pointerEvents: 'none',
          zIndex: 83,
        }}
      />
    </>
  );
};
