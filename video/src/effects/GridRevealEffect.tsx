import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {smoothstep} from './utils';

export type GridRevealEffectProps = EffectComponentProps;

export const GridRevealEffect = ({children, theme}: GridRevealEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cols = 6;
  const rows = 4;

  return (
    <>
      {children}
      <AbsoluteFill style={{display: 'grid', gridTemplateColumns: `repeat(${cols}, 1fr)`, gridTemplateRows: `repeat(${rows}, 1fr)`, pointerEvents: 'none', zIndex: 110}}>
        {Array.from({length: cols * rows}).map((_, index) => {
          const p = smoothstep((frame - index * 1.4) / Math.max(1, fps * 0.24));
          return (
            <div
              key={index}
              style={{
                background: index % 2 === 0 ? theme.background : '#000',
                opacity: 1 - p,
                transform: `scale(${1 - p * 0.18})`,
              }}
            />
          );
        })}
      </AbsoluteFill>
    </>
  );
};
