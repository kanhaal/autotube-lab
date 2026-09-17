export type RenderFormat = 'long' | 'short';
export type ScenePlanFormat = 'longform' | 'short';

export type CompositionId =
  | 'KernelRushLong'
  | 'LobbySignalLong'
  | 'KernelRushShort'
  | 'LobbySignalShort';

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
};

export type ScenePlanV1 = {
  schema_version: '1';
  channel_id: string;
  format: ScenePlanFormat;
  scenes: SceneSpecV1[];
};

export type CaptionCueV1 = {
  start: number;
  end: number;
  text: string;
  words: string[];
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
