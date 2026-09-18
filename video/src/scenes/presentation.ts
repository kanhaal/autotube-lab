import type {CSSProperties} from 'react';
import {interpolate} from 'remotion';

import {motionStyle, transitionPreset} from '../motion';
import type {MotionName, TransitionName} from '../motion';
import type {AssetRecordV1, SceneSpecV1} from '../types';

const imageKinds = new Set([
  'image',
  'screenshot',
  'source_screenshot',
  'fallback_card',
  'fallback_editorial',
]);
const verifiedAssetSceneTypes = new Set(['source_browser', 'device', 'github', 'game_store']);

const dataString = (scene: SceneSpecV1, key: string): string => {
  const value = scene.data[key];
  return typeof value === 'string' ? value.trim() : '';
};

export const sceneSupportsVerifiedAsset = (scene: SceneSpecV1): boolean =>
  verifiedAssetSceneTypes.has(scene.scene_type);

export const resolveSceneAsset = (
  scene: SceneSpecV1,
  assets: AssetRecordV1[],
): AssetRecordV1 | undefined => {
  for (const id of scene.asset_ids) {
    const match = assets.find((asset) => asset.id === id && imageKinds.has(asset.kind));
    if (match) return match;
  }

  const sceneBound = assets.find(
    (asset) => asset.scene_id === scene.id && imageKinds.has(asset.kind),
  );
  if (sceneBound) return sceneBound;

  const sourceUrl = dataString(scene, 'source_url') || dataString(scene, 'url');
  if (sourceUrl) {
    const match = assets.find(
      (asset) => asset.source_url === sourceUrl && imageKinds.has(asset.kind),
    );
    if (match) return match;
  }

  return assets.find(
    (asset) => asset.usage === scene.purpose && imageKinds.has(asset.kind),
  );
};

const transitionStyle = (
  name: TransitionName,
  frame: number,
): CSSProperties => {
  const preset = transitionPreset(name);
  if (preset.durationFrames <= 0) return {};
  const progress = interpolate(
    frame,
    [0, preset.durationFrames],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );
  const eased = progress * progress * (3 - 2 * progress);
  switch (name) {
    case 'crossfade':
      return {
        filter: `blur(${((1 - eased) * 7).toFixed(2)}px)`,
        opacity: eased,
        transform: `scale(${(0.985 + eased * 0.015).toFixed(4)})`,
      };
    case 'wipe': {
      const edge = Math.min(112, eased * 112);
      const lowerEdge = Math.max(0, edge - 10);
      return {
        clipPath: `polygon(0 0, ${edge}% 0, ${lowerEdge}% 100%, 0 100%)`,
        filter: `blur(${((1 - eased) * 2.4).toFixed(2)}px)`,
      };
    }
    case 'slide':
      return {
        filter: `blur(${((1 - eased) * 4).toFixed(2)}px)`,
        opacity: eased,
        transform:
          `perspective(1400px) translate3d(${((1 - eased) * 110).toFixed(2)}px,0,0) ` +
          `scale(${(0.975 + eased * 0.025).toFixed(4)}) rotateY(${((1 - eased) * -2.2).toFixed(2)}deg)`,
      };
    case 'stinger':
      return {
        filter: `blur(${((1 - eased) * 5).toFixed(2)}px) brightness(${(1.18 - eased * 0.18).toFixed(3)})`,
        opacity: eased,
        transform: `scale(${(0.92 + eased * 0.08).toFixed(4)}) rotateZ(${((1 - eased) * -0.8).toFixed(2)}deg)`,
      };
    case 'cut':
    default:
      return {};
  }
};

const numericOpacity = (value: CSSProperties['opacity']): number =>
  typeof value === 'number' ? value : 1;

export const scenePresentationStyle = (
  scene: SceneSpecV1,
  frame: number,
  fps: number,
): CSSProperties => {
  const transition = transitionStyle(scene.transition as TransitionName, frame);
  const motion = motionStyle(scene.motion as MotionName, frame, fps);
  const transforms = [transition.transform, motion.transform]
    .filter((value): value is string => typeof value === 'string' && value.length > 0)
    .join(' ');
  const style: CSSProperties = {...transition, ...motion};
  if (transition.opacity !== undefined || motion.opacity !== undefined) {
    style.opacity = numericOpacity(transition.opacity) * numericOpacity(motion.opacity);
  }
  if (transforms) style.transform = transforms;
  return style;
};
