import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber, effectString, smoothstep} from './utils';

export type StatCountUpEffectProps = EffectComponentProps;

export const StatCountUpEffect = ({effect, children, scene, theme}: StatCountUpEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sceneValue = typeof scene.data.value === 'number' ? scene.data.value : 0;
  const finalValue = effectNumber(
    effect,
    'verified_value',
    effectNumber(effect, 'final_value', sceneValue),
  );
  const duration = Math.max(1, Math.round(effectNumber(effect, 'duration_seconds', 0.8) * fps));
  const start = Math.max(0, Math.round(effectNumber(effect, 'start_seconds', 0) * fps));
  const progress = smoothstep((frame - start) / duration);
  const value = finalValue * progress;
  const decimals = Math.max(0, Math.min(3, Math.round(effectNumber(effect, 'decimals', 0))));
  const label = effectString(
    effect,
    'label',
    typeof scene.data.label === 'string' ? scene.data.label : scene.subheadline,
  );
  const suffix = effectString(
    effect,
    'suffix',
    typeof scene.data.suffix === 'string' ? scene.data.suffix : '',
  );

  return (
    <>
      {children}
      <div
        style={{
          backdropFilter: 'blur(20px)',
          background: 'rgba(6,10,16,.76)',
          border: `1px solid ${theme.border}`,
          borderRadius: 22,
          boxShadow: `0 18px 60px rgba(0,0,0,.35), 0 0 40px ${theme.accent}18`,
          color: '#fff',
          padding: '18px 24px',
          position: 'absolute',
          right: 78,
          top: 82,
          zIndex: 72,
        }}
      >
        <div style={{color: theme.muted, fontSize: 16, fontWeight: 800, letterSpacing: 1.6, textTransform: 'uppercase'}}>{label}</div>
        <div style={{color: theme.accent, fontSize: 54, fontWeight: 900, letterSpacing: -2}}>
          {value.toFixed(decimals)}{suffix}
        </div>
      </div>
    </>
  );
};
