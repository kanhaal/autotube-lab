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

const alignedWordEnds = (pkg: RenderPackageV1): number[] => {
  const ends: number[] = [];
  for (const cue of pkg.captions.cues) {
    const words = cue.words.length ? cue.words : cue.text.trim().split(/\s+/).filter(Boolean);
    if (!words.length || cue.end <= cue.start) continue;
    const duration = cue.end - cue.start;
    for (let index = 0; index < words.length; index += 1) {
      ends.push(cue.start + duration * ((index + 1) / words.length));
    }
  }
  return ends;
};

const proportionalWindows = (pkg: RenderPackageV1): SceneFrameWindow[] => {
  const scenes = pkg.scenes.scenes;
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

export const sceneFrameWindows = (pkg: RenderPackageV1): SceneFrameWindow[] => {
  const scenes = pkg.scenes.scenes;
  if (!scenes.length) return [];

  const wordEnds = alignedWordEnds(pkg);
  if (!wordEnds.length) return proportionalWindows(pkg);

  const fps = Math.max(1, pkg.manifest.fps || 30);
  const totalFrames = packageDurationFrames(pkg);
  const sceneWords = scenes.map((scene) => Math.max(1, wordCount(scene.narration)));
  const totalSceneWords = sceneWords.reduce((sum, count) => sum + count, 0);
  let cumulativeSceneWords = 0;
  let previousFrame = 0;

  return scenes.map((_, index) => {
    const from = previousFrame;
    cumulativeSceneWords += sceneWords[index];
    let next: number;
    if (index === scenes.length - 1) {
      next = totalFrames;
    } else {
      const fraction = cumulativeSceneWords / totalSceneWords;
      const wordIndex = Math.min(
        wordEnds.length - 1,
        Math.max(0, Math.round(fraction * wordEnds.length) - 1),
      );
      next = Math.round(wordEnds[wordIndex] * fps);
      next = Math.min(totalFrames, Math.max(from + 1, next));
    }
    previousFrame = next;
    return {from, durationInFrames: Math.max(1, next - from)};
  });
};
