import type {EffectRenderProps} from './types';
import {normalizedProgress} from './math';
export const GlitchRgbSplitTransition=({frame,durationInFrames,theme}:EffectRenderProps)=>{const p=normalizedProgress(frame,Math.max(0,durationInFrames-10),durationInFrames);if(p<=0)return null;const shift=(1-p)*14;return <div style={{background:`repeating-linear-gradient(0deg,transparent 0 5px,rgba(255,255,255,${(1-p)*.06}) 6px)`,boxShadow:`${shift}px 0 0 ${theme.accent}55,-${shift}px 0 0 ${theme.secondary}55`,inset:0,pointerEvents:'none',position:'absolute',zIndex:60}}/>;};
