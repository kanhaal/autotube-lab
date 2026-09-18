import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {ChannelTheme} from '../themes/types';
import {smoothstep} from './utils';

export type IntroStingProps = {
  channelName: string;
  theme: ChannelTheme;
  enabled: boolean;
};

export const IntroSting = ({channelName, theme, enabled}: IntroStingProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (!enabled) return null;
  const duration = Math.max(1, Math.round(fps * 0.78));
  if (frame >= duration) return null;
  const enter = smoothstep(frame / Math.max(1, fps * 0.16));
  const exit = 1 - smoothstep((frame - fps * 0.5) / Math.max(1, fps * 0.24));
  const p = Math.min(enter, exit);

  return (
    <div
      style={{
        alignItems: 'center',
        background: `radial-gradient(circle at 50% 50%, ${theme.accent}28, transparent 42%), ${theme.background}`,
        display: 'flex',
        inset: 0,
        justifyContent: 'center',
        opacity: p,
        position: 'absolute',
        zIndex: 140,
      }}
    >
      <div style={{textAlign: 'center', transform: `scale(${0.92 + enter * 0.08})`}}>
        <div style={{color: theme.accent, fontSize: 19, fontWeight: 950, letterSpacing: 6}}>AUTOTUBE SIGNAL</div>
        <div style={{fontSize: 70, fontWeight: 950, letterSpacing: -3, marginTop: 10}}>{channelName}</div>
        <div style={{background: `linear-gradient(90deg, transparent, ${theme.accent}, ${theme.secondary}, transparent)`, height: 3, margin: '20px auto 0', width: 260}} />
      </div>
    </div>
  );
};
