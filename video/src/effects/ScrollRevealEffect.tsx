import {Img, staticFile} from 'remotion';

import type {BoundingBox, EffectRenderProps} from './types';
import {eased, normalizedProgress} from './math';

export type ScrollRevealEffectProps = EffectRenderProps;

export const ScrollRevealEffect = ({
  effect,
  frame,
  fps,
  absoluteFrame,
  durationInFrames,
  assets,
  theme,
}: ScrollRevealEffectProps) => {
  const asset = assets.find((item) => item.id === String(effect.asset_id ?? ''));
  if (!asset) return null;

  const absoluteSeconds = absoluteFrame / Math.max(1, fps);
  const captionStart = Number(effect.caption_start ?? Number.NaN);
  const captionEnd = Number(effect.caption_end ?? Number.NaN);
  const hasCaptionWindow =
    Number.isFinite(captionStart) && Number.isFinite(captionEnd) && captionEnd > captionStart;
  const timelineProgress = hasCaptionWindow
    ? normalizedProgress(absoluteSeconds, captionStart, captionEnd)
    : normalizedProgress(frame, 0, Math.max(1, durationInFrames - 1));
  const p = eased(timelineProgress);
  const fromY = Number(effect.start_y ?? 0);
  const toY = Number(effect.end_y ?? -55);
  const box = effect.highlight as BoundingBox | undefined;

  return (
    <div style={{borderRadius: 22, inset: '8%', overflow: 'hidden', position: 'absolute', zIndex: 12}}>
      <Img
        src={staticFile(asset.local_path)}
        style={{transform: `translateY(${fromY + (toY - fromY) * p}%)`, width: '100%'}}
      />
      {box ? (
        <div
          style={{
            border: `3px solid ${theme.accent}`,
            boxShadow: `0 0 28px ${theme.accent}66`,
            height: `${box.height * 100}%`,
            left: `${box.x * 100}%`,
            opacity: 0.45 + p * 0.55,
            position: 'absolute',
            top: `${box.y * 100}%`,
            width: `${box.width * 100}%`,
          }}
        />
      ) : null}
    </div>
  );
};
