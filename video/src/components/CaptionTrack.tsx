import {useCurrentFrame, useVideoConfig} from 'remotion';

import {activeWordIndex, staggerProgress} from '../polish';
import type {CaptionCueV1} from '../types';

export const activeCaptionAt = (cues: CaptionCueV1[], seconds: number): CaptionCueV1 | undefined =>
  cues.find((cue) => seconds >= cue.start && seconds < cue.end);

const cueWords = (cue: CaptionCueV1): string[] => {
  if (cue.word_timings?.length) return cue.word_timings.map((word) => word.text);
  if (cue.words.length) return cue.words;
  return cue.text.trim().split(/\s+/).filter(Boolean);
};

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
  const seconds = frame / fps;
  const cue = activeCaptionAt(cues, seconds);
  if (!cue) return null;

  const words = cueWords(cue);
  const active = activeWordIndex(cue, seconds);
  const reveal = staggerProgress(Math.max(0, frame - Math.round(cue.start * fps)), fps, 0);

  return (
    <div
      style={{
        bottom: energetic ? 62 : 54,
        boxSizing: 'border-box',
        display: 'flex',
        justifyContent: 'center',
        left: 0,
        padding: '0 150px',
        position: 'absolute',
        right: 0,
        transform: `translateY(${(1 - reveal) * 18}px)`,
        opacity: reveal,
      }}
    >
      <div
        style={{
          backdropFilter: 'blur(18px)',
          background: 'rgba(4,7,13,0.72)',
          border: '1px solid rgba(255,255,255,0.10)',
          borderRadius: 18,
          boxShadow: '0 18px 52px rgba(0,0,0,0.30)',
          color: '#FFFFFF',
          fontFamily: 'Arial, Helvetica, sans-serif',
          fontSize: energetic ? 36 : 31,
          fontWeight: 800,
          letterSpacing: -0.35,
          lineHeight: 1.18,
          maxWidth: 1320,
          padding: energetic ? '15px 24px 17px' : '13px 22px 15px',
          textAlign: 'center',
        }}
      >
        {words.map((word, index) => (
          <span
            key={`${word}-${index}`}
            style={{
              color: index === active ? accent : '#FFFFFF',
              display: 'inline-block',
              marginRight: index === words.length - 1 ? 0 : 9,
              opacity: index > active + 3 && active >= 0 ? 0.68 : 1,
              textShadow: index === active ? `0 0 22px ${accent}55` : 'none',
              transform: index === active ? 'scale(1.06)' : 'scale(1)',
              transformOrigin: 'center bottom',
            }}
          >
            {word}
          </span>
        ))}
      </div>
    </div>
  );
};
