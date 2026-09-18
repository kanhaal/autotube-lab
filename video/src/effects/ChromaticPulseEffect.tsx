import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber} from './utils';

export type ChromaticPulseEffectProps = EffectComponentProps;

export const ChromaticPulseEffect = ({effect, children}: ChromaticPulseEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const at = Math.max(0, effectNumber(effect, 'at_seconds', 0) * fps);
  const distance = Math.abs(frame - at);
  const pulse = Math.max(0, 1 - distance / Math.max(1, fps * 0.12));
  const px = pulse * Math.min(8, Math.max(1, effectNumber(effect, 'pixels', 4)));
  return (
    <div
      style={{
        filter: pulse > 0 ? `drop-shadow(${px}px 0 rgba(255,0,92,.42)) drop-shadow(-${px}px 0 rgba(0,220,255,.38))` : 'none',
        height: '100%',
        width: '100%',
      }}
    >
      {children}
    </div>
  );
};
