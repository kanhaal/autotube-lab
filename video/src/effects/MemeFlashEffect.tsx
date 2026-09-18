import {Img,staticFile} from 'remotion';
import type {EffectRenderProps} from './types';
export type MemeFlashEffectProps=EffectRenderProps;
export const memeFlashDurationFrames=(seconds:number,fps:number)=>Math.round(Math.max(.5,Math.min(1.5,Number.isFinite(seconds)?seconds:1))*Math.max(1,fps));
export const MemeFlashEffect=({effect,frame,fps,assets}:MemeFlashEffectProps)=>{
  const limit=memeFlashDurationFrames(Number(effect.duration_seconds??1),fps);
  if(frame>=limit)return null;
  const asset=assets.find(item=>item.id===String(effect.asset_id??''));
  return <div style={{alignItems:'center',background:'rgba(0,0,0,.92)',display:'flex',inset:0,justifyContent:'center',position:'absolute',zIndex:50}}>
    {asset?<Img src={staticFile(asset.local_path)} style={{maxHeight:'86%',maxWidth:'86%',objectFit:'contain'}}/>:<div style={{fontSize:58,fontWeight:950,textAlign:'center'}}>{String(effect.text??'...')}</div>}
  </div>;
};
