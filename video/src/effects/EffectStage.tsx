import type {ReactNode} from 'react';
import {Audio, Sequence, staticFile, useVideoConfig} from 'remotion';

import type {AssetRecordV1, CaptionCueV1, SceneSpecV1} from '../types';
import type {ChannelTheme} from '../themes/types';
import type {ChannelEffectProfile} from './channelEffects';
import {effectRegistry, transitionRegistry} from './effectRegistry';
import {IntroSting} from './IntroSting';
import {LowerThird} from './LowerThird';
import {effectNumber, effectString} from './utils';

export type EffectStageProps = {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  profile: ChannelEffectProfile;
  assets: AssetRecordV1[];
  captions: CaptionCueV1[];
  absoluteFrom: number;
  durationInFrames: number;
  isFirstScene?: boolean;
  channelName: string;
  children: ReactNode;
};

export const EffectStage = ({
  scene,
  theme,
  profile,
  assets,
  captions,
  absoluteFrom,
  durationInFrames,
  isFirstScene = false,
  channelName,
  children,
}: EffectStageProps) => {
  const {fps} = useVideoConfig();
  const requests = [...profile.defaultEffects, ...(scene.effects || [])];
  let rendered: ReactNode = children;

  for (let index = requests.length - 1; index >= 0; index -= 1) {
    const effect = requests[index];
    const Component = effectRegistry[effect.kind];
    rendered = (
      <Component
        effect={effect}
        scene={scene}
        theme={theme}
        assets={assets}
        captions={captions}
        absoluteFrom={absoluteFrom}
        durationInFrames={durationInFrames}
      >
        {rendered}
      </Component>
    );
  }

  const transitionKind = scene.transition_out || profile.transitionDefault;
  const Transition = transitionRegistry[transitionKind];
  const showLowerThird =
    profile.lowerThirdEnabled &&
    profile.lowerThirdSceneTypes.includes(scene.scene_type) &&
    !requests.some((effect) => effect.kind === 'lower_third');

  return (
    <>
      {rendered}
      {showLowerThird ? <LowerThird scene={scene} theme={theme} /> : null}
      {isFirstScene ? (
        <IntroSting channelName={channelName} theme={theme} enabled={profile.introStingEnabled} />
      ) : null}
      <Transition kind={transitionKind} theme={theme} durationInFrames={durationInFrames} />
      {requests.map((effect, index) => {
        const sfxPath = effectString(effect, 'sfx_path', '');
        if (!sfxPath) return null;
        const from = Math.max(0, Math.round(effectNumber(effect, 'start_seconds', 0) * fps));
        const volume = Math.min(1, Math.max(0, effectNumber(effect, 'sfx_volume', 0.75)));
        return (
          <Sequence key={`${effect.kind}-sfx-${index}`} from={from}>
            <Audio src={staticFile(sfxPath)} volume={volume} />
          </Sequence>
        );
      })}
    </>
  );
};
