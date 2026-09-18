import type {CSSProperties} from 'react';
import type {EffectRenderProps} from './types';
import {eased,normalizedProgress} from './math';

export type AutoZoomEffectProps=EffectRenderProps;
export const autoZoomTransform=({effect,frame,durationInFrames}:AutoZoomEffectProps):CSSProperties=>{
  const start=Number(effect.start_frame??0);
  const end=Number(effect.end_frame??Math.max(1,durationInFrames-1));
  const requested=Number(effect.scale??1.18);
  const scale=Math.max(1.1,Math.min(1.3,requested));
  const p=eased(normalizedProgress(frame,start,end));
  const target=(effect.target??{}) as Record<string,unknown>;
  const x=Number(target.x??.5),y=Number(target.y??.5);
  return {transform:`scale(${(1+(scale-1)*p).toFixed(4)}) translate3d(${((.5-x)*8*p).toFixed(3)}%,${((.5-y)*8*p).toFixed(3)}%,0)`,transformOrigin:`${x*100}% ${y*100}%`};
};
export const AutoZoomEffect=()=>null;
