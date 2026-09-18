import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectString, smoothstep} from './utils';

export type TickerOverlayEffectProps = EffectComponentProps;

export const TickerOverlayEffect = ({effect, children, theme}: TickerOverlayEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const progress = smoothstep(frame / Math.max(1, Math.round(fps * 0.28)));
  const text = effectString(effect, 'text', '');
  const rawBadge = effectString(effect, 'badge', '');
  const badge = rawBadge === 'LEAK' || rawBadge === 'UNCONFIRMED' ? rawBadge : '';

  return (
    <>
      {children}
      {text ? (
        <div
          style={{
            alignItems: 'center',
            backdropFilter: 'blur(18px)',
            background: 'rgba(4,7,13,.88)',
            border: `1px solid ${theme.border}`,
            borderRadius: 18,
            bottom: 62,
            boxShadow: '0 18px 60px rgba(0,0,0,.4)',
            display: 'flex',
            gap: 16,
            left: 70,
            maxWidth: '78%',
            opacity: progress,
            padding: '14px 20px',
            position: 'absolute',
            transform: `translateY(${(1 - progress) * 24}px)`,
            zIndex: 82,
          }}
        >
          {badge ? (
            <span
              style={{
                background: badge === 'LEAK' ? '#FF3D6E' : '#FFB547',
                borderRadius: 999,
                color: '#090B10',
                fontSize: 14,
                fontWeight: 950,
                letterSpacing: 1.6,
                padding: '7px 10px',
              }}
            >
              {badge}
            </span>
          ) : null}
          <span style={{fontSize: 22, fontWeight: 820}}>{text}</span>
        </div>
      ) : null}
    </>
  );
};
