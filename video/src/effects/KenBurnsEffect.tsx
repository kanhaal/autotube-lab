import type {CSSProperties} from 'react';
import type {EffectRenderProps} from './types';

export const kenBurnsTransform=({effect,frame,durationInFrames}:EffectRenderProps):CSSProperties=>{
  const p=Math.max(0,Math.min(1,frame/Math.max(1,durationInFrames-1)));
  const zoom=Math.max(1.02,Math.min(1.22,Number(effect.zoom??1.09)));
  const x=Number(effect.pan_x??-1.8);
  const y=Number(effect.pan_y??-1.1);
  const ease=p*p*(3-2*p);
  return {
    transform:`translate3d(${(x*ease).toFixed(3)}%,${(y*ease).toFixed(3)}%,0) scale(${(1+(zoom-1)*ease).toFixed(5)})`,
    transformOrigin:'center center',
  };
};

export const KenBurnsEffect=()=>null;
