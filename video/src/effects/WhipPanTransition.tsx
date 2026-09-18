import type {EffectRenderProps} from './types';

export const WhipPanTransition = ({frame, durationInFrames, theme}: EffectRenderProps) => {
  const start = Math.max(0, durationInFrames - 9);
  const p = Math.max(0, Math.min(1, (frame - start) / Math.max(1, durationInFrames - start)));
  if (p <= 0) return null;
  const wave = Math.sin(p * Math.PI);
  return (
    <div style={{inset:0,overflow:'hidden',pointerEvents:'none',position:'absolute',zIndex:65}}>
      <div style={{
        background:`linear-gradient(90deg,transparent,${theme.accent}33,rgba(255,255,255,.34),${theme.secondary}33,transparent)`,
        filter:`blur(${6 + wave * 18}px)`,
        height:'140%',
        left:`${-55 + p * 155}%`,
        opacity:wave * .9,
        position:'absolute',
        top:'-20%',
        transform:`skewX(-16deg) scaleX(${1 + wave * 1.8})`,
        width:'36%',
      }}/>
      <div style={{
        backdropFilter:`blur(${wave * 7}px)`,
        background:`linear-gradient(90deg,rgba(0,0,0,${wave*.18}),transparent)`,
        inset:0,
        opacity:wave,
        position:'absolute',
        transform:`translateX(${(1-p)*-80}px)`,
      }}/>
    </div>
  );
};
