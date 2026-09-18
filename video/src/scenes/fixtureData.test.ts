import {describe, expect, it} from 'vitest';

import {chartPointsForScene, timelineItemsForScene} from './SceneRenderer';
import type {SceneSpecV1} from '../types';

const baseScene: SceneSpecV1 = {
  id: 'fixture',
  narration: 'Synthetic narration.',
  purpose: 'explain',
  scene_type: 'chart',
  headline: 'Synthetic data',
  subheadline: '',
  source_ids: [],
  asset_ids: [],
  motion: 'none',
  emphasis: [],
  transition: 'cut',
  fallback_scene_type: 'fallback_editorial',
  data: {},
};

describe('fixture-compatible scene data', () => {
  it('renders chart labels and values emitted by the Python planner fixtures', () => {
    const scene = {
      ...baseScene,
      data: {labels: ['A', 'B', 'C', 'D'], values: [42, 34, 25, 18]},
    };

    expect(chartPointsForScene(scene)).toEqual([
      {label: 'A', value: 42},
      {label: 'B', value: 34},
      {label: 'C', value: 25},
      {label: 'D', value: 18},
    ]);
  });

  it('renders timeline string items emitted by the Python planner fixtures', () => {
    const scene = {
      ...baseScene,
      scene_type: 'timeline',
      data: {items: ['Baseline', 'Scheduler change', 'Validation', 'Final pass']},
    };

    expect(timelineItemsForScene(scene)).toEqual([
      {label: 'Baseline'},
      {label: 'Scheduler change'},
      {label: 'Validation'},
      {label: 'Final pass'},
    ]);
  });
});
