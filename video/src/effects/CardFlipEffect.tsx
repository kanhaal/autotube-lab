import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {smoothstep} from './utils';

export type CardFlipEffectProps = EffectComponentProps;

export const CardFlipEffect = ({children}: CardFlipEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = smoothstep(frame / Math.max(1, fps * 0.48));
  return (
    <div
      style={{
        height: '100%',
        perspective: 1500,
        transform: `rotateY(${(1 - p) * -14}deg) rotateX(${(1 - p) * 6}deg) scale(${0.94 + p * 0.06})`,
        transformOrigin: 'center center',
        width: '100%',
      }}
    >
      {children}
    </div>
  );
};
