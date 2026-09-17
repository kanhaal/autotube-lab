import {interpolate, useCurrentFrame} from 'remotion';

export const Stat = ({label, value, suffix = ''}: {label: string; value: number; suffix?: string}) => {
  const frame = useCurrentFrame();
  const shown = Math.round(interpolate(frame, [0, 18], [0, value], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 12}}>
      <div style={{fontSize: 116, fontWeight: 850, letterSpacing: -5}}>{shown}{suffix}</div>
      <div style={{fontSize: 30, fontWeight: 600, opacity: 0.7}}>{label}</div>
    </div>
  );
};
