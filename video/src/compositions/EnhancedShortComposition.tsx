import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';

import {overlappedSceneWindow} from '../polish';
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
  };
};

const SourceOverlay = ({visual, theme}: {visual: ActiveShortVisual; theme: ChannelTheme}) => {
  if (!visual.asset) return null;
  return (
    <div
      style={{
        ...visual.style,
        background: '#090C12',
        border: `1px solid ${theme.border}`,
        borderRadius: 38,
        bottom: 430,
        boxShadow: `0 34px 100px rgba(0,0,0,0.52), 0 0 0 1px ${theme.accent}18`,
        left: 64,
        overflow: 'hidden',
        position: 'absolute',
        right: 64,
        top: 650,
      }}
    >
      <Img
        src={staticFile(visual.asset.local_path)}
        style={{height: '100%', objectFit: 'cover', objectPosition: 'top center', transform: 'scale(1.02)', width: '100%'}}
      />
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
