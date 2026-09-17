import {AbsoluteFill, Composition} from 'remotion';

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

export const RemotionRoot = () => (
  <>
    <Composition
      id="KernelRushLong"
      component={Placeholder}
      durationInFrames={30}
      fps={30}
      width={1920}
      height={1080}
    />
    <Composition
      id="LobbySignalLong"
      component={Placeholder}
      durationInFrames={30}
      fps={30}
      width={1920}
      height={1080}
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
