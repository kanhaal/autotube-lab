import {Img, OffthreadVideo, staticFile} from 'remotion';

import type {AssetRecordV1, SceneSpecV1} from '../types';

const videoExtensions = new Set(['.mp4', '.mov', '.webm', '.mkv', '.m4v']);

const extension = (value: string) => {
  const clean = value.split('?')[0].toLowerCase();
  const dot = clean.lastIndexOf('.');
  return dot >= 0 ? clean.slice(dot) : '';
};

export const isVideoAsset = (asset: AssetRecordV1) =>
  /video|clip|gameplay|b-roll|broll/i.test(asset.kind) ||
  videoExtensions.has(extension(asset.local_path));

export const resolveEditorialMedia = (
  scene: SceneSpecV1,
  assets: AssetRecordV1[],
): AssetRecordV1 | undefined => {
  for (const id of scene.asset_ids) {
    const direct = assets.find((asset) => asset.id === id);
    if (direct) return direct;
  }

  const bound = assets.find((asset) => asset.scene_id === scene.id);
  if (bound) return bound;

  const sourceUrl = String(scene.data.source_url ?? scene.data.url ?? '').trim();
  if (sourceUrl) {
    const matchingUrl = assets.find((asset) => asset.source_url === sourceUrl);
    if (matchingUrl) return matchingUrl;
  }

  return assets.find((asset) => asset.usage === scene.purpose);
};

export const EditorialMedia = ({
  asset,
  style,
}: {
  asset: AssetRecordV1;
  style?: React.CSSProperties;
}) => {
  const common: React.CSSProperties = {
    height: '100%',
    objectFit: 'cover',
    width: '100%',
    ...style,
  };
  if (isVideoAsset(asset)) {
    return <OffthreadVideo src={staticFile(asset.local_path)} muted style={common} />;
  }
  return <Img src={staticFile(asset.local_path)} style={common} />;
};
