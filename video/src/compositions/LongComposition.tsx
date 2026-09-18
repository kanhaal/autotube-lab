import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

import {CaptionTrack} from '../components/CaptionTrack';
import {overlappedSceneWindow, sceneEnvelope} from '../polish';
import {SceneRenderer} from '../scenes/SceneRenderer';
import {
  resolveSceneAsset,
  scenePresentationStyle,
  sceneSupportsVerifiedAsset,
} from '../scenes/presentation';
import type {AssetRecordV1, RenderPackageV1, SceneSpecV1} from '../types';
import type {ChannelTheme} from '../themes/types';
import {sceneFrameWindows} from './sceneTiming';

const SceneSequence = ({
  scene,
  theme,
  assets,
  durationInFrames,
}: {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  assets: AssetRecordV1[];
  durationInFrames: number;
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sourceAsset = sceneSupportsVerifiedAsset(scene)
    ? resolveSceneAsset(scene, assets)
    : undefined;
  const presentation = scenePresentationStyle(scene, frame, fps);
  const envelope = sceneEnvelope(frame, durationInFrames, Math.max(6, Math.round(fps * 0.24)));

  return (
    <AbsoluteFill
      style={{
        ...presentation,
        opacity: (typeof presentation.opacity === 'number' ? presentation.opacity : 1) * envelope,
      }}
    >
      <SceneRenderer scene={scene} theme={theme} assets={assets} />
      {sourceAsset ? (
        <div
          style={{
            background: '#0A0D12',
            border: `1px solid ${theme.border}`,
            borderRadius: 26,
            bottom: 145,
            boxShadow: `0 34px 100px rgba(0,0,0,0.48), 0 0 0 1px ${theme.accent}12`,
            left: '50.5%',
            overflow: 'hidden',
            position: 'absolute',
            right: 105,
            top: 145,
          }}
        >
          <Img
            src={staticFile(sourceAsset.local_path)}
            style={{height: '100%', objectFit: 'cover', objectPosition: 'top center', transform: 'scale(1.015)', width: '100%'}}
          />
          <div
            style={{
              background: 'linear-gradient(transparent, rgba(0,0,0,0.75))',
              bottom: 0,
              color: '#FFFFFF',
              fontFamily: 'Arial, Helvetica, sans-serif',
              fontSize: 18,
              fontWeight: 700,
              left: 0,
              padding: '68px 26px 20px',
              position: 'absolute',
              right: 0,
            }}
          >
            {sourceAsset.source_name || sourceAsset.source_url || 'Verified source'}
          </div>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

export const LongComposition = ({pkg, theme}: {pkg: RenderPackageV1; theme: ChannelTheme}) => {
  const windows = sceneFrameWindows(pkg);
  return (
    <AbsoluteFill style={{background: theme.background, color: theme.foreground, fontFamily: 'Arial, Helvetica, sans-serif'}}>
      {pkg.manifest.audio_path ? <Audio src={staticFile(pkg.manifest.audio_path)} /> : null}
      {pkg.scenes.scenes.map((scene, index) => {
        const window = windows[index];
        if (!window) return null;
        const editWindow = overlappedSceneWindow(
          window,
          index,
          pkg.scenes.scenes.length,
          Math.max(8, Math.round(pkg.manifest.fps * 0.3)),
        );
        return (
          <Sequence key={scene.id} from={editWindow.from} durationInFrames={editWindow.durationInFrames}>
            <SceneSequence
              scene={scene}
              theme={theme}
              assets={pkg.assets.records}
              durationInFrames={editWindow.durationInFrames}
            />
          </Sequence>
        );
      })}
      <CaptionTrack cues={pkg.captions.cues} accent={theme.accent} energetic={theme.motionIntensity > 1} />
    </AbsoluteFill>
  );
};
