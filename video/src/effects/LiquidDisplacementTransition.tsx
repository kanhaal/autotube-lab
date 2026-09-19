import type {EffectRenderProps} from './types';

export const LiquidDisplacementTransition = ({frame,durationInFrames,theme}:EffectRenderProps)=>{
  const start=Math.max(0,durationInFrames-14);
  const p=Math.max(0,Math.min(1,(frame-start)/Math.max(1,durationInFrames-start)));
  if(p<=0)return null;
  const wave=Math.sin(p*Math.PI);
  const bands=Array.from({length:9});
  return <div style={{inset:0,overflow:'hidden',pointerEvents:'none',position:'absolute',zIndex:66}}>
    {bands.map((_,index)=>{
      const y=index*(100/bands.length);
      const offset=Math.sin(index*1.8+p*Math.PI*3)*wave*34;
      return <div key={index} style={{
        background:`linear-gradient(90deg,transparent,${index%2===0?theme.accent:theme.secondary}22,transparent)`,
        filter:`blur(${3+wave*8}px)`,
        height:`${100/bands.length+2}%`,
        left:-50,
        opacity:wave*.82,
        position:'absolute',
        top:`${y}%`,
        transform:`translateX(${offset}px) scaleX(${1+wave*.08})`,
        width:'calc(100% + 100px)',
      }}/>;
    })}
    <div style={{backdropFilter:`blur(${wave*5}px)`,inset:0,opacity:wave*.55,position:'absolute'}}/>
  </div>;
};
