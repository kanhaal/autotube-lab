import {mkdtemp, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {describe, expect, it} from 'vitest';

import {loadRenderPackage} from './loadPackage';

const writeJson = async (root: string, name: string, value: unknown) => {
  await writeFile(join(root, name), JSON.stringify(value), 'utf8');
};

const fixture = async (schemaVersion = '1') => {
  const root = await mkdtemp(join(tmpdir(), 'autotube-render-package-'));
  await writeJson(root, 'manifest.json', {
    schema_version: schemaVersion,
    format: 'long',
    channel_id: 'kernelrush',
    channel_name: 'KernelRush',
    title: 'A launch story',
    width: 1920,
    height: 1080,
    fps: 30,
    duration_source: 'audio',
    audio_path: 'audio/narration.wav',
    theme: {background: '#050A14', accent: '#67F5C5'},
  });
  await writeJson(root, 'script.json', {title: 'A launch story', script: 'Verified narration.'});
  await writeJson(root, 'scenes.json', {
    schema_version: '1',
    channel_id: 'kernelrush',
    format: 'longform',
    scenes: [{
      id: 'scene-1', narration: 'Verified narration.', purpose: 'hook', scene_type: 'headline',
      headline: 'A launch story', subheadline: '', source_ids: [], asset_ids: [], motion: 'fade',
      emphasis: [], transition: 'cut', fallback_scene_type: 'fallback_editorial', data: {},
    }],
  });
  await writeJson(root, 'captions.json', {
    schema_version: '1',
    cues: [{start: 0, end: 1.5, text: 'Verified narration.', words: ['Verified', 'narration.']}],
  });
  await writeJson(root, 'asset-manifest.json', {schema_version: '1', records: []});
  return root;
};

describe('loadRenderPackage', () => {
  it('loads a schema-v1 package into one typed object', async () => {
    const root = await fixture();
    const result = await loadRenderPackage(root);

    expect(result.manifest.channel_id).toBe('kernelrush');
    expect(result.script.script).toBe('Verified narration.');
    expect(result.scenes.scenes).toHaveLength(1);
    expect(result.captions.cues[0].end).toBe(1.5);
    expect(result.assets.records).toEqual([]);
  });

  it('rejects unsupported package schema versions', async () => {
    const root = await fixture('2');
    await expect(loadRenderPackage(root)).rejects.toThrow(/schema version/i);
  });
});
