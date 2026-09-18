import type {ComponentType} from 'react';

import type {SceneEffectKind, SceneSpecV1, TransitionOutV1} from '../types';
import {AutoZoomEffect} from './AutoZoomEffect';
import {CardFlipEffect} from './CardFlipEffect';
import {ChapterCard} from './ChapterCard';
import {ChromaticPulseEffect} from './ChromaticPulseEffect';
import {CodeTypewriterEffect} from './CodeTypewriterEffect';
import {CursorSmoothEffect} from './CursorSmoothEffect';
import {DuotoneFlashEffect} from './DuotoneFlashEffect';
import {FilmGrainEffect} from './FilmGrainEffect';
import {FreezeFrameEffect} from './FreezeFrameEffect';
import {GridRevealEffect} from './GridRevealEffect';
import {IconMorphEffect} from './IconMorphEffect';
import {IntroStingEffect} from './IntroStingEffect';
import {KineticInfographicEffect} from './KineticInfographicEffect';
import {KineticWordReveal} from './KineticWordReveal';
import {LeaderLineEffect} from './LeaderLineEffect';
import {LightLeakEffect} from './LightLeakEffect';
import {LowerThirdEffect} from './LowerThirdEffect';
import {MemeFlashEffect, clampMemeFlashSeconds} from './MemeFlashEffect';
import {ParallaxLayersEffect} from './ParallaxLayersEffect';
import {ParticleBurstEffect} from './ParticleBurstEffect';
import {ProgressRevealEffect} from './ProgressRevealEffect';
import {RackFocusEffect} from './RackFocusEffect';
import {ScanlineFlickerEffect} from './ScanlineFlickerEffect';
import {ScreenShakeEffect} from './ScreenShakeEffect';
import {ScrollRevealEffect} from './ScrollRevealEffect';
import {SpeedRampEffect, speedRampPlaybackRate} from './SpeedRampEffect';
import {SplitCompareEffect} from './SplitCompareEffect';
import {SpotlightDimEffect} from './SpotlightDimEffect';
import {StatCountUpEffect} from './StatCountUpEffect';
import {TagPopEffect} from './TagPopEffect';
import {TickerOverlayEffect} from './TickerOverlayEffect';
import {TierListEffect} from './TierListEffect';
import type {EffectComponentProps, TransitionComponentProps} from './types';
import {UnderlineSweepEffect} from './UnderlineSweepEffect';
import {VignettePulseEffect} from './VignettePulseEffect';
import {VsScreenEffect} from './VsScreenEffect';
import {WaveformOverlayEffect} from './WaveformOverlayEffect';
import {GlitchRgbSplitTransition} from './GlitchRgbSplitTransition';
import {WhooshZoomTransition} from './WhooshZoomTransition';

export {clampMemeFlashSeconds};

export const sceneHasEffect = (scene: SceneSpecV1, kind: SceneEffectKind): boolean =>
  Boolean(scene.effects?.some((effect) => effect.kind === kind));

export const mediaPlaybackRateForScene = (
  scene: SceneSpecV1,
  frame: number,
  fps: number,
): number => {
  const effect = scene.effects?.find((candidate) => candidate.kind === 'speed_ramp');
  return effect ? speedRampPlaybackRate(frame, fps, effect) : 1;
};

export const CORE_EFFECT_KINDS: readonly SceneEffectKind[] = [
  'auto_zoom',
  'spotlight_dim',
  'cursor_smooth',
  'code_typewriter',
  'stat_count_up',
  'split_compare',
  'speed_ramp',
  'scroll_reveal',
  'tier_list',
  'vs_screen',
  'ticker_overlay',
  'meme_flash',
  'freeze_frame',
  'kinetic_word_reveal',
  'kinetic_infographic',
  'progress_reveal',
  'icon_morph',
  'tag_pop',
  'parallax_layers',
  'grid_reveal',
  'card_flip',
  'underline_sweep',
  'leader_line',
  'waveform_overlay',
  'chromatic_pulse',
  'light_leak',
  'film_grain',
  'vignette_pulse',
  'rack_focus',
  'particle_burst',
  'screen_shake',
  'scanline_flicker',
  'duotone_flash',
  'lower_third',
  'intro_sting',
  'chapter_card',
] as const;

type RegisteredEffect = ComponentType<EffectComponentProps>;
type RegisteredTransition = ComponentType<TransitionComponentProps>;

export const effectRegistry: Record<SceneEffectKind, RegisteredEffect> = {
  auto_zoom: AutoZoomEffect,
  spotlight_dim: SpotlightDimEffect,
  cursor_smooth: CursorSmoothEffect,
  code_typewriter: CodeTypewriterEffect,
  stat_count_up: StatCountUpEffect,
  split_compare: SplitCompareEffect,
  speed_ramp: SpeedRampEffect,
  scroll_reveal: ScrollRevealEffect,
  tier_list: TierListEffect,
  vs_screen: VsScreenEffect,
  ticker_overlay: TickerOverlayEffect,
  meme_flash: MemeFlashEffect,
  freeze_frame: FreezeFrameEffect,
  kinetic_word_reveal: KineticWordReveal,
  kinetic_infographic: KineticInfographicEffect,
  progress_reveal: ProgressRevealEffect,
  icon_morph: IconMorphEffect,
  tag_pop: TagPopEffect,
  parallax_layers: ParallaxLayersEffect,
  grid_reveal: GridRevealEffect,
  card_flip: CardFlipEffect,
  underline_sweep: UnderlineSweepEffect,
  leader_line: LeaderLineEffect,
  waveform_overlay: WaveformOverlayEffect,
  chromatic_pulse: ChromaticPulseEffect,
  light_leak: LightLeakEffect,
  film_grain: FilmGrainEffect,
  vignette_pulse: VignettePulseEffect,
  rack_focus: RackFocusEffect,
  particle_burst: ParticleBurstEffect,
  screen_shake: ScreenShakeEffect,
  scanline_flicker: ScanlineFlickerEffect,
  duotone_flash: DuotoneFlashEffect,
  lower_third: LowerThirdEffect,
  intro_sting: IntroStingEffect,
  chapter_card: ChapterCard,
};

export const transitionRegistry: Record<TransitionOutV1, RegisteredTransition> = {
  glitch_rgb_split: GlitchRgbSplitTransition,
  whoosh_zoom: WhooshZoomTransition,
};
