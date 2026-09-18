import type {ReactNode} from 'react';

import type {EffectRenderProps} from './types';

export type CodeTypewriterEffectProps = EffectRenderProps;

const tokenized = (code: string, accent: string): ReactNode[] => {
  const tokenPattern = /(\/\/.*$|#.*$|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\b(?:const|let|var|function|return|if|else|for|while|class|def|import|from|export|async|await|true|false|null|None|True|False)\b|\b\d+(?:\.\d+)?\b)/gm;
  return code.split(tokenPattern).filter(Boolean).map((token, index) => {
    let color = '#E7EDF6';
    if (/^(\/\/|#)/.test(token)) color = '#7F8C9F';
    else if (/^["']/.test(token)) color = '#A8E6A1';
    else if (/^\d/.test(token)) color = '#FFD580';
    else if (/^(const|let|var|function|return|if|else|for|while|class|def|import|from|export|async|await|true|false|null|None|True|False)$/.test(token)) color = accent;
    return <span key={index} style={{color}}>{token}</span>;
  });
};

export const CodeTypewriterEffect = ({
  effect,
  frame,
  fps,
  theme,
}: CodeTypewriterEffectProps) => {
  const code = String(effect.code ?? '');
  const cps = Math.max(4, Math.min(80, Number(effect.cps ?? 26)));
  const chars = Math.min(code.length, Math.floor((frame / Math.max(1, fps)) * cps));
  const visible = code.slice(0, chars);
  if (!code) return null;

  return (
    <div
      style={{
        background: 'rgba(5,9,15,.9)',
        border: `1px solid ${theme.border}`,
        borderRadius: 20,
        bottom: '10%',
        boxShadow: '0 24px 70px rgba(0,0,0,.42)',
        color: '#E7EDF6',
        fontFamily: 'ui-monospace, SFMono-Regular, Consolas, monospace',
        fontSize: 23,
        left: '8%',
        padding: '24px 28px',
        position: 'absolute',
        right: '8%',
        whiteSpace: 'pre-wrap',
        zIndex: 24,
      }}
    >
      {tokenized(visible, theme.accent)}
      <span style={{opacity: frame % Math.max(2, Math.round(fps * 0.6)) < Math.round(fps * 0.3) ? 1 : 0}}>
        ▋
      </span>
    </div>
  );
};
