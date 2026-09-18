import {useCurrentFrame} from 'remotion';

import type {TransitionComponentProps} from './types';

export type GlitchRgbSplitTransitionProps = TransitionComponentProps;

export const GlitchRgbSplitTransition = ({theme, durationInFrames}: GlitchRgbSplitTransitionProps) => {
  const frame = useCurrentFrame();
  const remaining = durationInFrames - 1 - frame;
  const p = Math.max(0, 1 - remaining / 8);
  if (p <= 0) return null;

  return (
    <div style={{inset: 0, overflow: 'hidden', pointerEvents: 'none', position: 'absolute', zIndex: 130}}>
      {[0, 1, 2, 3].map((band) => (
        <div
          key={band}
          style={{
            background: band % 2 === 0 ? `${theme.accent}28` : `${theme.secondary}24`,
            boxShadow: band % 2 === 0 ? '10px 0 rgba(255,0,92,.18)' : '-10px 0 rgba(0,220,255,.18)',
            height: '18%',
            left: `${(band % 2 === 0 ? 1 : -1) * p * 2}%`,
            opacity: p,
            position: 'absolute',
            right: 0,
            top: `${10 + band * 22}%`,
            transform: `skewX(${band % 2 === 0 ? -3 : 3}deg)`,
          }}
        />
      ))}
    </div>
  );
};
