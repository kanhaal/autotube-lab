import type {CSSProperties} from 'react';

export const wrapText = (text: string, maxChars: number): string[] => {
  if (maxChars < 1) throw new Error('maxChars must be positive');
  const words = text.trim().split(/\s+/).filter(Boolean);
  const lines: string[] = [];
  let current = '';
  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word;
    if (candidate.length <= maxChars || !current) {
      current = candidate;
    } else {
      lines.push(current);
      current = word;
    }
  }
  if (current) lines.push(current);
  return lines;
};

export const Headline = ({
  text,
  maxChars = 22,
  style,
}: {
  text: string;
  maxChars?: number;
  style?: CSSProperties;
}) => (
  <div style={{fontSize: 78, fontWeight: 800, letterSpacing: -2, lineHeight: 0.98, ...style}}>
    {wrapText(text, maxChars).map((line) => (
      <div key={line}>{line}</div>
    ))}
  </div>
);
