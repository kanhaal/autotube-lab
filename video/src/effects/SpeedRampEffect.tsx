import {Video,staticFile} from 'remotion';
import type {EffectRenderProps} from './types';
import {eased,normalizedProgress} from './math';
export type SpeedRampEffectProps=EffectRenderProps;
export const SpeedRampEffect=({effect,frame,durationInFrames,assets}:SpeedRampEffectProps)=>{
  const asset=assets.find(item=>item.id===String(effect.asset_id??''));
  if(!asset||!/video|gameplay|clip/i.test(asset.kind))return null;
  const start=Number(effect.start_frame??durationInFrames*.25),end=Number(effect.end_frame??durationInFrames*.62),span=Math.max(2,end-start);
  const down=eased(normalizedProgress(frame,start,start+span*.25)),up=eased(normalizedProgress(frame,end-span*.25,end));
  const slow=Math.max(.35,Math.min(.75,Number(effect.slow_rate??.5)));
  const playbackRate=frame<start?1:frame<end?1-(1-slow)*down+(1-slow)*up:1;
  return <Video src={staticFile(asset.local_path)} playbackRate={playbackRate} muted style={{height:'100%',objectFit:'cover',position:'absolute',width:'100%',zIndex:8}}/>;
};
