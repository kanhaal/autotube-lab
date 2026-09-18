import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber} from './utils';

export type DuotoneFlashEffectProps = EffectComponentProps;

export const DuotoneFlashEffect = ({effect, children, theme}: DuotoneFlashEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const at = effectNumber(effect, 'at_seconds', 0) * fps;
  const pulse = Math.max(0, 1 - Math.abs(frame - at) / Math.max(1, fps * 0.16));
  return (
    <div
      style={{
        filter: pulse > 0 ? `saturate(${1 + pulse * 1.5}) contrast(${1 + pulse * 0.25}) drop-shadow(0 0 ${pulse * 26}px ${theme.accent})` : 'none',
        height: '100%',
        width: '100%',
      }}
    >
      {children}
    </div>
  );
};
