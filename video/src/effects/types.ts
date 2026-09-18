import type {CSSProperties,ReactNode} from 'react';
import type {AssetRecordV1,CaptionCueV1,SceneEffectV1,SceneSpecV1,TransitionOutKind} from '../types';
import type {ChannelTheme} from '../themes/types';

export type BoundingBox={x:number;y:number;width:number;height:number};
export type EffectKind=
  |'auto_zoom'|'spotlight_dim'|'cursor_smooth'|'code_typewriter'|'stat_count_up'
  |'split_compare'|'speed_ramp'|'scroll_reveal'|'tier_list'|'vs_screen'|'ticker_overlay'
  |'meme_flash'|'freeze_frame'|'kinetic_word_reveal'|'kinetic_infographic'|'progress_reveal'
  |'tag_pop'|'parallax_layers'|'grid_reveal'|'card_flip'|'underline_sweep'|'callout_leader_line'
  |'waveform_overlay'|'chromatic_pulse'|'film_grain'|'vignette_pulse'|'rack_focus'
  |'screen_shake'|'scanline_flicker'|'duotone_flash';

export type EffectRenderProps={
  effect:SceneEffectV1;scene:SceneSpecV1;theme:ChannelTheme;assets:AssetRecordV1[];
  captions:CaptionCueV1[];frame:number;fps:number;durationInFrames:number;absoluteFrame:number;
};
export type EffectDefinition={
  component?:React.ComponentType<EffectRenderProps>;
  transform?:(props:EffectRenderProps)=>CSSProperties;
  wrap?:(children:ReactNode,props:EffectRenderProps)=>ReactNode;
};
export type {TransitionOutKind};
