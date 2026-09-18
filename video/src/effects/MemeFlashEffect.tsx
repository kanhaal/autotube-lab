import {Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber, effectString, sceneAsset} from './utils';

export type MemeFlashEffectProps = EffectComponentProps;

export const clampMemeFlashSeconds = (seconds: number): number =>
  Math.min(1.5, Math.max(0.5, Number.isFinite(seconds) ? seconds : 0.75));

export const MemeFlashEffect = ({effect, children, assets}: MemeFlashEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const start = Math.max(0, Math.round(effectNumber(effect, 'start_seconds', 0) * fps));
  const durationSeconds = clampMemeFlashSeconds(effectNumber(effect, 'duration_seconds', 0.75));
  const durationFrames = Math.max(1, Math.round(durationSeconds * fps));
  const active = frame >= start && frame < start + durationFrames;
  const asset = sceneAsset(effect, assets);
  const text = effectString(effect, 'text', '');

  return (
    <>
      {children}
      {active ? (
        <div
          data-meme-flash-seconds={durationSeconds.toFixed(3)}
          style={{
            alignItems: 'center',
            background: '#05060A',
            display: 'flex',
            inset: 0,
            justifyContent: 'center',
            overflow: 'hidden',
            position: 'absolute',
            zIndex: 120,
          }}
        >
          {asset ? <Img src={staticFile(asset.local_path)} style={{height: '100%', objectFit: 'contain', width: '100%'}} /> : null}
          {text ? (
            <div
              style={{
                color: '#fff',
                fontSize: 64,
                fontWeight: 950,
                left: '8%',
                position: 'absolute',
                right: '8%',
                textAlign: 'center',
                textShadow: '0 4px 22px rgba(0,0,0,.7)',
                top: '10%',
              }}
            >
              {text}
            </div>
          ) : null}
        </div>
      ) : null}
    </>
  );
};
