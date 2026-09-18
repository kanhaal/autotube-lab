import {Freeze, useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber} from './utils';

export type FreezeFrameEffectProps = EffectComponentProps;

export const FreezeFrameEffect = ({effect, children}: FreezeFrameEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const freezeAt = Math.max(0, Math.round(effectNumber(effect, 'at_seconds', 0) * fps));
  const duration = Math.max(1, Math.round(effectNumber(effect, 'duration_seconds', 0.8) * fps));
  const active = frame >= freezeAt && frame < freezeAt + duration;

  return (
    <Freeze frame={freezeAt} active={active}>
      {children}
    </Freeze>
  );
};
