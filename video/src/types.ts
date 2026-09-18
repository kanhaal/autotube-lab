export type RenderFormat = 'long' | 'short';
export type ScenePlanFormat = 'longform' | 'short';

export type CompositionId =
  | 'KernelRushLong'
  | 'LobbySignalLong'
  | 'KernelRushShort'
  | 'LobbySignalShort';

export type SceneEffectKind =
  | 'auto_zoom'
  | 'spotlight_dim'
  | 'cursor_smooth'
  | 'code_typewriter'
  | 'stat_count_up'
  | 'split_compare'
  | 'speed_ramp'
  | 'scroll_reveal'
  | 'tier_list'
  | 'vs_screen'
  | 'ticker_overlay'
  | 'meme_flash'
  | 'freeze_frame'
  | 'kinetic_word_reveal'
  | 'kinetic_infographic'
  | 'progress_reveal'
  | 'icon_morph'
  | 'tag_pop'
  | 'parallax_layers'
  | 'grid_reveal'
  | 'card_flip'
  | 'underline_sweep'
  | 'leader_line'
  | 'waveform_overlay'
  | 'chromatic_pulse'
  | 'light_leak'
  | 'film_grain'
  | 'vignette_pulse'
  | 'rack_focus'
  | 'particle_burst'
  | 'screen_shake'
  | 'scanline_flicker'
  | 'duotone_flash'
  | 'lower_third'
  | 'intro_sting'
  | 'chapter_card';

export type TransitionOutV1 = 'glitch_rgb_split' | 'whoosh_zoom';

export type SceneEffectRequestV1 = {
  kind: SceneEffectKind;
  [key: string]: unknown;
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
  effects?: SceneEffectRequestV1[];
  transition_out?: TransitionOutV1 | null;
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
