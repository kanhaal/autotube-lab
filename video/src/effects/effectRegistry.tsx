import type {CSSProperties,ReactNode} from 'react';
import {useCurrentFrame,useVideoConfig} from 'remotion';

import type {AssetRecordV1,CaptionCueV1,SceneSpecV1,TransitionOutKind} from '../types';
import type {ChannelTheme} from '../themes/types';
import {AutoZoomEffect,autoZoomTransform} from './AutoZoomEffect';
import {SpotlightDimEffect} from './SpotlightDimEffect';
import {CursorSmoothEffect} from './CursorSmoothEffect';
import {CodeTypewriterEffect} from './CodeTypewriterEffect';
import {StatCountUpEffect} from './StatCountUpEffect';
import {SplitCompareEffect} from './SplitCompareEffect';
import {SpeedRampEffect} from './SpeedRampEffect';
import {ScrollRevealEffect} from './ScrollRevealEffect';
import {TierListEffect} from './TierListEffect';
import {VsScreenEffect} from './VsScreenEffect';
import {TickerOverlayEffect} from './TickerOverlayEffect';
import {MemeFlashEffect,memeFlashDurationFrames} from './MemeFlashEffect';
import {FreezeFrameEffect,freezeFrameWrap} from './FreezeFrameEffect';
import {KineticWordReveal} from './KineticWordReveal';
import {GlitchRgbSplitTransition} from './GlitchRgbSplitTransition';
import {WhooshZoomTransition} from './WhooshZoomTransition';
import {
  CalloutLeaderLine,CardFlip,ChromaticPulse,DuotoneFlash,FilmGrain,GridReveal,
  KineticInfographic,ProgressReveal,ScanlineFlicker,TagPop,UnderlineSweep,VignettePulse,
  WaveformOverlay,parallaxTransform,rackFocusTransform,screenShakeTransform,
} from './ExtraEffects';
import type {EffectDefinition,EffectKind,EffectRenderProps} from './types';

export const EFFECT_KINDS:readonly EffectKind[]=[
  'auto_zoom','spotlight_dim','cursor_smooth','code_typewriter','stat_count_up','split_compare',
  'speed_ramp','scroll_reveal','tier_list','vs_screen','ticker_overlay','meme_flash','freeze_frame',
  'kinetic_word_reveal','kinetic_infographic','progress_reveal','tag_pop','parallax_layers','grid_reveal',
  'card_flip','underline_sweep','callout_leader_line','waveform_overlay','chromatic_pulse','film_grain',
  'vignette_pulse','rack_focus','screen_shake','scanline_flicker','duotone_flash',
];

export const effectRegistry:Record<EffectKind,EffectDefinition>={
  auto_zoom:{component:AutoZoomEffect,transform:autoZoomTransform},
  spotlight_dim:{component:SpotlightDimEffect},
  cursor_smooth:{component:CursorSmoothEffect},
  code_typewriter:{component:CodeTypewriterEffect},
  stat_count_up:{component:StatCountUpEffect},
  split_compare:{component:SplitCompareEffect},
  speed_ramp:{component:SpeedRampEffect},
  scroll_reveal:{component:ScrollRevealEffect},
  tier_list:{component:TierListEffect},
  vs_screen:{component:VsScreenEffect},
  ticker_overlay:{component:TickerOverlayEffect},
  meme_flash:{component:MemeFlashEffect},
  freeze_frame:{component:FreezeFrameEffect,wrap:freezeFrameWrap},
  kinetic_word_reveal:{component:KineticWordReveal},
  kinetic_infographic:{component:KineticInfographic},
  progress_reveal:{component:ProgressReveal},
  tag_pop:{component:TagPop},
  parallax_layers:{transform:parallaxTransform},
  grid_reveal:{component:GridReveal},
  card_flip:{component:CardFlip},
  underline_sweep:{component:UnderlineSweep},
  callout_leader_line:{component:CalloutLeaderLine},
  waveform_overlay:{component:WaveformOverlay},
  chromatic_pulse:{component:ChromaticPulse},
  film_grain:{component:FilmGrain},
  vignette_pulse:{component:VignettePulse},
  rack_focus:{transform:rackFocusTransform},
  screen_shake:{transform:screenShakeTransform},
  scanline_flicker:{component:ScanlineFlicker},
  duotone_flash:{component:DuotoneFlash},
};

export const transitionRegistry:Record<TransitionOutKind,React.ComponentType<EffectRenderProps>>={
  glitch_rgb_split:GlitchRgbSplitTransition,
  whoosh_zoom:WhooshZoomTransition,
};

const mergeStyles=(styles:CSSProperties[]):CSSProperties=>{
  const transforms=styles.map(style=>style.transform).filter(Boolean).join(' ');
  const filters=styles.map(style=>style.filter).filter(Boolean).join(' ');
  return Object.assign({},...styles,{transform:transforms||undefined,filter:filters||undefined});
};

export const SceneEffects=({scene,theme,assets,captions,durationInFrames,absoluteFrom,children}:{
  scene:SceneSpecV1;theme:ChannelTheme;assets:AssetRecordV1[];captions:CaptionCueV1[];
  durationInFrames:number;absoluteFrom:number;children:ReactNode;
})=>{
  const frame=useCurrentFrame();const {fps}=useVideoConfig();
  const effects=(scene.effects??[]).filter(effect=>EFFECT_KINDS.includes(effect.kind as EffectKind));
  const propsFor=(effect:(typeof effects)[number]):EffectRenderProps=>({effect,scene,theme,assets,captions,frame,fps,durationInFrames,absoluteFrame:absoluteFrom+frame});
  const styles=effects.map(effect=>effectRegistry[effect.kind as EffectKind]?.transform?.(propsFor(effect))).filter(Boolean) as CSSProperties[];
  let content:ReactNode=<div style={{height:'100%',position:'relative',width:'100%',...mergeStyles(styles)}}>{children}</div>;
  for(const effect of [...effects].reverse()){const def=effectRegistry[effect.kind as EffectKind];if(def.wrap)content=def.wrap(content,propsFor(effect));}
  return <>{content}{effects.map((effect,index)=>{const Component=effectRegistry[effect.kind as EffectKind]?.component;return Component?<Component key={`${effect.kind}-${index}`} {...propsFor(effect)}/>:null;})}</>;
};

export const SceneTransitionOut=({scene,defaultTransition,theme,assets,captions,durationInFrames,absoluteFrom}:{
  scene:SceneSpecV1;defaultTransition?:TransitionOutKind;theme:ChannelTheme;assets:AssetRecordV1[];
  captions:CaptionCueV1[];durationInFrames:number;absoluteFrom:number;
})=>{
  const frame=useCurrentFrame();const {fps}=useVideoConfig();const kind=scene.transition_out??defaultTransition;
  if(!kind)return null;
  const Component=transitionRegistry[kind];
  return <Component effect={{kind}} scene={scene} theme={theme} assets={assets} captions={captions} frame={frame} fps={fps} durationInFrames={durationInFrames} absoluteFrame={absoluteFrom+frame}/>;
};

export {memeFlashDurationFrames};
