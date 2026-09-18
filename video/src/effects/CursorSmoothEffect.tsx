import type {EffectRenderProps} from './types';
import {eased,normalizedProgress} from './math';
export type CursorPoint={x:number;y:number;at?:number};
export type CursorSmoothEffectProps=EffectRenderProps;
export const CursorSmoothEffect=({effect,frame,durationInFrames,theme}:CursorSmoothEffectProps)=>{
  const points=(Array.isArray(effect.points)?effect.points:[]) as CursorPoint[];
  if(points.length<2)return null;
  const p=eased(normalizedProgress(frame,0,Math.max(1,durationInFrames-1)));
  const scaled=p*(points.length-1),index=Math.min(points.length-2,Math.floor(scaled)),local=scaled-index;
  const a=points[index],b=points[index+1],x=a.x+(b.x-a.x)*local,y=a.y+(b.y-a.y)*local,size=Math.max(14,Number(effect.cursor_size??28));
  return <div style={{background:theme.foreground,border:`2px solid ${theme.accent}`,borderRadius:'80% 20% 80% 20%',boxShadow:`0 4px 20px rgba(0,0,0,.45),0 0 18px ${theme.accent}66`,height:size,left:`${x*100}%`,position:'absolute',top:`${y*100}%`,transform:'rotate(-42deg)',width:size,zIndex:30}}/>;
};
