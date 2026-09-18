import type {EffectRenderProps} from './types';
import {springProgress} from './math';
export type TierItem={label:string;tier:'S'|'A'|'B'|'C'|'D'};
export type TierListEffectProps=EffectRenderProps;
export const TierListEffect=({effect,frame,fps,theme}:TierListEffectProps)=>{
  const items=(Array.isArray(effect.items)?effect.items:[]) as TierItem[]; const tiers=['S','A','B','C','D'] as const;
  return <div style={{bottom:'8%',display:'grid',gap:7,left:'6%',position:'absolute',right:'6%',zIndex:22}}>
    {tiers.map((tier,row)=><div key={tier} style={{alignItems:'center',background:'rgba(5,8,14,.72)',border:`1px solid ${theme.border}`,borderRadius:12,display:'flex',gap:10,minHeight:52,padding:'6px 10px'}}>
      <div style={{color:theme.accent,fontWeight:950,width:34}}>{tier}</div>
      {items.filter(i=>i.tier===tier).map((item,index)=>{const p=springProgress(frame,fps,(row*2+index)*4);return <div key={item.label} style={{background:`${theme.accent}22`,borderRadius:10,fontSize:18,fontWeight:800,opacity:p,padding:'8px 12px',transform:`translateX(${(1-p)*34}px) scale(${.88+p*.12})`}}>{item.label}</div>;})}
    </div>)}
  </div>;
};
