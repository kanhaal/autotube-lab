import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectString, smoothstep} from './utils';

export type SplitCompareEffectProps = EffectComponentProps;

export const SplitCompareEffect = ({effect, children, theme}: SplitCompareEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const progress = smoothstep(frame / Math.max(1, Math.round(fps * 0.55)));
  const left = effectString(effect, 'left_label', 'BEFORE');
  const right = effectString(effect, 'right_label', 'AFTER');

  return (
    <>
      {children}
      <div style={{inset: '16% 8%', pointerEvents: 'none', position: 'absolute', zIndex: 68}}>
        <div
          style={{
            background: 'rgba(5,8,14,.48)',
            border: `1px solid ${theme.border}`,
            borderRadius: 28,
            height: '100%',
            overflow: 'hidden',
            position: 'relative',
          }}
        >
          <div style={{alignItems: 'flex-start', display: 'flex', height: '100%', justifyContent: 'space-between', padding: 26}}>
            <span style={{color: theme.muted, fontSize: 20, fontWeight: 900, letterSpacing: 2}}>{left}</span>
            <span style={{color: theme.accent, fontSize: 20, fontWeight: 900, letterSpacing: 2}}>{right}</span>
          </div>
          <div
            style={{
              background: `linear-gradient(180deg, transparent, ${theme.accent}, transparent)`,
              boxShadow: `0 0 28px ${theme.accent}99`,
              bottom: 0,
              left: `${progress * 100}%`,
              position: 'absolute',
              top: 0,
              width: 3,
            }}
          />
        </div>
      </div>
    </>
  );
};
