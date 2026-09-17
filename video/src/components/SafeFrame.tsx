import type {CSSProperties, PropsWithChildren} from 'react';
import {AbsoluteFill} from 'remotion';

export const SAFE_MARGIN_X = 120;
export const SAFE_MARGIN_Y = 80;

type SafeFrameProps = PropsWithChildren<{
  style?: CSSProperties;
}>;

export const SafeFrame = ({children, style}: SafeFrameProps) => (
  <AbsoluteFill
    style={{
      boxSizing: 'border-box',
      padding: `${SAFE_MARGIN_Y}px ${SAFE_MARGIN_X}px`,
      ...style,
    }}
  >
    {children}
  </AbsoluteFill>
);
