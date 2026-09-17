import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

import type {CaptionCueV1, RenderPackageV1, SceneSpecV1} from '../types';
import type {ChannelTheme} from '../themes/types';
import {sceneFrameWindows} from './sceneTiming';
import {validateShortPackage} from './shortTiming';

const dataText = (scene: SceneSpecV1, key: string, fallback = ''): string => {
  const value = scene.data[key];
  return typeof value === 'string' && value.trim() ? value : fallback;
};

const dataNumber = (scene: SceneSpecV1, key: string): number | undefined => {
  const value = scene.data[key];
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined;
};

const dataList = (scene: SceneSpecV1, key: string): string[] => {
  const value = scene.data[key];
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : [];
};

const sceneLabel = (scene: SceneSpecV1): string => {
  const labels: Record<string, string> = {
    hook: 'THE SIGNAL',
    headline: 'UPDATE',
    source_browser: 'SOURCE',
    device: 'PRODUCT',
    github: 'GITHUB',
    game_store: 'GAME / STORE',
    stat: 'BY THE NUMBERS',
    chart: 'TREND',
    timeline: 'TIMELINE',
    before_after: 'BEFORE / AFTER',
    comparison: 'COMPARISON',
    quote: 'QUOTE',
    list: 'KEY POINTS',
    process: 'HOW IT WORKS',
    code: 'CODE',
    map: 'WHERE',
    social_context: 'CONTEXT',
    chapter: 'NEXT',
    conclusion: 'WHAT TO WATCH',
    fallback_editorial: 'THE SIGNAL',
  };
  return labels[scene.scene_type] ?? 'THE SIGNAL';
};

const VerticalPanel = ({children, theme}: {children: React.ReactNode; theme: ChannelTheme}) => (
  <div
    style={{
      background: 'rgba(255,255,255,0.065)',
      border: `1px solid ${theme.border}`,
      borderRadius: 34,
      boxShadow: '0 22px 70px rgba(0,0,0,0.28)',
      padding: '30px 32px',
    }}
  >
    {children}
  </div>
);

const VerticalSceneVisual = ({scene, theme}: {scene: SceneSpecV1; theme: ChannelTheme}) => {
  if (scene.scene_type === 'stat') {
    const value = dataNumber(scene, 'value');
    const suffix = dataText(scene, 'suffix');
    return (
      <VerticalPanel theme={theme}>
        <div style={{color: theme.accent, fontSize: 112, fontWeight: 900, letterSpacing: -5}}>
          {value ?? dataText(scene, 'value', '—')}{suffix}
        </div>
        <div style={{fontSize: 30, fontWeight: 700, marginTop: 10, opacity: 0.7}}>
          {dataText(scene, 'label', scene.subheadline || 'Key metric')}
        </div>
      </VerticalPanel>
    );
  }

  if (scene.scene_type === 'quote') {
    return (
      <VerticalPanel theme={theme}>
        <div style={{borderLeft: `9px solid ${theme.accent}`, fontSize: 48, fontWeight: 760, lineHeight: 1.2, paddingLeft: 26}}>
          “{dataText(scene, 'quote', scene.narration)}”
        </div>
        <div style={{fontSize: 24, marginTop: 24, opacity: 0.52}}>
          {dataText(scene, 'attribution', scene.source_ids[0] || '')}
        </div>
      </VerticalPanel>
    );
  }

  if (scene.scene_type === 'list') {
    const items = dataList(scene, 'items');
    const visible = (items.length ? items : scene.emphasis).slice(0, 4);
    return (
      <div style={{display: 'grid', gap: 16}}>
        {visible.map((item, index) => (
          <VerticalPanel key={`${item}-${index}`} theme={theme}>
            <div style={{display: 'flex', gap: 18}}>
              <span style={{color: theme.accent, fontSize: 28, fontWeight: 900}}>{String(index + 1).padStart(2, '0')}</span>
              <span style={{fontSize: 31, fontWeight: 720, lineHeight: 1.2}}>{item}</span>
            </div>
          </VerticalPanel>
        ))}
      </div>
    );
  }

  if (scene.scene_type === 'comparison' || scene.scene_type === 'before_after') {
    const left = dataText(scene, 'before', dataText(scene, 'left', 'Before'));
    const right = dataText(scene, 'after', dataText(scene, 'right', 'After'));
    return (
      <div style={{display: 'grid', gap: 18}}>
        <VerticalPanel theme={theme}>
          <div style={{fontSize: 22, fontWeight: 850, letterSpacing: 2, opacity: 0.45}}>A</div>
          <div style={{fontSize: 38, fontWeight: 760, marginTop: 10}}>{left}</div>
        </VerticalPanel>
        <VerticalPanel theme={theme}>
          <div style={{color: theme.accent, fontSize: 22, fontWeight: 850, letterSpacing: 2}}>B</div>
          <div style={{fontSize: 38, fontWeight: 760, marginTop: 10}}>{right}</div>
        </VerticalPanel>
      </div>
    );
  }

  if (scene.scene_type === 'code') {
    return (
      <pre
        style={{
          background: '#090D14',
          border: `1px solid ${theme.border}`,
          borderRadius: 32,
          color: '#E7EDF6',
          fontFamily: 'ui-monospace, SFMono-Regular, Consolas, monospace',
          fontSize: 27,
          lineHeight: 1.45,
          margin: 0,
          maxHeight: 470,
          overflow: 'hidden',
          padding: 30,
          whiteSpace: 'pre-wrap',
        }}
      >
        <span style={{color: theme.accent}}>{dataText(scene, 'language', 'code')}</span>{'\n\n'}
        {dataText(scene, 'code', dataText(scene, 'snippet', '// verified example'))}
      </pre>
    );
  }

  const detail = scene.subheadline || dataText(scene, 'detail', scene.narration);
  return (
    <VerticalPanel theme={theme}>
      <div style={{display: 'flex', alignItems: 'center', gap: 16}}>
        <div style={{background: theme.accent, borderRadius: 999, height: 14, width: 14}} />
        <div style={{fontSize: 25, fontWeight: 850, letterSpacing: 1.4, textTransform: 'uppercase'}}>
          {scene.emphasis.slice(0, 2).join(' • ') || scene.purpose}
        </div>
      </div>
      <div style={{fontSize: 31, lineHeight: 1.35, marginTop: 22, opacity: 0.72}}>{detail}</div>
    </VerticalPanel>
  );
};

const VerticalScene = ({scene, theme}: {scene: SceneSpecV1; theme: ChannelTheme}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const translateY = interpolate(frame, [0, 10], [32, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const headlineSize = scene.headline.length > 42 ? 66 : scene.headline.length > 25 ? 78 : 92;

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 50% 20%, ${theme.secondary}22, transparent 34%), ${theme.background}`,
        boxSizing: 'border-box',
        color: theme.foreground,
        fontFamily: 'Inter, Arial, sans-serif',
        padding: '148px 132px 400px 88px',
      }}
    >
      <div style={{opacity, transform: `translateY(${translateY}px)`}}>
        <div
          style={{
            color: theme.accent,
            fontSize: 22,
            fontWeight: 900,
            letterSpacing: 3.2,
            marginBottom: 26,
            textTransform: 'uppercase',
          }}
        >
          {sceneLabel(scene)}
        </div>
        <div style={{fontSize: headlineSize, fontWeight: 920, letterSpacing: -3.4, lineHeight: 0.98}}>
          {scene.headline || scene.narration}
        </div>
        {scene.subheadline ? (
          <div style={{fontSize: 34, fontWeight: 620, lineHeight: 1.25, marginTop: 26, opacity: 0.68}}>
            {scene.subheadline}
          </div>
        ) : null}
        <div style={{marginTop: 46}}>
          <VerticalSceneVisual scene={scene} theme={theme} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

const activeCaptionAt = (cues: CaptionCueV1[], seconds: number): CaptionCueV1 | undefined =>
  cues.find((cue) => seconds >= cue.start && seconds < cue.end);

const VerticalCaptionTrack = ({cues, theme}: {cues: CaptionCueV1[]; theme: ChannelTheme}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = activeCaptionAt(cues, frame / fps);
  if (!cue) return null;

  return (
    <div
      style={{
        bottom: 238,
        left: 70,
        position: 'absolute',
        right: 150,
        textAlign: 'center',
      }}
    >
      <div
        style={{
          background: theme.captionStyle === 'punch' ? 'rgba(6,5,12,0.9)' : 'rgba(4,8,14,0.84)',
          border: `1px solid ${theme.border}`,
          borderRadius: theme.captionStyle === 'punch' ? 24 : 18,
          boxShadow: '0 16px 48px rgba(0,0,0,0.36)',
          color: '#FFFFFF',
          display: 'inline-block',
          fontSize: theme.captionStyle === 'punch' ? 58 : 50,
          fontWeight: 880,
          lineHeight: 1.08,
          maxWidth: 790,
          padding: '20px 28px 24px',
        }}
      >
        {cue.text}
      </div>
    </div>
  );
};

export const ShortComposition = ({pkg, theme}: {pkg: RenderPackageV1; theme: ChannelTheme}) => {
  validateShortPackage(pkg);
  const windows = sceneFrameWindows(pkg);

  return (
    <AbsoluteFill style={{background: theme.background}}>
      {pkg.manifest.audio_path ? <Audio src={staticFile(pkg.manifest.audio_path)} /> : null}
      {pkg.scenes.scenes.map((scene, index) => {
        const window = windows[index];
        if (!window) return null;
        return (
          <Sequence key={scene.id} from={window.from} durationInFrames={window.durationInFrames}>
            <VerticalScene scene={scene} theme={theme} />
          </Sequence>
        );
      })}
      <VerticalCaptionTrack cues={pkg.captions.cues} theme={theme} />
    </AbsoluteFill>
  );
};
