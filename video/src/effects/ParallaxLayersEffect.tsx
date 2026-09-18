import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber} from './utils';

export type ParallaxLayersEffectProps = EffectComponentProps;

export const ParallaxLayersEffect = ({effect, children}: ParallaxLayersEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const amplitude = Math.min(28, Math.max(2, effectNumber(effect, 'amplitude', 10)));
  const x = Math.sin((frame / fps) * 0.8) * amplitude;
  const y = Math.cos((frame / fps) * 0.55) * amplitude * 0.45;
  return (
    <div style={{height: '100%', transform: `translate3d(${x.toFixed(2)}px,${y.toFixed(2)}px,0) scale(1.012)`, width: '100%'}}>
      {children}
    </div>
  );
};
