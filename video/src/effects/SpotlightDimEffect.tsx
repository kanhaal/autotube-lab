import type {BoundingBox,EffectRenderProps} from './types';
export type SpotlightDimEffectProps=EffectRenderProps;
export const SpotlightDimEffect=({effect}:SpotlightDimEffectProps)=>{
  const target=(effect.target??{x:.25,y:.25,width:.5,height:.5}) as BoundingBox;
  const opacity=Math.max(0,Math.min(.85,Number(effect.opacity??.62)));
  return <div style={{inset:0,pointerEvents:'none',position:'absolute',zIndex:20,background:`radial-gradient(ellipse at ${(target.x+target.width/2)*100}% ${(target.y+target.height/2)*100}%,transparent 0%,transparent ${Math.max(target.width,target.height)*45}%,rgba(0,0,0,${opacity}) ${Math.max(target.width,target.height)*58}%)`}}/>;
};
