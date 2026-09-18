import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {CaptionCueV1} from '../types';
import type {ChannelTheme} from '../themes/types';

const normalized = (value: string) => value.toLowerCase().replace(/[^a-z0-9.%+-]/g, '');

const activeCue = (cues: CaptionCueV1[], seconds: number) =>
  cues.find((cue) => seconds >= cue.start && seconds < cue.end);

const wordsFor = (cue: CaptionCueV1) => {
  if (cue.word_timings?.length) return cue.word_timings;
  const words = cue.words.length ? cue.words : cue.text.trim().split(/\s+/).filter(Boolean);
  const duration = Math.max(0.001, cue.end - cue.start);
  return words.map((text, index) => ({
    text,
    start: cue.start + duration * (index / Math.max(1, words.length)),
    end: cue.start + duration * ((index + 1) / Math.max(1, words.length)),
  }));
};

const phraseWindow = (words: ReturnType<typeof wordsFor>, activeIndex: number) => {
  if (!words.length) return [];
  const chunkSize = words.length > 9 ? 5 : words.length > 6 ? 4 : words.length;
  const safeActive = activeIndex < 0 ? 0 : activeIndex;
  const start = Math.floor(safeActive / Math.max(1, chunkSize)) * chunkSize;
  return words.slice(start, start + chunkSize).map((word, index) => ({
    ...word,
    absoluteIndex: start + index,
  }));
};

export const EditorialCaptionTrack = ({
  cues,
  theme,
  format,
}: {
  cues: CaptionCueV1[];
  theme: ChannelTheme;
  format: 'long' | 'short';
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const seconds = frame / Math.max(1, fps);
  const cue = activeCue(cues, seconds);
  if (!cue) return null;

  const allWords = wordsFor(cue);
  const activeIndex = allWords.findIndex((word) => seconds >= word.start && seconds < word.end);
  const phrase = phraseWindow(allWords, activeIndex);
  if (!phrase.length) return null;

  const local = Math.max(0, seconds - cue.start);
  const reveal = Math.min(1, local / 0.16);
  const energetic = theme.transitionFamily === 'snap';

  return (
    <div
      style={{
        bottom: format === 'short' ? 122 : 54,
        left: format === 'short' ? 52 : 90,
        pointerEvents: 'none',
        position: 'absolute',
        right: format === 'short' ? 52 : 90,
        textAlign: format === 'short' ? 'center' : 'left',
        transform: `translateY(${((1 - reveal) * 14).toFixed(2)}px)`,
        opacity: reveal,
        zIndex: 90,
      }}
    >
      <div
        style={{
          display: 'inline',
          filter: 'drop-shadow(0 4px 14px rgba(0,0,0,.72))',
          fontFamily: 'Arial, Helvetica, sans-serif',
          fontSize: format === 'short' ? 58 : 38,
          fontWeight: 850,
          letterSpacing: format === 'short' ? -1.9 : -1.1,
          lineHeight: 1.02,
          maxWidth: format === 'short' ? 940 : 1280,
          textShadow: '0 2px 18px rgba(0,0,0,.78)',
        }}
      >
        {phrase.map((word) => {
          const active = word.absoluteIndex === activeIndex;
          const token = normalized(word.text);
          const numeric = /\d/.test(token);
          const accent = active && (numeric || energetic);
          return (
            <span
              key={word.absoluteIndex}
              style={{
                color: accent ? theme.accent : '#FFFFFF',
                display: 'inline-block',
                fontWeight: numeric ? 950 : active ? 920 : 780,
                marginRight: format === 'short' ? 13 : 10,
                opacity: activeIndex >= 0 && word.absoluteIndex < activeIndex - 2 ? 0.62 : 1,
                textShadow: accent
                  ? `0 0 28px ${theme.accent}55, 0 3px 16px rgba(0,0,0,.8)`
                  : '0 3px 16px rgba(0,0,0,.8)',
                transform: active
                  ? `translateY(-2px) scale(${numeric ? 1.13 : energetic ? 1.08 : 1.045})`
                  : 'scale(1)',
                transformOrigin: 'center bottom',
              }}
            >
              {word.text}
            </span>
          );
        })}
      </div>
    </div>
  );
};
