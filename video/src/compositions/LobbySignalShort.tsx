import type {RenderPackageV1} from '../types';
import {lobbysignalTheme} from '../themes/lobbysignal';
import {EnhancedShortComposition} from './EnhancedShortComposition';

export const LOBBYSIGNAL_SHORT_THEME_ID = lobbysignalTheme.id;

export const LobbySignalShort = ({pkg}: {pkg: RenderPackageV1}) => (
  <EnhancedShortComposition pkg={pkg} theme={lobbysignalTheme} />
);
