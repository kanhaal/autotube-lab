import type {EffectRenderProps} from './types';
import {eased,normalizedProgress} from './math';
export type VsScreenEffectProps=EffectRenderProps;
export const VsScreenEffect=({effect,frame,durationInFrames,theme}:VsScreenEffectProps)=>{
  const p=eased(normalizedProgress(frame,0,durationInFrames*.55)),left=Number(effect.left_value??0),right=Number(effect.right_value??0),max=Math.max(1,left,right);
  return <div style={{alignItems:'center',bottom:'10%',display:'grid',gap:16,gridTemplateColumns:'1fr auto 1fr',left:'7%',position:'absolute',right:'7%',zIndex:22}}>
    <div><div style={{fontSize:26,fontWeight:900}}>{String(effect.left_label??'A')}</div><div style={{background:'rgba(255,255,255,.12)',borderRadius:99,height:12,overflow:'hidden'}}><div style={{background:theme.secondary,height:'100%',width:`${p*left/max*100}%`}}/></div></div>
    <div style={{color:theme.accent,fontSize:34,fontWeight:950}}>VS</div>
    <div style={{textAlign:'right'}}><div style={{fontSize:26,fontWeight:900}}>{String(effect.right_label??'B')}</div><div style={{background:'rgba(255,255,255,.12)',borderRadius:99,height:12,overflow:'hidden'}}><div style={{background:theme.accent,height:'100%',marginLeft:'auto',width:`${p*right/max*100}%`}}/></div></div>
  </div>;
};
