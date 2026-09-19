import type {EffectRenderProps} from './types';

export const SmashCutTransition = ({frame, durationInFrames, theme}: EffectRenderProps) => {
  const delta = durationInFrames - 1 - frame;
  if (delta < 0 || delta > 3) return null;
  const intensity = delta === 1 ? 1 : delta === 2 ? .42 : .72;
  return (
    <div style={{
      background:delta === 1 ? '#FFFFFF' : theme.accent,
      inset:0,
      mixBlendMode:delta === 1 ? 'screen' : 'color-dodge',
      opacity:intensity,
      pointerEvents:'none',
      position:'absolute',
      zIndex:70,
    }}/>
  );
};
