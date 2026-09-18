import type {ReactNode} from 'react';

import type {ChannelTheme} from '../themes/types';
import type {
  AssetRecordV1,
  CaptionCueV1,
  SceneEffectRequestV1,
  SceneSpecV1,
  TransitionOutV1,
} from '../types';

export type TargetBox = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type CursorPoint = {
  x: number;
  y: number;
  at?: number;
};

export type EffectComponentProps<T extends SceneEffectRequestV1 = SceneEffectRequestV1> = {
  effect: T;
  scene: SceneSpecV1;
  theme: ChannelTheme;
  assets: AssetRecordV1[];
  captions: CaptionCueV1[];
  absoluteFrom: number;
  durationInFrames: number;
  children: ReactNode;
};

export type TransitionComponentProps = {
  kind: TransitionOutV1;
  theme: ChannelTheme;
  durationInFrames: number;
};

export type EffectComponent = (props: EffectComponentProps) => ReactNode;
export type TransitionComponent = (props: TransitionComponentProps) => ReactNode;
