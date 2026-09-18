import type {EffectRenderProps} from './types';
export type CodeTypewriterEffectProps=EffectRenderProps;
export const CodeTypewriterEffect=({effect,frame,fps,theme}:CodeTypewriterEffectProps)=>{
  const code=String(effect.code??''),cps=Math.max(4,Math.min(80,Number(effect.cps??26))),chars=Math.min(code.length,Math.floor((frame/Math.max(1,fps))*cps));
  if(!code)return null;
  return <div style={{background:'rgba(5,9,15,.9)',border:`1px solid ${theme.border}`,borderRadius:20,bottom:'10%',boxShadow:'0 24px 70px rgba(0,0,0,.42)',color:'#E7EDF6',fontFamily:'ui-monospace, SFMono-Regular, Consolas, monospace',fontSize:23,left:'8%',padding:'24px 28px',position:'absolute',right:'8%',whiteSpace:'pre-wrap',zIndex:24}}>
    <span style={{color:theme.accent}}>{code.slice(0,chars)}</span><span style={{opacity:frame%Math.max(2,Math.round(fps*.6))<Math.round(fps*.3)?1:0}}>▋</span>
  </div>;
};
