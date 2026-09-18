import type {CaptionCueV1, RenderPackageV1} from '../types';

export type SceneFrameWindow = {
  from: number;
  durationInFrames: number;
};

type TimedWord = {
  token: string;
  end: number;
};

const tokenize = (text: string): string[] =>
  text
    .toLowerCase()
    .split(/\s+/)
    .map((word) => word.replace(/[^a-z0-9']/g, ''))
    .filter(Boolean);

const wordCount = (text: string): number => tokenize(text).length;

export const packageDurationFrames = (pkg: RenderPackageV1): number => {
  const fps = Math.max(1, pkg.manifest.fps || 30);
  const captionEnd = pkg.captions.cues.reduce((latest, cue) => Math.max(latest, cue.end), 0);
  const audioDuration = Number.isFinite(pkg.manifest.duration_seconds)
    ? Math.max(0, pkg.manifest.duration_seconds ?? 0)
    : 0;
  const timedDuration = Math.max(audioDuration, captionEnd);
  if (timedDuration > 0) return Math.max(1, Math.round(timedDuration * fps));
  const narrationWords = pkg.scenes.scenes.reduce((total, scene) => total + Math.max(1, wordCount(scene.narration)), 0);
  return Math.max(fps, Math.round((narrationWords / 2.5) * fps));
};

const cueTimedWords = (cue: CaptionCueV1): TimedWord[] => {
  if (cue.word_timings?.length) {
    return cue.word_timings
      .map((word) => ({token: tokenize(word.text)[0] ?? '', end: word.end}))
      .filter((word) => word.token && Number.isFinite(word.end));
  }

  const words = cue.words.length ? cue.words : cue.text.trim().split(/\s+/).filter(Boolean);
  if (!words.length || cue.end <= cue.start) return [];
  const duration = cue.end - cue.start;
  return words
    .map((word, index) => ({
      token: tokenize(word)[0] ?? '',
      end: cue.start + duration * ((index + 1) / words.length),
    }))
    .filter((word) => word.token);
};

const alignedWords = (pkg: RenderPackageV1): TimedWord[] =>
  pkg.captions.cues.flatMap(cueTimedWords);

const exactSceneEnd = (words: TimedWord[], tokens: string[], cursor: number): number | undefined => {
  if (!tokens.length) return undefined;
  for (let start = cursor; start <= words.length - tokens.length; start += 1) {
    const matches = tokens.every((token, offset) => words[start + offset]?.token === token);
    if (matches) return start + tokens.length - 1;
  }
  return undefined;
};

const fuzzySceneEnd = (words: TimedWord[], tokens: string[], cursor: number): number | undefined => {
  if (!tokens.length) return undefined;
  let transcriptIndex = cursor;
  let matched = 0;
  let lastMatched = -1;

  for (const token of tokens) {
    const stop = Math.min(words.length, transcriptIndex + 4);
    let found = -1;
    for (let probe = transcriptIndex; probe < stop; probe += 1) {
      if (words[probe].token === token) {
        found = probe;
        break;
      }
    }
    if (found >= 0) {
      matched += 1;
      lastMatched = found;
      transcriptIndex = found + 1;
    }
  }

  return matched / tokens.length >= 0.8 && lastMatched >= cursor ? lastMatched : undefined;
};

const sceneEndWord = (words: TimedWord[], narration: string, cursor: number): number | undefined => {
  const tokens = tokenize(narration);
  return exactSceneEnd(words, tokens, cursor) ?? fuzzySceneEnd(words, tokens, cursor);
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

  const words = alignedWords(pkg);
  if (!words.length) return proportionalWindows(pkg);

  const fps = Math.max(1, pkg.manifest.fps || 30);
  const totalFrames = packageDurationFrames(pkg);
  let wordCursor = 0;
  let previousFrame = 0;

  return scenes.map((scene, index) => {
    const from = previousFrame;
    let next: number;
    if (index === scenes.length - 1) {
      next = totalFrames;
    } else {
      const tokens = tokenize(scene.narration);
      const matchedEnd = sceneEndWord(words, scene.narration, wordCursor);
      const fallbackEnd = Math.min(
        words.length - 1,
        wordCursor + Math.max(1, tokens.length) - 1,
      );
      const endIndex = matchedEnd ?? fallbackEnd;
      wordCursor = Math.min(words.length, endIndex + 1);
      next = Math.round(words[endIndex].end * fps);
      next = Math.min(totalFrames, Math.max(from + 1, next));
    }
    previousFrame = next;
    return {from, durationInFrames: Math.max(1, next - from)};
  });
};
