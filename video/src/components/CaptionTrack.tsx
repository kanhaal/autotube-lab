import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {CaptionCueV1} from '../types';

export const activeCaptionAt = (cues: CaptionCueV1[], seconds: number): CaptionCueV1 | undefined =>
  cues.find((cue) => seconds >= cue.start && seconds < cue.end);

export const CaptionTrack = ({
  cues,
  accent = '#67F5C5',
  energetic = false,
}: {
  cues: CaptionCueV1[];
  accent?: string;
  energetic?: boolean;
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = activeCaptionAt(cues, frame / fps);
  if (!cue) return null;

  return (
    <div
      style={{
        bottom: energetic ? 96 : 74,
        boxSizing: 'border-box',
        display: 'flex',
        justifyContent: 'center',
        left: 0,
        padding: '0 120px',
        position: 'absolute',
        right: 0,
      }}
    >
      <div
        style={{
          background: 'rgba(4,7,13,0.82)',
          border: '1px solid rgba(255,255,255,0.12)',
          borderRadius: energetic ? 16 : 12,
          boxShadow: '0 12px 34px rgba(0,0,0,0.3)',
          color: '#FFFFFF',
          fontSize: energetic ? 38 : 31,
          fontWeight: 760,
          lineHeight: 1.15,
          maxWidth: 1260,
          padding: energetic ? '16px 24px' : '12px 20px',
          textAlign: 'center',
        }}
      >
        {cue.text}
        <span style={{color: accent}}> </span>
      </div>
    </div>
  );
};
