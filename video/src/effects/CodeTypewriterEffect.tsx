import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';
import {effectNumber, effectString} from './utils';

export type CodeTypewriterEffectProps = EffectComponentProps;

const KEYWORDS = new Set([
  'const', 'let', 'var', 'function', 'return', 'async', 'await', 'if', 'else', 'for', 'while',
  'class', 'import', 'from', 'export', 'def', 'lambda', 'True', 'False', 'None', 'try', 'except',
]);

const highlightLine = (line: string, accent: string) => {
  const tokens = line.split(/(\s+|[()[\]{}:,.=+\-*\/]+)/g);
  return tokens.map((token, index) => {
    const color = KEYWORDS.has(token)
      ? accent
      : /^["'\`].*["'\`]$/.test(token)
        ? '#A8E6A3'
        : /^\d+(?:\.\d+)?$/.test(token)
          ? '#FFD479'
          : '#E8EDF4';
    return <span key={`${token}-${index}`} style={{color}}>{token}</span>;
  });
};

export const CodeTypewriterEffect = ({effect, children, scene, theme}: CodeTypewriterEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const code = effectString(effect, 'code', typeof scene.data.code === 'string' ? scene.data.code : '');
  const cps = Math.min(120, Math.max(4, effectNumber(effect, 'cps', 28)));
  const startFrame = Math.max(0, Math.round(effectNumber(effect, 'start_seconds', 0) * fps));
  const visible = Math.max(0, Math.floor(((frame - startFrame) / fps) * cps));
  const text = code.slice(0, visible);
  const cursor = frame >= startFrame && Math.floor(frame / Math.max(1, Math.round(fps * 0.42))) % 2 === 0;

  return (
    <>
      {children}
      {code ? (
        <div
          style={{
            backdropFilter: 'blur(18px)',
            background: 'rgba(5,9,16,.93)',
            border: `1px solid ${theme.border}`,
            borderRadius: 18,
            bottom: 88,
            boxShadow: '0 24px 70px rgba(0,0,0,.42)',
            fontFamily: 'Consolas, Menlo, monospace',
            fontSize: 22,
            left: 88,
            lineHeight: 1.48,
            maxHeight: '46%',
            overflow: 'hidden',
            padding: '22px 26px',
            position: 'absolute',
            right: 88,
            whiteSpace: 'pre-wrap',
            zIndex: 70,
          }}
        >
          {text.split('\n').map((line, index) => (
            <div key={`${index}-${line}`}>
              <span style={{color: theme.muted, display: 'inline-block', marginRight: 18, opacity: 0.5, width: 30}}>
                {String(index + 1).padStart(2, '0')}
              </span>
              {highlightLine(line, theme.accent)}
              {index === text.split('\n').length - 1 && cursor ? <span style={{color: theme.accent}}>▋</span> : null}
            </div>
          ))}
        </div>
      ) : null}
    </>
  );
};
