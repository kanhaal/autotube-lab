import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

import {staggerProgress} from '../polish';

export const Stat = ({label, value, suffix = ''}: {label: string; value: number; suffix?: string}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const progress = staggerProgress(frame, fps, 1);
  const shown = Math.round(interpolate(progress, [0, 1], [0, value], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 12}}>
      <div
        style={{
          fontSize: 132,
          fontWeight: 900,
          letterSpacing: -6,
          lineHeight: 0.92,
          transform: `translateY(${(1 - progress) * 24}px) scale(${0.94 + progress * 0.06})`,
          opacity: progress,
        }}
      >
        {shown}{suffix}
      </div>
      <div style={{fontSize: 30, fontWeight: 650, opacity: 0.45 + progress * 0.3}}>{label}</div>
    </div>
  );
};
