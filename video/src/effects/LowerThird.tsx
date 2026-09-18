import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {SceneSpecV1} from '../types';
import type {ChannelTheme} from '../themes/types';
import {smoothstep} from './utils';

export type LowerThirdProps = {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  label?: string;
};

export const LowerThird = ({scene, theme, label}: LowerThirdProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = smoothstep((frame - fps * 0.18) / Math.max(1, fps * 0.28));
  const exit = 1 - smoothstep((frame - fps * 2.25) / Math.max(1, fps * 0.25));
  const p = Math.min(enter, exit);
  if (p <= 0) return null;

  return (
    <div
      style={{
        alignItems: 'center',
        backdropFilter: 'blur(20px)',
        background: 'linear-gradient(135deg, rgba(7,10,16,.82), rgba(7,10,16,.56))',
        border: `1px solid ${theme.border}`,
        borderRadius: 18,
        bottom: 58,
        boxShadow: '0 18px 58px rgba(0,0,0,.38)',
        display: 'flex',
        gap: 14,
        left: 66,
        maxWidth: '66%',
        opacity: p,
        padding: '13px 18px',
        position: 'absolute',
        transform: `translateY(${(1 - p) * 22}px)`,
        zIndex: 92,
      }}
    >
      <span style={{background: theme.accent, borderRadius: 99, boxShadow: `0 0 18px ${theme.accent}`, height: 10, width: 10}} />
      <div>
        <div style={{color: theme.accent, fontSize: 13, fontWeight: 950, letterSpacing: 1.8, textTransform: 'uppercase'}}>
          {label || scene.purpose || 'SOURCE VERIFIED'}
        </div>
        <div style={{fontSize: 20, fontWeight: 820, marginTop: 2}}>
          {scene.subheadline || scene.headline}
        </div>
      </div>
    </div>
  );
};
