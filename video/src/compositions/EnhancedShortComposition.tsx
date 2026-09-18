import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

import {overlappedSceneWindow} from '../polish';
import {sourceMediaStyle} from '../vfx';
import {
  resolveSceneAsset,
  scenePresentationStyle,
  sceneSupportsVerifiedAsset,
} from '../scenes/presentation';
import type {AssetRecordV1, RenderPackageV1, SceneSpecV1} from '../types';
import type {ChannelTheme} from '../themes/types';
import {ShortComposition} from './ShortComposition';
import {sceneFrameWindows} from './sceneTiming';

export type ActiveShortVisual = {
  scene: SceneSpecV1;
  asset?: AssetRecordV1;
  style: React.CSSProperties;
  localFrame: number;
  durationInFrames: number;
};

export const activeShortVisual = (
  pkg: RenderPackageV1,
  frame: number,
): ActiveShortVisual | undefined => {
  const windows = sceneFrameWindows(pkg);
  const editWindows = windows.map((window, index) =>
    overlappedSceneWindow(
      window,
      index,
      windows.length,
      Math.max(8, Math.round((pkg.manifest.fps || 30) * 0.28)),
    ),
  );
  let index = -1;
  for (let candidate = 0; candidate < editWindows.length; candidate += 1) {
    const window = editWindows[candidate];
    if (frame >= window.from && frame < window.from + window.durationInFrames) {
      index = candidate;
    }
  }
  if (index < 0) return undefined;
  const scene = pkg.scenes.scenes[index];
  const window = editWindows[index];
  const localFrame = Math.max(0, frame - window.from);
  return {
    scene,
    asset: sceneSupportsVerifiedAsset(scene)
      ? resolveSceneAsset(scene, pkg.assets.records)
      : undefined,
    style: scenePresentationStyle(scene, localFrame, Math.max(1, pkg.manifest.fps || 30)),
    localFrame,
    durationInFrames: window.durationInFrames,
  };
};

const SourceOverlay = ({visual, theme}: {visual: ActiveShortVisual; theme: ChannelTheme}) => {
  const {fps} = useVideoConfig();
  if (!visual.asset) return null;
  const mediaStyle = sourceMediaStyle(
    visual.localFrame,
    visual.durationInFrames,
    fps,
    theme.motionIntensity * 0.82,
  );
  const scanProgress = Math.max(
    0,
    Math.min(1, visual.localFrame / Math.max(1, visual.durationInFrames - 1)),
  );
  return (
    <div
      style={{
        ...visual.style,
        background: '#090C12',
        border: `1px solid ${theme.border}`,
        borderRadius: 38,
        bottom: 430,
        boxShadow: `0 42px 130px rgba(0,0,0,0.58), 0 0 0 1px ${theme.accent}28, inset 0 1px 0 rgba(255,255,255,.10)`,
        left: 58,
        overflow: 'hidden',
        perspective: 1400,
        position: 'absolute',
        right: 58,
        top: 625,
        transformOrigin: 'center center',
      }}
    >
      <Img
        src={staticFile(visual.asset.local_path)}
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
          background: `linear-gradient(90deg, transparent, ${theme.accent}AA, rgba(255,255,255,.82), ${theme.secondary}99, transparent)`,
          boxShadow: `0 0 32px ${theme.accent}55`,
          height: 3,
          left: 0,
          opacity: 0.42,
          position: 'absolute',
          right: 0,
          top: `${10 + scanProgress * 76}%`,
        }}
      />
      <div
        style={{
          alignItems: 'center',
          backdropFilter: 'blur(18px)',
          background: 'rgba(4,7,12,.58)',
          border: `1px solid ${theme.border}`,
          borderRadius: 999,
          color: theme.accent,
          display: 'flex',
          fontFamily: 'Arial, Helvetica, sans-serif',
          fontSize: 18,
          fontWeight: 900,
          gap: 10,
          left: 22,
          letterSpacing: 1.6,
          padding: '10px 14px',
          position: 'absolute',
          textTransform: 'uppercase',
          top: 22,
        }}
      >
        <span
          style={{
            background: theme.accent,
            borderRadius: 99,
            boxShadow: `0 0 18px ${theme.accent}`,
            height: 9,
            width: 9,
          }}
        />
        source capture
      </div>
      <div
        style={{
          background: 'linear-gradient(transparent, rgba(0,0,0,0.78))',
          bottom: 0,
          color: '#FFFFFF',
          fontFamily: 'Arial, Helvetica, sans-serif',
          fontSize: 21,
          fontWeight: 800,
          left: 0,
          padding: '76px 26px 22px',
          position: 'absolute',
          right: 0,
        }}
      >
        {visual.asset.source_name || visual.asset.source_url || 'Verified source'}
      </div>
    </div>
  );
};

export const EnhancedShortComposition = ({
  pkg,
  theme,
}: {
  pkg: RenderPackageV1;
  theme: ChannelTheme;
}) => {
  const frame = useCurrentFrame();
  const visual = activeShortVisual(pkg, frame);
  return (
    <AbsoluteFill>
      <ShortComposition pkg={pkg} theme={theme} />
      {visual?.asset ? <SourceOverlay visual={visual} theme={theme} /> : null}
    </AbsoluteFill>
  );
};
