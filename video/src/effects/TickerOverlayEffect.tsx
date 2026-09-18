import type {EffectRenderProps} from './types';
export type TickerOverlayEffectProps=EffectRenderProps;
export const TickerOverlayEffect=({effect,theme}:TickerOverlayEffectProps)=>{
  const badge=String(effect.badge??''),safe=badge==='LEAK'||badge==='UNCONFIRMED'?badge:'';
  return <div style={{alignItems:'center',background:'rgba(4,7,12,.88)',borderTop:`1px solid ${theme.border}`,bottom:0,display:'flex',gap:16,left:0,padding:'13px 26px',position:'absolute',right:0,zIndex:35}}>
    {safe?<span style={{background:safe==='LEAK'?'#FF5A5A':'#F1B84B',borderRadius:999,color:'#090909',fontSize:15,fontWeight:950,padding:'6px 10px'}}>{safe}</span>:null}
    <span style={{fontSize:19,fontWeight:800,letterSpacing:.4}}>{String(effect.text??'')}</span>
  </div>;
};
