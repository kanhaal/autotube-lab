import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectString, smoothstep} from './utils';

export type ChapterCardProps = EffectComponentProps;

export const ChapterCard = ({effect, children, scene, theme}: ChapterCardProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = smoothstep(frame / Math.max(1, fps * 0.4));
  const title = effectString(effect, 'title', scene.headline);
  const kicker = effectString(effect, 'kicker', 'NEXT SIGNAL');
  return (
    <>
      {children}
      <div
        style={{
          alignItems: 'center',
          backdropFilter: 'blur(24px)',
          background: 'linear-gradient(135deg, rgba(4,8,14,.92), rgba(4,8,14,.68))',
          border: `1px solid ${theme.border}`,
          borderRadius: 30,
          display: 'flex',
          inset: '22% 12%',
          justifyContent: 'center',
          opacity: p,
          position: 'absolute',
          textAlign: 'center',
          transform: `scale(${0.94 + p * 0.06})`,
          zIndex: 88,
        }}
      >
        <div>
          <div style={{color: theme.accent, fontSize: 18, fontWeight: 950, letterSpacing: 4}}>{kicker}</div>
          <div style={{fontSize: 62, fontWeight: 950, letterSpacing: -2.4, marginTop: 16}}>{title}</div>
        </div>
      </div>
    </>
  );
};
