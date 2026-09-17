import type {RenderPackageV1} from '../types';
import {packageDurationFrames} from './sceneTiming';

export const validateShortPackage = (pkg: RenderPackageV1): void => {
  if (pkg.manifest.format !== 'short' || pkg.scenes.format !== 'short') {
    throw new Error('Short render package must declare the short format');
  }
  if (pkg.manifest.width !== 1080 || pkg.manifest.height !== 1920) {
    throw new Error('Short render package must use native 1080x1920 dimensions');
  }
  const sceneCount = pkg.scenes.scenes.length;
  if (sceneCount < 5 || sceneCount > 12) {
    throw new Error('Short render package must contain 5-12 semantic scenes');
  }

  const fps = Math.max(1, pkg.manifest.fps || 30);
  const durationSeconds = packageDurationFrames(pkg) / fps;
  if (durationSeconds < 30 || durationSeconds > 45) {
    throw new Error('Short render package duration must stay within 30-45 seconds');
  }
};

export const shortDurationFrames = (pkg: RenderPackageV1): number => {
  validateShortPackage(pkg);
  return packageDurationFrames(pkg);
};
