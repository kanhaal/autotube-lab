import type {EffectRenderProps} from './types';

export const CrossDissolveTransition = ({frame, durationInFrames, theme}: EffectRenderProps) => {
  const start=Math.max(0,durationInFrames-14);
  const p=Math.max(0,Math.min(1,(frame-start)/Math.max(1,durationInFrames-start)));
  if(p<=0)return null;
  const smooth=p*p*(3-2*p);
  return <div style={{
    background:`radial-gradient(circle at 50% 44%,${theme.secondary}18,rgba(2,4,8,${smooth*.38}))`,
    backdropFilter:`blur(${smooth*3}px)`,
    inset:0,
    opacity:smooth,
    pointerEvents:'none',
    position:'absolute',
    zIndex:62,
  }}/>;
};
