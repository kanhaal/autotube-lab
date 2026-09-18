import {AbsoluteFill, Composition} from 'remotion';

import {KernelRushLong} from './compositions/KernelRushLong';
import {KernelRushShort} from './compositions/KernelRushShort';
import {LobbySignalLong} from './compositions/LobbySignalLong';
import {LobbySignalShort} from './compositions/LobbySignalShort';
import {packageDurationFrames} from './compositions/sceneTiming';
import {shortDurationFrames, validateShortPackage} from './compositions/shortTiming';
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

type RenderInput = {pkg?: RenderPackageV1};

const longMetadata = (rawProps: unknown) => {
  const props = rawProps as RenderInput;
  return {
    durationInFrames: props.pkg ? packageDurationFrames(props.pkg) : 30,
    fps: props.pkg?.manifest.fps ?? 30,
    width: props.pkg?.manifest.width ?? 1920,
    height: props.pkg?.manifest.height ?? 1080,
  };
};

const shortMetadata = (rawProps: unknown) => {
  const props = rawProps as RenderInput;
  if (!props.pkg) {
    return {durationInFrames: 900, fps: 30, width: 1080, height: 1920};
  }
  validateShortPackage(props.pkg);
  return {
    durationInFrames: shortDurationFrames(props.pkg),
    fps: props.pkg.manifest.fps,
    width: 1080,
    height: 1920,
  };
};

const KernelRushEntry = ({pkg}: RenderInput) => (pkg ? <KernelRushLong pkg={pkg} /> : <Placeholder />);
const LobbySignalEntry = ({pkg}: RenderInput) => (pkg ? <LobbySignalLong pkg={pkg} /> : <Placeholder />);
const KernelRushShortEntry = ({pkg}: RenderInput) => (pkg ? <KernelRushShort pkg={pkg} /> : <Placeholder />);
const LobbySignalShortEntry = ({pkg}: RenderInput) => (pkg ? <LobbySignalShort pkg={pkg} /> : <Placeholder />);

export const RemotionRoot = () => (
  <>
    <Composition
      id="KernelRushLong"
      component={KernelRushEntry}
      durationInFrames={30}
      fps={30}
      width={1920}
      height={1080}
      calculateMetadata={({props}) => longMetadata(props)}
    />
    <Composition
      id="LobbySignalLong"
      component={LobbySignalEntry}
      durationInFrames={30}
      fps={30}
      width={1920}
      height={1080}
      calculateMetadata={({props}) => longMetadata(props)}
    />
    <Composition
      id="KernelRushShort"
      component={KernelRushShortEntry}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
      calculateMetadata={({props}) => shortMetadata(props)}
    />
    <Composition
      id="LobbySignalShort"
      component={LobbySignalShortEntry}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
      calculateMetadata={({props}) => shortMetadata(props)}
    />
  </>
);
