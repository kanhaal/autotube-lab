import {AbsoluteFill, useCurrentFrame} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber} from './utils';

export type FilmGrainEffectProps = EffectComponentProps;

export const FilmGrainEffect = ({effect, children}: FilmGrainEffectProps) => {
  const frame = useCurrentFrame();
  const opacity = Math.min(0.14, Math.max(0.015, effectNumber(effect, 'opacity', 0.045)));
  const offset = frame % 4;
  return (
    <>
      {children}
      <AbsoluteFill
        style={{
          backgroundImage:
            'radial-gradient(circle at 20% 30%, rgba(255,255,255,.9) 0 .7px, transparent .8px), radial-gradient(circle at 70% 60%, rgba(255,255,255,.7) 0 .55px, transparent .65px)',
          backgroundSize: `${8 + offset}px ${9 + offset}px, ${11 + offset}px ${10 + offset}px`,
          mixBlendMode: 'soft-light',
          opacity,
          pointerEvents: 'none',
          zIndex: 90,
        }}
      />
    </>
  );
};
