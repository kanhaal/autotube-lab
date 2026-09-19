import type {EffectRenderProps} from './types';

const particle=(index:number)=>{
  const angle=(index*137.508*Math.PI)/180;
  const radius=.45+((index*17)%37)/52;
  return {x:Math.cos(angle)*radius,y:Math.sin(angle)*radius,size:4+(index*7)%9};
};

export const ParticleBurstEffect=({effect,frame,fps,theme}:EffectRenderProps)=>{
  const at=Number(effect.at??.3)*fps;
  const duration=Math.max(8,Number(effect.duration_frames??Math.round(fps*.7)));
  const p=Math.max(0,Math.min(1,(frame-at)/duration));
  if(p<=0||p>=1)return null;
  const count=Math.max(8,Math.min(70,Number(effect.count??28)));
  const centerX=Number(effect.x??.5),centerY=Number(effect.y??.5);
  const ease=1-Math.pow(1-p,3);
  return <div style={{inset:0,pointerEvents:'none',position:'absolute',zIndex:34}}>
    {Array.from({length:count}).map((_,index)=>{
      const item=particle(index);
      return <div key={index} style={{
        background:index%3===0?theme.secondary:theme.accent,
        borderRadius:index%4===0?2:99,
        boxShadow:`0 0 14px ${theme.accent}44`,
        height:item.size,
        left:`${(centerX+item.x*ease*.38)*100}%`,
        opacity:1-p,
        position:'absolute',
        top:`${(centerY+item.y*ease*.38+p*p*.12)*100}%`,
        transform:`rotate(${index*31+p*180}deg) scale(${1-p*.35})`,
        width:item.size*(index%4===0?1.8:1),
      }}/>;
    })}
  </div>;
};
