import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {smoothstep} from './utils';

export type VsScreenEffectProps = EffectComponentProps;

type Side = {label: string; value: number; suffix: string};

const side = (value: unknown, fallback: Side): Side => {
  if (!value || typeof value !== 'object') return fallback;
  const raw = value as Record<string, unknown>;
  return {
    label: typeof raw.label === 'string' ? raw.label : fallback.label,
    value: typeof raw.value === 'number' && Number.isFinite(raw.value) ? raw.value : fallback.value,
    suffix: typeof raw.suffix === 'string' ? raw.suffix : fallback.suffix,
  };
};

export const VsScreenEffect = ({effect, children, theme}: VsScreenEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const progress = smoothstep(frame / Math.max(1, Math.round(fps * 0.7)));
  const left = side(effect.left, {label: 'A', value: 50, suffix: ''});
  const right = side(effect.right, {label: 'B', value: 50, suffix: ''});
  const max = Math.max(1, left.value, right.value);

  return (
    <>
      {children}
      <div
        style={{
          alignItems: 'stretch',
          display: 'grid',
          gap: 18,
          gridTemplateColumns: '1fr 84px 1fr',
          inset: '18% 8%',
          position: 'absolute',
          zIndex: 68,
        }}
      >
        {[left, right].map((entry, index) => (
          <div
            key={entry.label}
            style={{
              backdropFilter: 'blur(18px)',
              background: 'rgba(7,10,16,.82)',
              border: `1px solid ${theme.border}`,
              borderRadius: 26,
              padding: 28,
            }}
          >
            <div style={{color: index === 0 ? theme.foreground : theme.accent, fontSize: 34, fontWeight: 900}}>{entry.label}</div>
            <div style={{fontSize: 62, fontWeight: 950, marginTop: 18}}>{Math.round(entry.value * progress)}{entry.suffix}</div>
            <div style={{background: 'rgba(255,255,255,.09)', borderRadius: 999, height: 12, marginTop: 24, overflow: 'hidden'}}>
              <div
                style={{
                  background: index === 0 ? theme.secondary : theme.accent,
                  borderRadius: 999,
                  height: '100%',
                  width: `${(entry.value / max) * progress * 100}%`,
                }}
              />
            </div>
          </div>
        ))}
        <div style={{alignItems: 'center', color: theme.accent, display: 'flex', fontSize: 32, fontWeight: 950, justifyContent: 'center'}}>
          VS
        </div>
      </div>
    </>
  );
};
