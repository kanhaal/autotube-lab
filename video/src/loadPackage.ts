import {readFile} from 'node:fs/promises';
import {join, resolve} from 'node:path';

import type {
  AssetManifestV1,
  CaptionPayloadV1,
  RenderManifestV1,
  RenderPackageV1,
  ScenePlanV1,
  ScriptPayload,
} from './types';

const readJson = async <T>(root: string, name: string): Promise<T> => {
  const raw = await readFile(join(root, name), 'utf8');
  return JSON.parse(raw) as T;
};

const requireSchemaV1 = (value: {schema_version?: string}, label: string) => {
  if (value.schema_version !== '1') {
    throw new Error(`Unsupported ${label} schema version: ${String(value.schema_version)}`);
  }
};

export const loadRenderPackage = async (packageDir: string): Promise<RenderPackageV1> => {
  const root = resolve(packageDir);
  const [manifest, script, scenes, captions, assets] = await Promise.all([
    readJson<RenderManifestV1>(root, 'manifest.json'),
    readJson<ScriptPayload>(root, 'script.json'),
    readJson<ScenePlanV1>(root, 'scenes.json'),
    readJson<CaptionPayloadV1>(root, 'captions.json'),
    readJson<AssetManifestV1>(root, 'asset-manifest.json'),
  ]);

  requireSchemaV1(manifest, 'render package');
  requireSchemaV1(scenes, 'scene plan');
  requireSchemaV1(captions, 'caption');
  requireSchemaV1(assets, 'asset manifest');

  return {root, manifest, script, scenes, captions, assets};
};
