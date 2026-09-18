import {interpolate} from 'remotion';
import type {EffectRenderProps} from './types';
export type StatCountUpEffectProps=EffectRenderProps;
export const StatCountUpEffect=({effect,frame,durationInFrames,theme}:StatCountUpEffectProps)=>{
  const verified=Number(effect.verified_value??effect.final_value??0),finalValue=Number(effect.final_value??verified),end=Math.max(1,Math.min(durationInFrames-1,Number(effect.end_frame??durationInFrames*.72)));
  const value=interpolate(frame,[0,end],[0,finalValue],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
  return <div style={{position:'absolute',right:'7%',textAlign:'right',top:'12%',zIndex:26}}>
    <div style={{color:theme.accent,fontSize:82,fontWeight:950,letterSpacing:-4}}>{String(effect.prefix??'')}{Math.round(value).toLocaleString()}{String(effect.suffix??'')}</div>
    <div style={{fontSize:17,fontWeight:800,opacity:.6,textTransform:'uppercase'}}>verified metric</div>
  </div>;
};
