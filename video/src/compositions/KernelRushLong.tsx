import type {RenderPackageV1} from '../types';
import {kernelrushTheme} from '../themes/kernelrush';
import {LongComposition} from './LongComposition';

export const KERNELRUSH_LONG_THEME_ID = kernelrushTheme.id;

export const KernelRushLong = ({pkg}: {pkg: RenderPackageV1}) => (
  <LongComposition pkg={pkg} theme={kernelrushTheme} />
);
