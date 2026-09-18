import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber} from './utils';

export type ParticleBurstEffectProps = EffectComponentProps;

export const ParticleBurstEffect = ({effect, children, theme}: ParticleBurstEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const at = effectNumber(effect, 'at_seconds', 0) * fps;
  const p = Math.min(1, Math.max(0, (frame - at) / Math.max(1, fps * 0.5)));
  const visible = p > 0 && p < 1;
  return (
    <>
      {children}
      {visible ? (
        <AbsoluteFill style={{pointerEvents: 'none', zIndex: 100}}>
          {Array.from({length: 24}).map((_, index) => {
            const angle = (index / 24) * Math.PI * 2;
            const radius = p * (80 + (index % 5) * 18);
            return (
              <div
                key={index}
                style={{
                  background: index % 2 === 0 ? theme.accent : theme.secondary,
                  borderRadius: index % 3 === 0 ? 2 : 99,
                  height: 5 + (index % 4) * 2,
                  left: '50%',
                  opacity: 1 - p,
                  position: 'absolute',
                  top: '48%',
                  transform: `translate(${Math.cos(angle) * radius}px,${Math.sin(angle) * radius}px) rotate(${index * 17}deg)`,
                  width: 5 + (index % 3) * 3,
                }}
              />
            );
          })}
        </AbsoluteFill>
      ) : null}
    </>
  );
};
