import type {EffectRenderProps} from './types';
import {eased,normalizedProgress} from './math';
export const WhooshZoomTransition=({frame,durationInFrames}:EffectRenderProps)=>{const p=eased(normalizedProgress(frame,Math.max(0,durationInFrames-12),durationInFrames));if(p<=0)return null;return <div style={{background:`radial-gradient(circle at center,rgba(255,255,255,${p*.16}),transparent 55%)`,filter:`blur(${p*8}px)`,inset:0,opacity:p,pointerEvents:'none',position:'absolute',transform:`scale(${1+p*.12})`,zIndex:60}}/>;};
