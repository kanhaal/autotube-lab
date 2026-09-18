import type {AssetRecordV1, SceneEffectRequestV1} from '../types';
import type {TargetBox} from './types';

export const clamp = (value: number, min: number, max: number): number =>
  Math.min(max, Math.max(min, value));

export const smoothstep = (value: number): number => {
  const t = clamp(value, 0, 1);
  return t * t * (3 - 2 * t);
};

export const effectNumber = (
  effect: SceneEffectRequestV1,
  key: string,
  fallback: number,
): number => {
  const value = effect[key];
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
};

export const effectString = (
  effect: SceneEffectRequestV1,
  key: string,
  fallback = '',
): string => {
  const value = effect[key];
  return typeof value === 'string' ? value : fallback;
};

export const effectStringList = (effect: SceneEffectRequestV1, key: string): string[] => {
  const value = effect[key];
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : [];
};

export const effectBox = (
  effect: SceneEffectRequestV1,
  key = 'target',
  fallback: TargetBox = {x: 0.25, y: 0.25, width: 0.5, height: 0.5},
): TargetBox => {
  const value = effect[key];
  if (!value || typeof value !== 'object') return fallback;
  const candidate = value as Record<string, unknown>;
  const number = (name: keyof TargetBox, defaultValue: number) => {
    const raw = candidate[name];
    return typeof raw === 'number' && Number.isFinite(raw)
      ? clamp(raw, 0, 1)
      : defaultValue;
  };
  const x = number('x', fallback.x);
  const y = number('y', fallback.y);
  const width = clamp(number('width', fallback.width), 0.02, 1 - x);
  const height = clamp(number('height', fallback.height), 0.02, 1 - y);
  return {x, y, width, height};
};

export const sceneAsset = (
  effect: SceneEffectRequestV1,
  assets: AssetRecordV1[],
): AssetRecordV1 | undefined => {
  const requested = effectString(effect, 'asset_id');
  return assets.find((asset) => asset.id === requested);
};

export const frameProgress = (
  frame: number,
  fps: number,
  startSeconds: number,
  durationSeconds: number,
): number => {
  const start = Math.round(startSeconds * fps);
  const duration = Math.max(1, Math.round(durationSeconds * fps));
  return clamp((frame - start) / duration, 0, 1);
};
