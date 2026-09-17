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
}: {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  assets: AssetRecordV1[];
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sourceAsset = sceneSupportsVerifiedAsset(scene)
    ? resolveSceneAsset(scene, assets)
    : undefined;

  return (
    <AbsoluteFill style={scenePresentationStyle(scene, frame, fps)}>
      <SceneRenderer scene={scene} theme={theme} assets={assets} />
      {sourceAsset ? (
        <div
          style={{
            background: '#0A0D12',
            border: `1px solid ${theme.border}`,
            borderRadius: 26,
            bottom: 105,
            boxShadow: '0 28px 70px rgba(0,0,0,0.42)',
            left: 150,
            overflow: 'hidden',
            position: 'absolute',
            right: 150,
            top: 360,
          }}
        >
          <Img
            src={staticFile(sourceAsset.local_path)}
            style={{height: '100%', objectFit: 'cover', objectPosition: 'top center', width: '100%'}}
          />
          <div
            style={{
              background: 'linear-gradient(transparent, rgba(0,0,0,0.75))',
              bottom: 0,
              color: '#FFFFFF',
              fontSize: 18,
              left: 0,
              padding: '48px 24px 18px',
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
    <AbsoluteFill style={{background: theme.background, color: theme.foreground, fontFamily: 'Inter, Arial, sans-serif'}}>
      {pkg.manifest.audio_path ? <Audio src={staticFile(pkg.manifest.audio_path)} /> : null}
      {pkg.scenes.scenes.map((scene, index) => {
        const window = windows[index];
        if (!window) return null;
        return (
          <Sequence key={scene.id} from={window.from} durationInFrames={window.durationInFrames}>
            <SceneSequence scene={scene} theme={theme} assets={pkg.assets.records} />
          </Sequence>
        );
      })}
      <CaptionTrack cues={pkg.captions.cues} accent={theme.accent} energetic={theme.motionIntensity > 1} />
    </AbsoluteFill>
  );
};
