import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';

import {resolveSceneAsset, scenePresentationStyle} from '../scenes/presentation';
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
  const index = windows.findIndex(
    (window) => frame >= window.from && frame < window.from + window.durationInFrames,
  );
  if (index < 0) return undefined;
  const scene = pkg.scenes.scenes[index];
  const window = windows[index];
  const localFrame = Math.max(0, frame - window.from);
  return {
    scene,
    asset: scene.scene_type === 'source_browser'
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
        borderRadius: 30,
        bottom: 500,
        boxShadow: '0 26px 72px rgba(0,0,0,0.46)',
        left: 86,
        overflow: 'hidden',
        position: 'absolute',
        right: 146,
        top: 780,
      }}
    >
      <Img
        src={staticFile(visual.asset.local_path)}
        style={{height: '100%', objectFit: 'cover', objectPosition: 'top center', width: '100%'}}
      />
      <div
        style={{
          background: 'linear-gradient(transparent, rgba(0,0,0,0.78))',
          bottom: 0,
          color: '#FFFFFF',
          fontSize: 19,
          left: 0,
          padding: '48px 22px 18px',
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
      {visual?.scene.scene_type === 'source_browser' ? (
        <SourceOverlay visual={visual} theme={theme} />
      ) : null}
    </AbsoluteFill>
  );
};
