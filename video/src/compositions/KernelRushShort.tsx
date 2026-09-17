import type {RenderPackageV1} from '../types';
import {kernelrushTheme} from '../themes/kernelrush';
import {ShortComposition} from './ShortComposition';

export const KERNELRUSH_SHORT_THEME_ID = kernelrushTheme.id;

export const KernelRushShort = ({pkg}: {pkg: RenderPackageV1}) => (
  <ShortComposition pkg={pkg} theme={kernelrushTheme} />
);
