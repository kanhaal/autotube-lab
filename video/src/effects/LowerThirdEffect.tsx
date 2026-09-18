import {LowerThird} from './LowerThird';
import type {EffectComponentProps} from './types';
import {effectString} from './utils';

export type LowerThirdEffectProps = EffectComponentProps;

export const LowerThirdEffect = ({effect, children, scene, theme}: LowerThirdEffectProps) => (
  <>
    {children}
    <LowerThird scene={scene} theme={theme} label={effectString(effect, 'label', '') || undefined} />
  </>
);
