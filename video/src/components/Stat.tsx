import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

import {staggerProgress} from '../polish';

export const Stat = ({label, value, suffix = ''}: {label: string; value: number; suffix?: string}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const progress = staggerProgress(frame, fps, 1);
  const shown = Math.round(interpolate(progress, [0, 1], [0, value], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const orbit = (frame / Math.max(1, fps)) * 24;

  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 14, minHeight: 210, position: 'relative'}}>
      <div
        style={{
          border: '1px solid currentColor',
          borderRadius: '50%',
          height: 210,
          opacity: 0.10 * progress,
          position: 'absolute',
          right: 10,
          top: -42,
          transform: `rotate(${orbit}deg) scale(${0.8 + progress * 0.2})`,
          width: 210,
        }}
      >
        <div style={{background: 'currentColor', height: 2, left: '50%', opacity: 0.4, position: 'absolute', top: -1, width: 48}} />
      </div>
      <div
        style={{
          fontSize: 146,
          fontWeight: 950,
          letterSpacing: -7,
          lineHeight: 0.88,
          opacity: progress,
          position: 'relative',
          textShadow: '0 20px 60px rgba(0,0,0,.26)',
          transform: `translate3d(0,${(1 - progress) * 32}px,0) scale(${0.91 + progress * 0.09})`,
        }}
      >
        <span
          style={{
            color: 'transparent',
            left: 7,
            opacity: 0.18,
            position: 'absolute',
            textShadow: 'none',
            top: 8,
            WebkitTextStroke: '1px currentColor',
          }}
        >
          {shown}{suffix}
        </span>
        <span style={{position: 'relative'}}>{shown}{suffix}</span>
      </div>
      <div
        style={{
          alignItems: 'center',
          display: 'flex',
          fontSize: 30,
          fontWeight: 700,
          gap: 14,
          opacity: 0.42 + progress * 0.34,
        }}
      >
        <span style={{background: 'currentColor', borderRadius: 99, boxShadow: '0 0 18px currentColor', height: 8, width: 36}} />
        {label}
      </div>
    </div>
  );
};
