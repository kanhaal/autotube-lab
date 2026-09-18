import {interpolate,spring} from 'remotion';

export const clamp01=(value:number)=>Math.max(0,Math.min(1,value));
export const normalizedProgress=(frame:number,start:number,end:number)=>clamp01((frame-start)/Math.max(1,end-start));
export const eased=(progress:number)=>progress*progress*(3-2*progress);
export const springProgress=(frame:number,fps:number,delay=0)=>spring({frame:Math.max(0,frame-delay),fps,config:{damping:16,stiffness:150,mass:.85}});
export const pulse=(frame:number,fps:number,hz=1)=>(Math.sin((frame/Math.max(1,fps))*Math.PI*2*hz)+1)/2;
export const tween=(frame:number,from:number,to:number,start:number,end:number)=>interpolate(frame,[start,end],[from,to],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
