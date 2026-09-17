import type {RenderPackageV1} from '../types';
import {kernelrushTheme} from '../themes/kernelrush';
import {EnhancedShortComposition} from './EnhancedShortComposition';

export const KERNELRUSH_SHORT_THEME_ID = kernelrushTheme.id;

export const KernelRushShort = ({pkg}: {pkg: RenderPackageV1}) => (
  <EnhancedShortComposition pkg={pkg} theme={kernelrushTheme} />
);
