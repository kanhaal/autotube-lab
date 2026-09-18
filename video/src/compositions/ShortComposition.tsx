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
import {validateShortPackage} from './shortTiming';

const VerticalShot = ({
  scene,
  theme,
  assets,
  captions,
  durationInFrames,
  absoluteFrom,
  defaultTransition,
}: {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  assets: AssetRecordV1[];
  captions: CaptionCueV1[];
  durationInFrames: number;
  absoluteFrom: number;
  defaultTransition?: TransitionOutKind;
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
        format="short"
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

export const ShortComposition = ({
  pkg,
  theme,
}: {
  pkg: RenderPackageV1;
  theme: ChannelTheme;
}) => {
  validateShortPackage(pkg);
  const windows = sceneFrameWindows(pkg);

  return (
    <AbsoluteFill
      style={{
        background: theme.background,
        color: theme.foreground,
        fontFamily: 'Arial, Helvetica, sans-serif',
        overflow: 'hidden',
      }}
    >
      {pkg.manifest.audio_path ? <Audio src={staticFile(pkg.manifest.audio_path)} /> : null}
      {pkg.manifest.render_effects?.intro_sting ? (
        <Sequence from={0} durationInFrames={Math.max(1, Math.round(pkg.manifest.fps * 0.55))}>
          <IntroSting channelName={pkg.manifest.channel_name} theme={theme} />
        </Sequence>
      ) : null}
      {pkg.manifest.render_effects?.lower_third ? (
        <Sequence
          from={Math.round(pkg.manifest.fps * 0.65)}
          durationInFrames={Math.max(1, Math.round(pkg.manifest.fps * 1.55))}
        >
          <LowerThird
            channelName={pkg.manifest.channel_name}
            label={pkg.manifest.title}
            theme={theme}
          />
        </Sequence>
      ) : null}
      {pkg.scenes.scenes.map((scene, index) => {
        const window = windows[index];
        if (!window) return null;
        const editWindow = overlappedSceneWindow(
          window,
          index,
          pkg.scenes.scenes.length,
          Math.max(5, Math.round(pkg.manifest.fps * 0.18)),
        );
        return (
          <Sequence
            key={scene.id}
            from={editWindow.from}
            durationInFrames={editWindow.durationInFrames}
          >
            <VerticalShot
              scene={scene}
              theme={theme}
              assets={pkg.assets.records}
              captions={pkg.captions.cues}
              durationInFrames={editWindow.durationInFrames}
              absoluteFrom={editWindow.from}
              defaultTransition={pkg.manifest.render_effects?.default_transition_out}
            />
          </Sequence>
        );
      })}
      <EditorialCaptionTrack cues={pkg.captions.cues} theme={theme} format="short" />
    </AbsoluteFill>
  );
};
