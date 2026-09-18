export type RenderFormat = 'long' | 'short';
export type ScenePlanFormat = 'longform' | 'short';

export type CompositionId =
  | 'KernelRushLong'
  | 'LobbySignalLong'
  | 'KernelRushShort'
  | 'LobbySignalShort'
  | 'KernelRushIntroSting'
  | 'LobbySignalIntroSting';

export type TransitionOutKind =
  | 'glitch_rgb_split'
  | 'whoosh_zoom'
  | 'whip_pan'
  | 'match_cut'
  | 'smash_cut'
  | 'cross_dissolve'
  | 'liquid_displacement';

export type ShotStyle =
  | 'source_full'
  | 'source_detail'
  | 'kinetic_text'
  | 'data_full'
  | 'graphic_3d'
  | 'split_screen'
  | 'chapter'
  | 'editorial';

export type CameraPreset =
  | 'locked'
  | 'dolly_in'
  | 'dolly_out'
  | 'orbit_left'
  | 'orbit_right'
  | 'whip_pan'
  | 'handheld_micro'
  | 'rack_push'
  | 'crane_down';

export type CameraDirectionV1 = {
  preset?: CameraPreset;
  intensity?: number;
  target?: {x?: number; y?: number};
};

export type MicroBeatV1 = {
  at: number;
  kind: 'focus_punch' | 'callout' | 'tag_pop' | 'underline' | 'flash' | 'shake' | 'crop_shift';
  [key: string]: unknown;
};

export type AudioCueV1 = {
  at: number;
  kind: 'whoosh' | 'impact' | 'click' | 'riser' | 'braam' | 'ding' | 'glitch' | 'static';
  volume?: number;
};

export type SceneEffectV1 = {
  kind: string;
  [key: string]: unknown;
};

export type RenderEffectsProfileV1 = {
  panel_style?: string;
  default_transition_out?: TransitionOutKind;
  intro_sting?: boolean;
  lower_third?: boolean;
  texture?: string;
};

export type RenderManifestV1 = {
  schema_version: '1';
  format: RenderFormat;
  channel_id: string;
  channel_name: string;
  title: string;
  width: number;
  height: number;
  fps: number;
  duration_source: 'audio';
  duration_seconds?: number;
  audio_path: string;
  theme: Record<string, unknown>;
  render_effects?: RenderEffectsProfileV1;
};

export type ScriptPayload = {
  title: string;
  script: string;
};

export type SceneSpecV1 = {
  id: string;
  narration: string;
  purpose: string;
  scene_type: string;
  headline: string;
  subheadline: string;
  source_ids: string[];
  asset_ids: string[];
  motion: string;
  emphasis: string[];
  transition: string;
  fallback_scene_type: string;
  data: Record<string, unknown>;
  effects?: SceneEffectV1[];
  transition_out?: TransitionOutKind | null;
  shot_style?: ShotStyle | null;
  camera?: CameraDirectionV1;
  micro_beats?: MicroBeatV1[];
  audio_cues?: AudioCueV1[];
};

export type ScenePlanV1 = {
  schema_version: '1';
  channel_id: string;
  format: ScenePlanFormat;
  scenes: SceneSpecV1[];
};

export type CaptionWordTimingV1 = {
  text: string;
  start: number;
  end: number;
};

export type CaptionCueV1 = {
  start: number;
  end: number;
  text: string;
  words: string[];
  word_timings?: CaptionWordTimingV1[];
};

export type CaptionPayloadV1 = {
  schema_version: '1';
  cues: CaptionCueV1[];
};

export type AssetRecordV1 = {
  id: string;
  kind: string;
  local_path: string;
  source_url: string | null;
  source_name: string | null;
  usage: string;
  license_note: string | null;
  sha256: string;
  captured_at: string;
  scene_id?: string | null;
};

export type AssetManifestV1 = {
  schema_version: '1';
  records: AssetRecordV1[];
};

export type RenderPackageV1 = {
  root: string;
  manifest: RenderManifestV1;
  script: ScriptPayload;
  scenes: ScenePlanV1;
  captions: CaptionPayloadV1;
  assets: AssetManifestV1;
};
