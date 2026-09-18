import {Freeze} from 'remotion';
import type {ReactNode} from 'react';
import type {EffectRenderProps} from './types';
export type FreezeFrameEffectProps=EffectRenderProps&{children?:ReactNode};
export const freezeFrameWrap=(children:ReactNode,props:EffectRenderProps)=>{const at=Math.max(0,Math.round(Number(props.effect.at_frame??props.durationInFrames*.62)));return props.frame<at?children:<Freeze frame={at}>{children}</Freeze>;};
export const FreezeFrameEffect=()=>null;
