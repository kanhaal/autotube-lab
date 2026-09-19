import type {EffectRenderProps} from './types';

export const LightLeakEffect=({effect,frame,fps,theme}:EffectRenderProps)=>{
  const seconds=frame/Math.max(1,fps);
  const speed=Math.max(.15,Math.min(2,Number(effect.speed??.55)));
  const x=((seconds*speed*120)%180)-40;
  const opacity=Math.max(0,Math.min(.45,Number(effect.opacity??.2)));
  return <div style={{
    background:
      `radial-gradient(circle at ${x}% 22%,${theme.accent}88 0%,${theme.secondary}44 18%,transparent 44%)`,
    filter:'blur(28px)',
    inset:'-18%',
    mixBlendMode:'screen',
    opacity,
    pointerEvents:'none',
    position:'absolute',
    zIndex:28,
  }}/>;
};
