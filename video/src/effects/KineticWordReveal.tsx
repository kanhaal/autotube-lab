import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {CaptionCueV1} from '../types';
import type {EffectComponentProps} from './types';

export type KineticWordRevealProps = EffectComponentProps;

const activeCue = (cues: CaptionCueV1[], seconds: number): CaptionCueV1 | undefined =>
  cues.find((cue) => seconds >= cue.start && seconds < cue.end);

export const KineticWordReveal = ({
  effect,
  children,
  captions,
  absoluteFrom,
  scene,
  theme,
}: KineticWordRevealProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const seconds = (absoluteFrom + frame) / Math.max(1, fps);
  const cue = activeCue(captions, seconds);
  const timings = cue?.word_timings || [];
  const stressed = new Set(
    [
      ...scene.emphasis,
      ...(Array.isArray(effect.stressed_words)
        ? effect.stressed_words.filter((item): item is string => typeof item === 'string')
        : []),
    ].map((word) => word.toLowerCase().replace(/[^a-z0-9]/g, '')),
  );

  return (
    <>
      {children}
      {cue && timings.length ? (
        <div
          style={{
            bottom: 132,
            left: '8%',
            position: 'absolute',
            right: '8%',
            textAlign: 'center',
            zIndex: 95,
          }}
        >
          {timings.map((word, index) => {
            const normalized = word.text.toLowerCase().replace(/[^a-z0-9]/g, '');
            const active = seconds >= word.start && seconds < word.end;
            const stress = active && (stressed.has(normalized) || /\d/.test(normalized));
            return (
              <span
                key={`${word.text}-${index}`}
                style={{
                  color: active ? theme.accent : '#fff',
                  display: 'inline-block',
                  fontSize: stress ? 56 : active ? 50 : 42,
                  fontWeight: stress ? 950 : 850,
                  margin: '0 6px',
                  opacity: active ? 1 : 0.66,
                  textShadow: active ? `0 0 26px ${theme.accent}55` : '0 3px 16px rgba(0,0,0,.5)',
                  transform: `scale(${stress ? 1.13 : active ? 1.06 : 1}) translateY(${active ? -4 : 0}px)`,
                }}
              >
                {word.text}
              </span>
            );
          })}
        </div>
      ) : null}
    </>
  );
};
