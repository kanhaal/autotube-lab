import {useCurrentFrame} from 'remotion';

import type {TransitionComponentProps} from './types';

export type WhooshZoomTransitionProps = TransitionComponentProps;

export const WhooshZoomTransition = ({theme, durationInFrames}: WhooshZoomTransitionProps) => {
  const frame = useCurrentFrame();
  const remaining = durationInFrames - 1 - frame;
  const p = Math.max(0, Math.min(1, 1 - remaining / 10));
  if (p <= 0) return null;

  return (
    <div
      style={{
        background:
          `radial-gradient(circle at 50% 50%, transparent 0 ${Math.max(0, 58 - p * 35)}%, ${theme.accent}22 ${65 - p * 20}%, rgba(255,255,255,${(p * 0.22).toFixed(3)}) 74%, transparent 82%)`,
        filter: `blur(${(p * 4).toFixed(2)}px)`,
        inset: '-8%',
        opacity: p,
        pointerEvents: 'none',
        position: 'absolute',
        transform: `scale(${1 + p * 0.22})`,
        zIndex: 130,
      }}
    />
  );
};
