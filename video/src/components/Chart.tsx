import {useCurrentFrame, useVideoConfig} from 'remotion';

import {staggerProgress} from '../polish';

type ChartPoint = {label: string; value: number};

export const Chart = ({points, accent = '#67F5C5'}: {points: ChartPoint[]; accent?: string}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const max = Math.max(1, ...points.map((point) => point.value));
  return (
    <div style={{alignItems: 'flex-end', display: 'flex', gap: 28, height: 380}}>
      {points.map((point, index) => {
        const progress = staggerProgress(frame, fps, index + 1);
        const height = Math.max(8, (point.value / max) * 286 * progress);
        return (
          <div key={point.label} style={{alignItems: 'center', display: 'flex', flex: 1, flexDirection: 'column', gap: 12}}>
            <div style={{fontSize: 23, fontWeight: 800, opacity: progress}}>
              {Math.round(point.value * progress)}
            </div>
            <div
              style={{
                background: `linear-gradient(180deg, ${accent}, ${accent}AA)`,
                borderRadius: '18px 18px 7px 7px',
                boxShadow: `0 14px 40px ${accent}22`,
                height,
                opacity: 0.35 + progress * 0.65,
                transform: `scaleX(${0.86 + progress * 0.14})`,
                transformOrigin: 'bottom',
                width: '76%',
              }}
            />
            <div style={{fontSize: 20, fontWeight: 650, opacity: 0.52 + progress * 0.25, textAlign: 'center'}}>
              {point.label}
            </div>
          </div>
        );
      })}
    </div>
  );
};
