import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';

export type LightLeakEffectProps = EffectComponentProps;

export const LightLeakEffect = ({children, theme}: LightLeakEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const x = ((frame / fps) * 32) % 140 - 20;
  return (
    <>
      {children}
      <AbsoluteFill
        style={{
          background: `linear-gradient(115deg, transparent 0 32%, ${theme.accent}00 38%, ${theme.accent}28 46%, rgba(255,255,255,.18) 50%, ${theme.secondary}18 55%, transparent 64%)`,
          mixBlendMode: 'screen',
          opacity: 0.7,
          pointerEvents: 'none',
          transform: `translateX(${x}%)`,
          zIndex: 84,
        }}
      />
    </>
  );
};
