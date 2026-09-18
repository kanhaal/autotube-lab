import type {RenderPackageV1, SceneEffectRequestV1, TransitionOutV1} from '../types';

export type ChannelEffectProfile = {
  transitionDefault: TransitionOutV1;
  introStingEnabled: boolean;
  lowerThirdEnabled: boolean;
  lowerThirdSceneTypes: string[];
  defaultEffects: SceneEffectRequestV1[];
};

const asRecord = (value: unknown): Record<string, unknown> =>
  value && typeof value === 'object' ? (value as Record<string, unknown>) : {};

export const resolveChannelEffectProfile = (pkg: RenderPackageV1): ChannelEffectProfile => {
  const config = asRecord(pkg.manifest.theme.effects);
  const transition = config.transition_default;
  const rawDefaults = Array.isArray(config.default_effects) ? config.default_effects : [];
  const defaultEffects = rawDefaults.filter(
    (item): item is SceneEffectRequestV1 =>
      Boolean(item) && typeof item === 'object' && typeof (item as Record<string, unknown>).kind === 'string',
  );
  const sceneTypes = Array.isArray(config.lower_third_scene_types)
    ? config.lower_third_scene_types.filter((item): item is string => typeof item === 'string')
    : [];

  return {
    transitionDefault: transition === 'glitch_rgb_split' ? 'glitch_rgb_split' : 'whoosh_zoom',
    introStingEnabled: config.intro_sting_enabled !== false,
    lowerThirdEnabled: config.lower_third_enabled !== false,
    lowerThirdSceneTypes: sceneTypes,
    defaultEffects,
  };
};
