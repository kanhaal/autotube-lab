export type ChannelTheme = Record<string, unknown> & {
  id: string;
  background: string;
  foreground: string;
  accent: string;
  secondary: string;
  border: string;
  muted: string;
  typeScale: {
    display: number;
    headline: number;
    body: number;
    label: number;
  };
  spacing: number;
  transitionFamily: 'precision' | 'snap';
  captionStyle: 'glass' | 'punch';
  motionIntensity: number;
};
