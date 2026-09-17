import type {RenderPackageV1} from '../types';
import {lobbysignalTheme} from '../themes/lobbysignal';
import {ShortComposition} from './ShortComposition';

export const LOBBYSIGNAL_SHORT_THEME_ID = lobbysignalTheme.id;

export const LobbySignalShort = ({pkg}: {pkg: RenderPackageV1}) => (
  <ShortComposition pkg={pkg} theme={lobbysignalTheme} />
);
