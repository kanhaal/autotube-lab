import {spring, useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';

export type TagPopEffectProps = EffectComponentProps;

export const TagPopEffect = ({effect, children, scene, theme}: TagPopEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const tags = Array.isArray(effect.tags)
    ? effect.tags.filter((item): item is string => typeof item === 'string').slice(0, 7)
    : scene.emphasis.slice(0, 7);

  return (
    <>
      {children}
      {tags.length ? (
        <div style={{display: 'flex', flexWrap: 'wrap', gap: 10, left: 72, position: 'absolute', top: 72, zIndex: 74}}>
          {tags.map((tag, index) => {
            const p = spring({frame: frame - index * 4, fps, config: {damping: 12, stiffness: 180, mass: 0.7}});
            return (
              <span
                key={`${tag}-${index}`}
                style={{
                  backdropFilter: 'blur(16px)',
                  background: `${theme.accent}1C`,
                  border: `1px solid ${theme.border}`,
                  borderRadius: 999,
                  color: theme.accent,
                  fontSize: 16,
                  fontWeight: 900,
                  letterSpacing: 0.8,
                  opacity: p,
                  padding: '9px 13px',
                  transform: `translateY(${(1 - p) * -24}px) scale(${0.75 + p * 0.25})`,
                }}
              >
                {tag}
              </span>
            );
          })}
        </div>
      ) : null}
    </>
  );
};
