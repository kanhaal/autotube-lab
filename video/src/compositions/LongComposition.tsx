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
import {narrationEmphasisBeat, sourceMediaStyle, TransitionAccent} from '../vfx';
import {
  resolveSceneAsset,
  scenePresentationStyle,
  sceneSupportsVerifiedAsset,
} from '../scenes/presentation';
import type {AssetRecordV1, CaptionCueV1, RenderPackageV1, SceneSpecV1} from '../types';
import type {ChannelTheme} from '../themes/types';
import {sceneFrameWindows} from './sceneTiming';

const SceneSequence = ({
  scene,
  theme,
  assets,
  durationInFrames,
  absoluteFrom,
  captions,
}: {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  assets: AssetRecordV1[];
  durationInFrames: number;
  absoluteFrom: number;
  captions: CaptionCueV1[];
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sourceAsset = sceneSupportsVerifiedAsset(scene)
    ? resolveSceneAsset(scene, assets)
    : undefined;
  const presentation = scenePresentationStyle(scene, frame, fps);
  const envelope = sceneEnvelope(frame, durationInFrames, Math.max(6, Math.round(fps * 0.24)));
  const mediaStyle = sourceMediaStyle(frame, durationInFrames, fps, theme.motionIntensity * 0.72);
  const scanProgress = Math.max(0, Math.min(1, frame / Math.max(1, durationInFrames - 1)));
  const narrationBeat = narrationEmphasisBeat(
    captions,
    (absoluteFrom + frame) / Math.max(1, fps),
    scene.emphasis,
  );

  return (
    <AbsoluteFill
      style={{
        ...presentation,
        opacity: (typeof presentation.opacity === 'number' ? presentation.opacity : 1) * envelope,
      }}
    >
      <SceneRenderer
        scene={scene}
        theme={theme}
        assets={assets}
        durationInFrames={durationInFrames}
        narrationBeat={narrationBeat}
      />
      {sourceAsset ? (
        <div
          style={{
            background: '#0A0D12',
            border: `1px solid ${theme.border}`,
            borderRadius: 26,
            bottom: 145,
            boxShadow: `0 42px 120px rgba(0,0,0,0.54), 0 0 0 1px ${theme.accent}20, inset 0 1px 0 rgba(255,255,255,.08)`,
            left: '50.5%',
            overflow: 'hidden',
            perspective: 1500,
            position: 'absolute',
            right: 105,
            top: 145,
            transform: `rotateY(${theme.transitionFamily === 'snap' ? -1.1 : -0.55}deg) rotateX(0.35deg)`,
            transformOrigin: 'center center',
          }}
        >
          <Img
            src={staticFile(sourceAsset.local_path)}
            style={{
              ...mediaStyle,
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'top center',
              width: '100%',
            }}
          />
          <div
            style={{
              background: `linear-gradient(90deg, transparent, ${theme.accent}99, rgba(255,255,255,.72), ${theme.secondary}88, transparent)`,
              boxShadow: `0 0 28px ${theme.accent}55`,
              height: 2,
              left: 0,
              opacity: 0.34,
              position: 'absolute',
              right: 0,
              top: `${8 + scanProgress * 78}%`,
              transform: 'translateZ(0)',
            }}
          />
          <div
            style={{
              border: `1px solid ${theme.accent}40`,
              borderBottom: 0,
              borderRight: 0,
              height: 46,
              left: 18,
              position: 'absolute',
              top: 18,
              width: 46,
            }}
          />
          <div
            style={{
              border: `1px solid ${theme.secondary}44`,
              borderLeft: 0,
              borderTop: 0,
              bottom: 18,
              height: 46,
              position: 'absolute',
              right: 18,
              width: 46,
            }}
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
      <TransitionAccent theme={theme} durationInFrames={durationInFrames} />
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
              absoluteFrom={editWindow.from}
              captions={pkg.captions.cues}
            />
          </Sequence>
        );
      })}
      <CaptionTrack cues={pkg.captions.cues} accent={theme.accent} energetic={theme.motionIntensity > 1} />
    </AbsoluteFill>
  );
};
