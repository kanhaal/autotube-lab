import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber, effectString, smoothstep} from './utils';

export type LeaderLineEffectProps = EffectComponentProps;

export const LeaderLineEffect = ({effect, children, theme}: LeaderLineEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = smoothstep(frame / Math.max(1, fps * 0.45));
  const x1 = effectNumber(effect, 'x1', 24);
  const y1 = effectNumber(effect, 'y1', 32);
  const x2 = effectNumber(effect, 'x2', 64);
  const y2 = effectNumber(effect, 'y2', 58);
  const label = effectString(effect, 'label', '');

  return (
    <>
      {children}
      <svg height="100%" style={{inset: 0, pointerEvents: 'none', position: 'absolute', zIndex: 78}} viewBox="0 0 100 100" width="100%">
        <line
          x1={x1}
          y1={y1}
          x2={x1 + (x2 - x1) * p}
          y2={y1 + (y2 - y1) * p}
          stroke={theme.accent}
          strokeLinecap="round"
          strokeWidth="0.35"
        />
        <circle cx={x2} cy={y2} fill={theme.accent} opacity={p} r="0.7" />
      </svg>
      {label ? (
        <div
          style={{
            background: 'rgba(5,8,14,.82)',
            border: `1px solid ${theme.border}`,
            borderRadius: 12,
            fontSize: 16,
            fontWeight: 850,
            left: `${x2}%`,
            opacity: p,
            padding: '8px 11px',
            position: 'absolute',
            top: `${y2}%`,
            transform: 'translate(10px,-50%)',
            zIndex: 79,
          }}
        >
          {label}
        </div>
      ) : null}
    </>
  );
};
