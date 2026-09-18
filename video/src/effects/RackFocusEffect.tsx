import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber, smoothstep} from './utils';

export type RackFocusEffectProps = EffectComponentProps;

export const RackFocusEffect = ({effect, children}: RackFocusEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const at = Math.max(0, effectNumber(effect, 'at_seconds', 0) * fps);
  const duration = Math.max(1, effectNumber(effect, 'duration_seconds', 0.45) * fps);
  const p = smoothstep((frame - at) / duration);
  const from = Math.min(12, Math.max(0, effectNumber(effect, 'from_blur', 7)));
  const to = Math.min(12, Math.max(0, effectNumber(effect, 'to_blur', 0)));
  const blur = from + (to - from) * p;
  return <div style={{filter: `blur(${blur.toFixed(2)}px)`, height: '100%', width: '100%'}}>{children}</div>;
};
