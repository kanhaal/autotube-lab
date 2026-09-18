import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';

export type WaveformOverlayEffectProps = EffectComponentProps;

export const WaveformOverlayEffect = ({children, theme}: WaveformOverlayEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const bars = 36;
  return (
    <>
      {children}
      <div style={{alignItems: 'center', bottom: 76, display: 'flex', gap: 4, height: 42, left: 72, opacity: 0.7, position: 'absolute', zIndex: 67}}>
        {Array.from({length: bars}).map((_, index) => {
          const wave = 0.35 + 0.65 * Math.abs(Math.sin(index * 0.72 + (frame / fps) * 6.2));
          return (
            <div
              key={index}
              style={{
                background: index % 3 === 0 ? theme.accent : theme.secondary,
                borderRadius: 99,
                height: `${7 + wave * 30}px`,
                width: 3,
              }}
            />
          );
        })}
      </div>
    </>
  );
};
