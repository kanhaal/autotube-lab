import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

import type {CursorPoint, EffectComponentProps} from './types';

export type CursorSmoothEffectProps = EffectComponentProps;

const parsePoints = (value: unknown): CursorPoint[] => {
  if (!Array.isArray(value)) return [];
  const points: CursorPoint[] = [];
  for (const item of value) {
    if (!item || typeof item !== 'object') continue;
    const raw = item as Record<string, unknown>;
    if (typeof raw.x !== 'number' || typeof raw.y !== 'number') continue;
    const point: CursorPoint = {
      x: Math.min(1, Math.max(0, raw.x)),
      y: Math.min(1, Math.max(0, raw.y)),
    };
    if (typeof raw.at === 'number' && Number.isFinite(raw.at)) {
      point.at = Math.min(1, Math.max(0, raw.at));
    }
    points.push(point);
  }
  return points;
};

export const CursorSmoothEffect = ({effect, children, theme, durationInFrames}: CursorSmoothEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const points = parsePoints(effect.path);
  const fallback: CursorPoint[] = [{x: 0.28, y: 0.3}, {x: 0.68, y: 0.55}];
  const path = points.length >= 2 ? points : fallback;
  const start = typeof effect.start_seconds === 'number' ? effect.start_seconds * fps : 0;
  const end = typeof effect.end_seconds === 'number'
    ? effect.end_seconds * fps
    : Math.max(start + 1, durationInFrames - 1);
  const progress = Math.min(1, Math.max(0, (frame - start) / Math.max(1, end - start)));
  const segmentFloat = progress * (path.length - 1);
  const index = Math.min(path.length - 2, Math.floor(segmentFloat));
  const local = segmentFloat - index;
  const eased = local * local * (3 - 2 * local);
  const from = path[index];
  const to = path[index + 1];
  const x = interpolate(eased, [0, 1], [from.x, to.x]);
  const y = interpolate(eased, [0, 1], [from.y, to.y]);

  return (
    <>
      {children}
      <AbsoluteFill style={{pointerEvents: 'none', zIndex: 80}}>
        <div
          style={{
            filter: 'drop-shadow(0 5px 8px rgba(0,0,0,.45))',
            left: `${x * 100}%`,
            position: 'absolute',
            top: `${y * 100}%`,
            transform: 'translate(-4px,-4px) rotate(-18deg)',
          }}
        >
          <div
            style={{
              borderBottom: '18px solid transparent',
              borderLeft: `12px solid ${theme.accent}`,
              borderTop: '18px solid transparent',
              height: 0,
              width: 0,
            }}
          />
        </div>
      </AbsoluteFill>
    </>
  );
};
