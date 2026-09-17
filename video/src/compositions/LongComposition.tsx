import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';

import {CaptionTrack} from '../components/CaptionTrack';
import {SceneRenderer} from '../scenes/SceneRenderer';
import type {RenderPackageV1} from '../types';
import type {ChannelTheme} from '../themes/types';
import {sceneFrameWindows} from './sceneTiming';

export const LongComposition = ({pkg, theme}: {pkg: RenderPackageV1; theme: ChannelTheme}) => {
  const windows = sceneFrameWindows(pkg);
  return (
    <AbsoluteFill style={{background: theme.background, color: theme.foreground, fontFamily: 'Inter, Arial, sans-serif'}}>
      {pkg.manifest.audio_path ? <Audio src={staticFile(pkg.manifest.audio_path)} /> : null}
      {pkg.scenes.scenes.map((scene, index) => {
        const window = windows[index];
        if (!window) return null;
        return (
          <Sequence key={scene.id} from={window.from} durationInFrames={window.durationInFrames}>
            <SceneRenderer scene={scene} theme={theme} assets={pkg.assets.records} />
          </Sequence>
        );
      })}
      <CaptionTrack cues={pkg.captions.cues} accent={theme.accent} energetic={theme.motionIntensity > 1} />
    </AbsoluteFill>
  );
};
