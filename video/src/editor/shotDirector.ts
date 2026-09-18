import type {SceneSpecV1, ShotStyle} from '../types';

const SOURCE_SCENES = new Set(['source_browser', 'github', 'game_store', 'device']);
const DATA_SCENES = new Set(['stat', 'chart', 'timeline', 'map']);
const SPLIT_SCENES = new Set(['comparison', 'before_after']);
const TEXT_SCENES = new Set(['hook', 'headline', 'quote', 'conclusion']);

export const resolveShotStyle = (scene: SceneSpecV1): ShotStyle => {
  if (scene.shot_style) return scene.shot_style;
  if (SOURCE_SCENES.has(scene.scene_type)) return 'source_full';
  if (DATA_SCENES.has(scene.scene_type)) return 'data_full';
  if (SPLIT_SCENES.has(scene.scene_type)) return 'split_screen';
  if (TEXT_SCENES.has(scene.scene_type)) return 'kinetic_text';
  if (scene.scene_type === 'chapter') return 'chapter';
  if (scene.scene_type === 'code' || scene.scene_type === 'process') return 'graphic_3d';
  return 'editorial';
};
