import {IntroSting} from '../effects/IntroSting';
import {kernelrushTheme} from '../themes/kernelrush';
import {lobbysignalTheme} from '../themes/lobbysignal';

export const KernelRushIntroSting = () => (
  <IntroSting channelName="KernelRush" theme={kernelrushTheme} />
);

export const LobbySignalIntroSting = () => (
  <IntroSting channelName="LobbySignal" theme={lobbysignalTheme} />
);
