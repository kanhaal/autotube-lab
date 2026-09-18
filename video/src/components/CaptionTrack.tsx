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
          backdropFilter: 'blur(24px)',
          background: 'linear-gradient(180deg, rgba(9,12,20,.76), rgba(3,5,10,.64))',
          border: '1px solid rgba(255,255,255,0.11)',
          borderRadius: 20,
          boxShadow: '0 22px 70px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,.055)',
          color: '#FFFFFF',
          fontFamily: 'Arial, Helvetica, sans-serif',
          fontSize: energetic ? 36 : 31,
          fontWeight: 800,
          letterSpacing: -0.35,
          lineHeight: 1.18,
          maxWidth: 1220,
          padding: energetic ? '16px 25px 18px' : '14px 23px 16px',
          textAlign: 'center',
        }}
      >
        {words.map((word, index) => (
          <span
            key={`${word}-${index}`}
            style={{
              background: energetic && index === active ? accent : 'transparent',
              borderRadius: energetic && index === active ? 7 : 0,
              boxShadow: index === active ? `0 0 24px ${accent}33` : 'none',
              color: index === active ? (energetic ? '#07100D' : accent) : '#FFFFFF',
              display: 'inline-block',
              marginRight: index === words.length - 1 ? 0 : 8,
              opacity: active >= 0 && Math.abs(index - active) > 4 ? 0.62 : 1,
              padding: energetic && index === active ? '1px 6px 3px' : '1px 1px 3px',
              textShadow: index === active && !energetic ? `0 0 22px ${accent}55` : 'none',
              transform: index === active ? 'translateY(-1px) scale(1.065)' : 'scale(1)',
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
