import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {smoothstep} from './utils';

export type KineticInfographicEffectProps = EffectComponentProps;

export const KineticInfographicEffect = ({effect, children, theme}: KineticInfographicEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const values = Array.isArray(effect.values)
    ? effect.values.filter((value): value is number => typeof value === 'number' && Number.isFinite(value)).slice(0, 6)
    : [];
  const labels = Array.isArray(effect.labels)
    ? effect.labels.filter((value): value is string => typeof value === 'string').slice(0, values.length)
    : [];
  const max = Math.max(1, ...values);

  return (
    <>
      {children}
      {values.length ? (
        <div
          style={{
            backdropFilter: 'blur(18px)',
            background: 'rgba(5,8,14,.78)',
            border: `1px solid ${theme.border}`,
            borderRadius: 24,
            bottom: '10%',
            display: 'flex',
            gap: 18,
            left: '9%',
            padding: 26,
            position: 'absolute',
            right: '9%',
            zIndex: 68,
          }}
        >
          {values.map((value, index) => {
            const p = smoothstep((frame - index * 4) / Math.max(1, fps * 0.65));
            return (
              <div key={`${labels[index]}-${index}`} style={{flex: 1}}>
                <div style={{color: theme.muted, fontSize: 15, fontWeight: 800, minHeight: 36}}>{labels[index] || `#${index + 1}`}</div>
                <div style={{alignItems: 'flex-end', display: 'flex', height: 150}}>
                  <div
                    style={{
                      background: `linear-gradient(180deg, ${theme.accent}, ${theme.secondary})`,
                      borderRadius: '10px 10px 3px 3px',
                      boxShadow: `0 0 22px ${theme.accent}33`,
                      height: `${Math.max(4, (value / max) * p * 100)}%`,
                      width: '100%',
                    }}
                  />
                </div>
                <div style={{fontSize: 24, fontWeight: 900, marginTop: 10}}>{Math.round(value * p)}</div>
              </div>
            );
          })}
        </div>
      ) : null}
    </>
  );
};
