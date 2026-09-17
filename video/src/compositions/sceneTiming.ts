import type {RenderPackageV1} from '../types';

export type SceneFrameWindow = {
  from: number;
  durationInFrames: number;
};

const wordCount = (text: string): number => text.trim().split(/\s+/).filter(Boolean).length;

export const packageDurationFrames = (pkg: RenderPackageV1): number => {
  const fps = Math.max(1, pkg.manifest.fps || 30);
  const captionEnd = pkg.captions.cues.reduce((latest, cue) => Math.max(latest, cue.end), 0);
  if (captionEnd > 0) return Math.max(1, Math.round(captionEnd * fps));
  const narrationWords = pkg.scenes.scenes.reduce((total, scene) => total + Math.max(1, wordCount(scene.narration)), 0);
  return Math.max(fps, Math.round((narrationWords / 2.5) * fps));
};

export const sceneFrameWindows = (pkg: RenderPackageV1): SceneFrameWindow[] => {
  const scenes = pkg.scenes.scenes;
  if (!scenes.length) return [];

  const totalFrames = packageDurationFrames(pkg);
  const weights = scenes.map((scene) => Math.max(1, wordCount(scene.narration)));
  const totalWeight = weights.reduce((sum, weight) => sum + weight, 0);
  let cumulativeWeight = 0;

  return scenes.map((_, index) => {
    const from = Math.round((cumulativeWeight / totalWeight) * totalFrames);
    cumulativeWeight += weights[index];
    const next = index === scenes.length - 1
      ? totalFrames
      : Math.round((cumulativeWeight / totalWeight) * totalFrames);
    return {from, durationInFrames: Math.max(1, next - from)};
  });
};
