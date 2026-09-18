import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber} from './utils';

export type ScreenShakeEffectProps = EffectComponentProps;

export const ScreenShakeEffect = ({effect, children}: ScreenShakeEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const at = Math.round(effectNumber(effect, 'at_seconds', 0) * fps);
  const frames = Math.min(3, Math.max(1, Math.round(effectNumber(effect, 'frames', 2))));
  const active = frame >= at && frame < at + frames;
  const amp = Math.min(10, Math.max(1, effectNumber(effect, 'amplitude', 4)));
  const x = active ? (frame % 2 === 0 ? amp : -amp) : 0;
  const y = active ? (frame % 3 === 0 ? -amp * 0.55 : amp * 0.35) : 0;
  return <div style={{height: '100%', transform: `translate3d(${x}px,${y}px,0)`, width: '100%'}}>{children}</div>;
};
