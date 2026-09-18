import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectString, smoothstep} from './utils';

export type IconMorphEffectProps = EffectComponentProps;

export const IconMorphEffect = ({effect, children, theme}: IconMorphEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = smoothstep(frame / Math.max(1, fps * 0.45));
  const from = effectString(effect, 'from_icon', '●');
  const to = effectString(effect, 'to_icon', '◆');
  return (
    <>
      {children}
      <div style={{height: 70, position: 'absolute', right: 78, top: 72, width: 70, zIndex: 75}}>
        <div style={{color: theme.secondary, fontSize: 58, opacity: 1 - p, position: 'absolute', transform: `rotate(${p * 45}deg) scale(${1 - p * 0.3})`}}>{from}</div>
        <div style={{color: theme.accent, fontSize: 58, opacity: p, position: 'absolute', transform: `rotate(${(p - 1) * -45}deg) scale(${0.7 + p * 0.3})`}}>{to}</div>
      </div>
    </>
  );
};
