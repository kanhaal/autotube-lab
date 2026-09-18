import {useCurrentFrame,useVideoConfig} from 'remotion';
import type {ChannelTheme} from '../themes/types';
import {springProgress} from './math';
export type IntroStingProps={channelName:string;theme:ChannelTheme};
export const IntroSting=({channelName,theme}:IntroStingProps)=>{const frame=useCurrentFrame();const {fps}=useVideoConfig();const p=springProgress(frame,fps,0);const out=Math.max(0,1-Math.max(0,frame-fps*.75)/(fps*.3));return <div style={{alignItems:'center',background:theme.background,display:'flex',inset:0,justifyContent:'center',opacity:out,pointerEvents:'none',position:'absolute',zIndex:70}}><div style={{color:theme.foreground,fontSize:68,fontWeight:950,letterSpacing:-3,transform:`scale(${.86+p*.14})`}}>{channelName}<span style={{color:theme.accent}}>.</span></div></div>;};
