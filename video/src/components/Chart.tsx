import {useCurrentFrame, useVideoConfig} from 'remotion';

import {staggerProgress} from '../polish';

type ChartPoint = {label: string; value: number};

export const Chart = ({points, accent = '#67F5C5'}: {points: ChartPoint[]; accent?: string}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const max = Math.max(1, ...points.map((point) => point.value));
  const lineProgress = staggerProgress(frame, fps, 2);
  const width = 1000;
  const height = 330;
  const chartPoints = points.map((point, index) => {
    const x = points.length <= 1 ? width / 2 : 60 + (index / (points.length - 1)) * (width - 120);
    const y = 52 + (1 - point.value / max) * 210;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');

  return (
    <div style={{height: 410, overflow: 'hidden', position: 'relative'}}>
      <div
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,.07) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.045) 1px, transparent 1px)',
          backgroundSize: '100% 25%, 14.285% 100%',
          inset: '20px 0 72px',
          opacity: 0.44,
          position: 'absolute',
        }}
      />
      <svg
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
        style={{height: 330, left: 0, overflow: 'visible', position: 'absolute', right: 0, top: 8, width: '100%'}}
      >
        <defs>
          <filter id="chart-glow">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <polyline
          fill="none"
          filter="url(#chart-glow)"
          points={chartPoints}
          stroke={accent}
          strokeDasharray="1400"
          strokeDashoffset={1400 * (1 - lineProgress)}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeOpacity={0.74}
          strokeWidth="5"
        />
        {points.map((point, index) => {
          const progress = staggerProgress(frame, fps, index + 2);
          const x = points.length <= 1 ? width / 2 : 60 + (index / (points.length - 1)) * (width - 120);
          const y = 52 + (1 - point.value / max) * 210;
          return (
            <g key={`${point.label}-dot`} opacity={progress}>
              <circle cx={x} cy={y} fill={accent} opacity="0.22" r={16 * progress} />
              <circle cx={x} cy={y} fill={accent} r={6 * progress} />
            </g>
          );
        })}
      </svg>
      <div style={{alignItems: 'flex-end', bottom: 0, display: 'flex', gap: 24, left: 0, position: 'absolute', right: 0, top: 26}}>
        {points.map((point, index) => {
          const progress = staggerProgress(frame, fps, index + 1);
          const barHeight = Math.max(8, (point.value / max) * 250 * progress);
          const shimmer = ((frame * 7 + index * 80) % 420) - 160;
          return (
            <div key={point.label} style={{alignItems: 'center', display: 'flex', flex: 1, flexDirection: 'column', gap: 10, height: '100%', justifyContent: 'flex-end'}}>
              <div style={{fontSize: 23, fontWeight: 850, opacity: progress, textShadow: `0 0 24px ${accent}33`}}>
                {Math.round(point.value * progress)}
              </div>
              <div
                style={{
                  background: `linear-gradient(180deg, ${accent}, ${accent}88)`,
                  border: '1px solid rgba(255,255,255,.10)',
                  borderRadius: '16px 16px 7px 7px',
                  boxShadow: `0 18px 46px ${accent}20, inset 0 1px 0 rgba(255,255,255,.22)`,
                  height: barHeight,
                  overflow: 'hidden',
                  opacity: 0.3 + progress * 0.7,
                  position: 'relative',
                  transform: `scaleX(${0.84 + progress * 0.16})`,
                  transformOrigin: 'bottom',
                  width: '66%',
                }}
              >
                <div
                  style={{
                    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,.34), transparent)',
                    bottom: 0,
                    position: 'absolute',
                    top: 0,
                    transform: `translateX(${shimmer}px) skewX(-18deg)`,
                    width: 74,
                  }}
                />
              </div>
              <div style={{fontSize: 20, fontWeight: 700, opacity: 0.5 + progress * 0.26, textAlign: 'center'}}>
                {point.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
