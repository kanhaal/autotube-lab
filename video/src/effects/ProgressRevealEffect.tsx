import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber, effectString, smoothstep} from './utils';

export type ProgressRevealEffectProps = EffectComponentProps;

export const ProgressRevealEffect = ({effect, children, theme}: ProgressRevealEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const target = Math.min(100, Math.max(0, effectNumber(effect, 'percent', 100)));
  const duration = Math.max(1, Math.round(effectNumber(effect, 'duration_seconds', 0.7) * fps));
  const p = smoothstep(frame / duration);
  const label = effectString(effect, 'label', '');

  return (
    <>
      {children}
      <div style={{bottom: 70, left: '10%', position: 'absolute', right: '10%', zIndex: 72}}>
        {label ? <div style={{fontSize: 18, fontWeight: 850, marginBottom: 10}}>{label}</div> : null}
        <div style={{background: 'rgba(255,255,255,.11)', borderRadius: 999, height: 10, overflow: 'hidden'}}>
          <div
            style={{
              background: `linear-gradient(90deg, ${theme.accent}, ${theme.secondary})`,
              borderRadius: 999,
              boxShadow: `0 0 24px ${theme.accent}66`,
              height: '100%',
              width: `${target * p}%`,
            }}
          />
        </div>
      </div>
    </>
  );
};
