import type {EffectRenderProps} from './types';
import {eased,normalizedProgress} from './math';
export type SplitCompareEffectProps=EffectRenderProps;
export const SplitCompareEffect=({effect,frame,durationInFrames,theme}:SplitCompareEffectProps)=>{
  const p=eased(normalizedProgress(frame,0,Math.max(1,durationInFrames*.45)));
  return <div style={{inset:0,pointerEvents:'none',position:'absolute',zIndex:18}}>
    <div style={{background:`linear-gradient(90deg,${theme.accent},${theme.secondary})`,bottom:0,boxShadow:`0 0 24px ${theme.accent}88`,left:`${p*50}%`,position:'absolute',top:0,width:3}}/>
    <div style={{bottom:40,fontSize:18,fontWeight:900,left:40,opacity:p,position:'absolute'}}>{String(effect.left_label??'A')}</div>
    <div style={{bottom:40,fontSize:18,fontWeight:900,opacity:p,position:'absolute',right:40}}>{String(effect.right_label??'B')}</div>
  </div>;
};
