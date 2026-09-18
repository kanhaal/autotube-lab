import type {EffectRenderProps} from './types';
export type KineticWordRevealProps=EffectRenderProps;
export const KineticWordReveal=({captions,absoluteFrame,fps,scene,theme}:KineticWordRevealProps)=>{
  const seconds=absoluteFrame/Math.max(1,fps),cue=captions.find(item=>seconds>=item.start&&seconds<item.end); if(!cue)return null;
  const fallback=cue.text.split(/\s+/).filter(Boolean); const words=cue.word_timings?.length?cue.word_timings:fallback.map((text,index)=>({text,start:cue.start+(cue.end-cue.start)*index/Math.max(1,fallback.length),end:cue.start+(cue.end-cue.start)*(index+1)/Math.max(1,fallback.length)}));
  const stressed=new Set(scene.emphasis.flatMap(x=>x.toLowerCase().split(/\s+/)).map(x=>x.replace(/[^a-z0-9]/g,'')));
  return <div style={{bottom:'13%',left:'8%',position:'absolute',right:'8%',textAlign:'center',zIndex:31}}>
    {words.map((word,index)=>{const active=seconds>=word.start&&seconds<word.end,token=word.text.toLowerCase().replace(/[^a-z0-9]/g,''),stress=active&&stressed.has(token);return <span key={index} style={{color:active?theme.accent:'#fff',display:'inline-block',fontSize:46,fontWeight:stress?950:800,margin:'0 7px',textShadow:stress?`0 0 28px ${theme.accent}77`:'none',transform:`scale(${stress?1.16:active?1.07:1})`}}>{word.text}</span>;})}
  </div>;
};
