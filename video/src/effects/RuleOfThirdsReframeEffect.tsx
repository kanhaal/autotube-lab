import type {CSSProperties} from 'react';
import type {EffectRenderProps} from './types';

export const ruleOfThirdsReframeTransform=({effect,frame,durationInFrames}:EffectRenderProps):CSSProperties=>{
  const p=Math.max(0,Math.min(1,frame/Math.max(1,durationInFrames-1)));
  const x=Math.max(0,Math.min(1,Number(effect.x??.333)));
  const y=Math.max(0,Math.min(1,Number(effect.y??.333)));
  const strength=Math.max(0,Math.min(1.4,Number(effect.strength??.75)));
  const tx=(.5-x)*14*p*strength;
  const ty=(.5-y)*10*p*strength;
  const scale=1+.055*p*strength;
  return {
    transform:`translate3d(${tx.toFixed(3)}%,${ty.toFixed(3)}%,0) scale(${scale.toFixed(5)})`,
    transformOrigin:`${(x*100).toFixed(2)}% ${(y*100).toFixed(2)}%`,
  };
};

export const RuleOfThirdsReframeEffect=()=>null;
