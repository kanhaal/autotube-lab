import {Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectBox, effectNumber, sceneAsset, smoothstep} from './utils';

export type ScrollRevealEffectProps = EffectComponentProps;

export const ScrollRevealEffect = ({effect, children, assets, theme, durationInFrames}: ScrollRevealEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const asset = sceneAsset(effect, assets);
  const start = Math.max(0, Math.round(effectNumber(effect, 'start_seconds', 0) * fps));
  const endFrame = Math.min(
    durationInFrames - 1,
    Math.max(start + 1, Math.round(effectNumber(effect, 'end_seconds', durationInFrames / fps) * fps)),
  );
  const progress = smoothstep((frame - start) / Math.max(1, endFrame - start));
  const highlight = effectBox(effect, 'highlight', {x: 0.08, y: 0.35, width: 0.84, height: 0.15});
  const travel = Math.max(0, Math.min(70, effectNumber(effect, 'travel_percent', 38)));

  return (
    <>
      {children}
      {asset ? (
        <div
          style={{
            background: '#05080D',
            border: `1px solid ${theme.border}`,
            borderRadius: 24,
            bottom: '9%',
            boxShadow: '0 30px 90px rgba(0,0,0,.45)',
            left: '9%',
            overflow: 'hidden',
            position: 'absolute',
            right: '9%',
            top: '12%',
            zIndex: 66,
          }}
        >
          <Img
            src={staticFile(asset.local_path)}
            style={{
              height: `${100 + travel}%`,
              objectFit: 'cover',
              objectPosition: 'top center',
              transform: `translateY(-${(progress * travel).toFixed(2)}%)`,
              width: '100%',
            }}
          />
          <div
            style={{
              border: `2px solid ${theme.accent}`,
              borderRadius: 12,
              boxShadow: `0 0 0 999px rgba(0,0,0,.22), 0 0 30px ${theme.accent}55`,
              height: `${highlight.height * 100}%`,
              left: `${highlight.x * 100}%`,
              position: 'absolute',
              top: `${highlight.y * 100}%`,
              width: `${highlight.width * 100}%`,
            }}
          />
        </div>
      ) : null}
    </>
  );
};
