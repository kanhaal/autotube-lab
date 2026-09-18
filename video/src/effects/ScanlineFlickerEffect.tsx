import {AbsoluteFill, useCurrentFrame} from 'remotion';

import type {EffectComponentProps} from './types';

export type ScanlineFlickerEffectProps = EffectComponentProps;

export const ScanlineFlickerEffect = ({children}: ScanlineFlickerEffectProps) => {
  const frame = useCurrentFrame();
  const opacity = frame % 7 === 0 ? 0.16 : 0.07;
  return (
    <>
      {children}
      <AbsoluteFill
        style={{
          backgroundImage: 'repeating-linear-gradient(180deg, transparent 0 3px, rgba(255,255,255,.28) 4px)',
          mixBlendMode: 'overlay',
          opacity,
          pointerEvents: 'none',
          zIndex: 88,
        }}
      />
    </>
  );
};
