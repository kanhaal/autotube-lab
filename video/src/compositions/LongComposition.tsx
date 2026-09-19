import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';

import {EditorialCaptionTrack} from '../editor/EditorialCaptionTrack';
import {DirectedScene} from '../editor/DirectedScene';
import {IntroSting} from '../effects/IntroSting';
import {LowerThird} from '../effects/LowerThird';
import {SceneEffects, SceneTransitionOut} from '../effects/effectRegistry';
import {overlappedSceneWindow} from '../polish';
import type {
  AssetRecordV1,
  CaptionCueV1,
  RenderPackageV1,
  SceneSpecV1,
  TransitionOutKind,
} from '../types';
import type {ChannelTheme} from '../themes/types';
import {sceneFrameWindows} from './sceneTiming';

const SceneSequence = ({
  scene,
  theme,
  assets,
  durationInFrames,
  absoluteFrom,
  captions,
  defaultTransition,
  profile,
}: {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  assets: AssetRecordV1[];
  durationInFrames: number;
  absoluteFrom: number;
  captions: CaptionCueV1[];
  defaultTransition?: TransitionOutKind;
  profile?: RenderPackageV1['manifest']['render_effects'];
}) => (
  <>
    <SceneEffects
      scene={scene}
      theme={theme}
      assets={assets}
      captions={captions}
      durationInFrames={durationInFrames}
      absoluteFrom={absoluteFrom}
    >
      <DirectedScene
        scene={scene}
        theme={theme}
        assets={assets}
        captions={captions}
        durationInFrames={durationInFrames}
        absoluteFrom={absoluteFrom}
        format="long"
        profile={profile}
      />
    </SceneEffects>
    <SceneTransitionOut
      scene={scene}
      defaultTransition={defaultTransition}
      theme={theme}
      assets={assets}
      captions={captions}
      durationInFrames={durationInFrames}
      absoluteFrom={absoluteFrom}
    />
  </>
);

export const LongComposition = ({pkg, theme}: {pkg: RenderPackageV1; theme: ChannelTheme}) => {
  const windows = sceneFrameWindows(pkg);
  return (
    <AbsoluteFill
      style={{
        background: theme.background,
        color: theme.foreground,
        fontFamily: 'Arial, Helvetica, sans-serif',
      }}
    >
      {pkg.manifest.audio_path ? <Audio src={staticFile(pkg.manifest.audio_path)} /> : null}
      {pkg.manifest.render_effects?.intro_sting ? (
        <Sequence from={0} durationInFrames={Math.max(1, Math.round(pkg.manifest.fps * 0.72))}>
          <IntroSting channelName={pkg.manifest.channel_name} theme={theme} />
        </Sequence>
      ) : null}
      {pkg.manifest.render_effects?.lower_third ? (
        <Sequence
          from={Math.round(pkg.manifest.fps * 0.8)}
          durationInFrames={Math.max(1, Math.round(pkg.manifest.fps * 2.2))}
        >
          <LowerThird channelName={pkg.manifest.channel_name} label={pkg.manifest.title} theme={theme} />
        </Sequence>
      ) : null}
      {pkg.scenes.scenes.map((scene, index) => {
        const window = windows[index];
        if (!window) return null;
        const editWindow = overlappedSceneWindow(
          window,
          index,
          pkg.scenes.scenes.length,
          Math.max(6, Math.round(pkg.manifest.fps * 0.22)),
        );
        return (
          <Sequence key={scene.id} from={editWindow.from} durationInFrames={editWindow.durationInFrames}>
            <SceneSequence
              scene={scene}
              theme={theme}
              assets={pkg.assets.records}
              durationInFrames={editWindow.durationInFrames}
              absoluteFrom={editWindow.from}
              captions={pkg.captions.cues}
              defaultTransition={pkg.manifest.render_effects?.default_transition_out}
              profile={pkg.manifest.render_effects}
            />
          </Sequence>
        );
      })}
      <EditorialCaptionTrack cues={pkg.captions.cues} theme={theme} format="long" />
    </AbsoluteFill>
  );
};
