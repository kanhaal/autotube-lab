import type {EffectRenderProps} from './types';

export const LensFlareEffect=({effect,frame,durationInFrames,theme}:EffectRenderProps)=>{
  const p=Math.max(0,Math.min(1,frame/Math.max(1,durationInFrames-1)));
  const x=10+p*80;
  const y=Number(effect.y??28);
  const strength=Math.max(0,Math.min(.55,Number(effect.strength??.24)));
  return <div style={{inset:0,mixBlendMode:'screen',pointerEvents:'none',position:'absolute',zIndex:29}}>
    <div style={{
      background:`radial-gradient(circle,${theme.accent}CC 0%,rgba(255,255,255,.5) 4%,${theme.secondary}55 11%,transparent 32%)`,
      filter:'blur(3px)',
      height:240,
      left:`calc(${x}% - 120px)`,
      opacity:strength,
      position:'absolute',
      top:`calc(${y}% - 120px)`,
      width:240,
    }}/>
    {[.18,.34,.58,.76].map((offset,index)=><div key={index} style={{
      border:`1px solid ${index%2?theme.secondary:theme.accent}55`,
      borderRadius:999,
      height:24+index*17,
      left:`${x-(x-50)*offset}%`,
      opacity:strength*(.7-index*.1),
      position:'absolute',
      top:`${y+(50-y)*offset}%`,
      transform:'translate(-50%,-50%)',
      width:24+index*17,
    }}/>)}
  </div>;
};
