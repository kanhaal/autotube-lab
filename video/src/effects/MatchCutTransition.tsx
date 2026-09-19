import type {EffectRenderProps} from './types';

export const MatchCutTransition = ({frame, durationInFrames, theme}: EffectRenderProps) => {
  const start = Math.max(0, durationInFrames - 10);
  const p = Math.max(0, Math.min(1, (frame - start) / Math.max(1, durationInFrames - start)));
  if (p <= 0) return null;
  const pulse = Math.sin(p * Math.PI);
  return (
    <div style={{inset:0,pointerEvents:'none',position:'absolute',zIndex:64}}>
      <div style={{
        border:`${2 + pulse * 3}px solid ${theme.accent}`,
        borderRadius:999,
        boxShadow:`0 0 ${24 + pulse*54}px ${theme.accent}55`,
        height:`${40 + p*780}px`,
        left:'50%',
        opacity:pulse,
        position:'absolute',
        top:'50%',
        transform:'translate(-50%,-50%)',
        width:`${40 + p*780}px`,
      }}/>
      <div style={{
        background:`radial-gradient(circle,${theme.accent}20,transparent 62%)`,
        inset:0,
        opacity:pulse*.7,
        position:'absolute',
      }}/>
    </div>
  );
};
