import {IntroSting} from './IntroSting';
import type {EffectComponentProps} from './types';
import {effectString} from './utils';

export type IntroStingEffectProps = EffectComponentProps;

export const IntroStingEffect = ({effect, children, theme}: IntroStingEffectProps) => (
  <>
    {children}
    <IntroSting
      channelName={effectString(effect, 'channel_name', 'SIGNAL')}
      theme={theme}
      enabled
    />
  </>
);
