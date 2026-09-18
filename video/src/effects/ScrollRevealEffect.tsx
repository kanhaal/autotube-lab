import {Img,staticFile} from 'remotion';
import type {BoundingBox,EffectRenderProps} from './types';
import {eased,normalizedProgress} from './math';
export type ScrollRevealEffectProps=EffectRenderProps;
export const ScrollRevealEffect=({effect,frame,durationInFrames,assets,theme}:ScrollRevealEffectProps)=>{
  const asset=assets.find(item=>item.id===String(effect.asset_id??'')); if(!asset)return null;
  const p=eased(normalizedProgress(frame,0,Math.max(1,durationInFrames-1))),fromY=Number(effect.start_y??0),toY=Number(effect.end_y??-55),box=effect.highlight as BoundingBox|undefined;
  return <div style={{borderRadius:22,inset:'8%',overflow:'hidden',position:'absolute',zIndex:12}}>
    <Img src={staticFile(asset.local_path)} style={{transform:`translateY(${fromY+(toY-fromY)*p}%)`,width:'100%'}}/>
    {box?<div style={{border:`3px solid ${theme.accent}`,boxShadow:`0 0 28px ${theme.accent}66`,height:`${box.height*100}%`,left:`${box.x*100}%`,position:'absolute',top:`${box.y*100}%`,width:`${box.width*100}%`}}/>:null}
  </div>;
};
