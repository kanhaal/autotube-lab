import {AbsoluteFill, Composition} from 'remotion';

import {KernelRushLong} from './compositions/KernelRushLong';
import {LobbySignalLong} from './compositions/LobbySignalLong';
import type {RenderPackageV1} from './types';

const Placeholder = () => (
  <AbsoluteFill
    style={{
      alignItems: 'center',
      backgroundColor: '#05070D',
      color: '#FFFFFF',
      display: 'flex',
      fontFamily: 'Inter, Arial, sans-serif',
      fontSize: 64,
      justifyContent: 'center',
    }}
  >
    AutoTube Professional Renderer
  </AbsoluteFill>
);

type LongInput = {pkg?: RenderPackageV1};

const packageDurationFrames = (pkg: RenderPackageV1 | undefined): number => {
  if (!pkg) return 30;
  const fps = Math.max(1, pkg.manifest.fps || 30);
  const cueEnd = pkg.captions.cues.reduce((latest, cue) => Math.max(latest, cue.end), 0);
  return Math.max(1, Math.ceil(Math.max(cueEnd, 1) * fps));
};

const KernelRushEntry = ({pkg}: LongInput) => (pkg ? <KernelRushLong pkg={pkg} /> : <Placeholder />);
const LobbySignalEntry = ({pkg}: LongInput) => (pkg ? <LobbySignalLong pkg={pkg} /> : <Placeholder />);

export const RemotionRoot = () => (
  <>
    <Composition
      id="KernelRushLong"
      component={KernelRushEntry}
      durationInFrames={30}
      fps={30}
      width={1920}
      height={1080}
      calculateMetadata={({props}) => ({
        durationInFrames: packageDurationFrames(props.pkg),
        fps: props.pkg?.manifest.fps ?? 30,
        width: props.pkg?.manifest.width ?? 1920,
        height: props.pkg?.manifest.height ?? 1080,
      })}
    />
    <Composition
      id="LobbySignalLong"
      component={LobbySignalEntry}
      durationInFrames={30}
      fps={30}
      width={1920}
      height={1080}
      calculateMetadata={({props}) => ({
        durationInFrames: packageDurationFrames(props.pkg),
        fps: props.pkg?.manifest.fps ?? 30,
        width: props.pkg?.manifest.width ?? 1920,
        height: props.pkg?.manifest.height ?? 1080,
      })}
    />
    <Composition
      id="KernelRushShort"
      component={Placeholder}
      durationInFrames={30}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="LobbySignalShort"
      component={Placeholder}
      durationInFrames={30}
      fps={30}
      width={1080}
      height={1920}
    />
  </>
);
