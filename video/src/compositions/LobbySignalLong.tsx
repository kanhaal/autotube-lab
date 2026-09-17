import type {RenderPackageV1} from '../types';
import {lobbysignalTheme} from '../themes/lobbysignal';
import {LongComposition} from './LongComposition';

export const LOBBYSIGNAL_LONG_THEME_ID = lobbysignalTheme.id;

export const LobbySignalLong = ({pkg}: {pkg: RenderPackageV1}) => (
  <LongComposition pkg={pkg} theme={lobbysignalTheme} />
);
