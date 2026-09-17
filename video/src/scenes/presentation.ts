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
  switch (name) {
    case 'crossfade':
      return {opacity: progress};
    case 'wipe':
      return {clipPath: `inset(0 ${(1 - progress) * 100}% 0 0)`};
    case 'slide':
      return {opacity: progress, transform: `translateX(${(1 - progress) * 90}px)`};
    case 'stinger':
      return {opacity: progress, transform: `scale(${0.96 + progress * 0.04})`};
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
