import {EditorialMedia} from '../editor/media';
import type {EffectRenderProps} from './types';

export const SplitScreenMultiAngleEffect=({effect,assets,theme}:EffectRenderProps)=>{
  const ids=Array.isArray(effect.asset_ids)?effect.asset_ids.map(String):[];
  const selected=ids.map(id=>assets.find(asset=>asset.id===id)).filter((asset):asset is NonNullable<typeof asset>=>Boolean(asset)).slice(0,3);
  if(selected.length<2)return null;
  return <div style={{
    background:'#05070B',
    display:'grid',
    gap:4,
    gridTemplateColumns:selected.length===2?'1fr 1fr':'1fr 1fr 1fr',
    inset:0,
    padding:4,
    position:'absolute',
    zIndex:16,
  }}>
    {selected.map((asset,index)=><div key={asset.id} style={{border:`1px solid ${theme.border}`,overflow:'hidden',position:'relative'}}>
      <EditorialMedia asset={asset} style={{objectPosition:index===0?'35% center':index===1?'65% center':'center'}}/>
      <div style={{
        background:'rgba(4,7,11,.68)',
        bottom:16,
        color:index===0?'#fff':theme.accent,
        fontSize:15,
        fontWeight:900,
        left:16,
        letterSpacing:1.4,
        padding:'6px 9px',
        position:'absolute',
        textTransform:'uppercase',
      }}>ANGLE {index+1}</div>
    </div>)}
  </div>;
};
