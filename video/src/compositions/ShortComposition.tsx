import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

import {Chart} from '../components/Chart';
import {Stat} from '../components/Stat';
import {Timeline} from '../components/Timeline';
import {
  activeWordIndex,
  layoutForScene,
  overlappedSceneWindow,
  sceneEnvelope,
  staggerProgress,
} from '../polish';
import {
  resolveSceneAsset,
  scenePresentationStyle,
  sceneSupportsVerifiedAsset,
} from '../scenes/presentation';
import type {CaptionCueV1, RenderPackageV1, SceneSpecV1} from '../types';
import {
  cinematicCameraStyle,
  headlineWordProgress,
  PremiumVfxBackdrop,
  TransitionAccent,
} from '../vfx';
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

const dataNumberList = (scene: SceneSpecV1, key: string): number[] => {
  const value = scene.data[key];
  return Array.isArray(value)
    ? value.filter((item): item is number => typeof item === 'number' && Number.isFinite(item))
    : [];
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
      backdropFilter: 'blur(20px)',
      background: 'linear-gradient(145deg, rgba(255,255,255,0.10), rgba(255,255,255,0.045))',
      border: `1px solid ${theme.border}`,
      borderRadius: 34,
      boxShadow: '0 30px 84px rgba(0,0,0,0.30)',
      padding: '32px 34px',
    }}
  >
    {children}
  </div>
);

const VerticalSceneVisual = ({
  scene,
  theme,
  hasSourceAsset,
}: {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  hasSourceAsset: boolean;
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  if (scene.scene_type === 'source_browser' && hasSourceAsset) {
    return <div style={{height: 600}} />;
  }

  if (scene.scene_type === 'stat') {
    return (
      <VerticalPanel theme={theme}>
        <div style={{color: theme.accent}}>
          <Stat
            label={dataText(scene, 'label', scene.subheadline || 'Key metric')}
            value={dataNumber(scene, 'value') ?? 0}
            suffix={dataText(scene, 'suffix')}
          />
        </div>
      </VerticalPanel>
    );
  }

  if (scene.scene_type === 'chart') {
    const labels = dataList(scene, 'labels');
    const values = dataNumberList(scene, 'values');
    const points = labels.slice(0, values.length).map((label, index) => ({
      label,
      value: values[index],
    }));
    return (
      <VerticalPanel theme={theme}>
        <Chart points={points.length ? points : [{label: 'Now', value: 1}]} accent={theme.accent} />
      </VerticalPanel>
    );
  }

  if (scene.scene_type === 'timeline') {
    const items = dataList(scene, 'items').map((label) => ({label}));
    return (
      <VerticalPanel theme={theme}>
        <Timeline items={items.length ? items : [{label: scene.subheadline || 'Now'}]} accent={theme.accent} />
      </VerticalPanel>
    );
  }

  if (scene.scene_type === 'quote') {
    return (
      <VerticalPanel theme={theme}>
        <div style={{borderLeft: `9px solid ${theme.accent}`, fontSize: 48, fontWeight: 800, lineHeight: 1.18, paddingLeft: 26}}>
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
        {visible.map((item, index) => {
          const progress = staggerProgress(frame, fps, index + 2);
          return (
            <div key={`${item}-${index}`} style={{opacity: progress, transform: `translateX(${(1 - progress) * 28}px)`}}>
              <VerticalPanel theme={theme}>
                <div style={{display: 'flex', gap: 18}}>
                  <span style={{color: theme.accent, fontSize: 28, fontWeight: 900}}>{String(index + 1).padStart(2, '0')}</span>
                  <span style={{fontSize: 31, fontWeight: 760, lineHeight: 1.2}}>{item}</span>
                </div>
              </VerticalPanel>
            </div>
          );
        })}
      </div>
    );
  }

  if (scene.scene_type === 'comparison' || scene.scene_type === 'before_after') {
    const left = dataText(scene, 'before', dataText(scene, 'left', 'Before'));
    const right = dataText(scene, 'after', dataText(scene, 'right', 'After'));
    return (
      <div style={{display: 'grid', gap: 18}}>
        {[['A', left], ['B', right]].map(([label, text], index) => {
          const progress = staggerProgress(frame, fps, index + 2);
          return (
            <div key={label} style={{opacity: progress, transform: `translateY(${(1 - progress) * 24}px)`}}>
              <VerticalPanel theme={theme}>
                <div style={{color: index === 1 ? theme.accent : theme.muted, fontSize: 22, fontWeight: 900, letterSpacing: 2}}>{label}</div>
                <div style={{fontSize: 40, fontWeight: 800, marginTop: 10}}>{text}</div>
              </VerticalPanel>
            </div>
          );
        })}
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
        <div style={{background: theme.accent, borderRadius: 999, boxShadow: `0 0 24px ${theme.accent}55`, height: 14, width: 14}} />
        <div style={{fontSize: 25, fontWeight: 900, letterSpacing: 1.4, textTransform: 'uppercase'}}>
          {scene.emphasis.slice(0, 2).join(' • ') || scene.purpose}
        </div>
      </div>
      <div style={{fontSize: 31, lineHeight: 1.35, marginTop: 22, opacity: 0.7}}>{detail}</div>
    </VerticalPanel>
  );
};

const VerticalScene = ({
  scene,
  theme,
  durationInFrames,
  hasSourceAsset,
}: {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  durationInFrames: number;
  hasSourceAsset: boolean;
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const presentation = scenePresentationStyle(scene, frame, fps);
  const envelope = sceneEnvelope(frame, durationInFrames, Math.max(7, Math.round(fps * 0.24)));
  const layout = layoutForScene(scene.scene_type, 'short');
  const labelProgress = staggerProgress(frame, fps, 0);
  const headlineProgress = staggerProgress(frame, fps, 1);
  const subProgress = staggerProgress(frame, fps, 2);
  const visualProgress = staggerProgress(frame, fps, 3);
  const headlineSize = scene.headline.length > 42 ? 64 : scene.headline.length > 25 ? 76 : 88;
  const topPadding = layout === 'hero' ? 190 : layout === 'source' ? 120 : 128;
  const camera = cinematicCameraStyle(
    frame,
    durationInFrames,
    fps,
    theme.transitionFamily,
    theme.motionIntensity * 0.48,
  );
  const presentationTransform =
    typeof presentation.transform === 'string' ? presentation.transform : '';
  const cameraTransform = typeof camera.transform === 'string' ? camera.transform : '';
  const headlineWords = (scene.headline || scene.narration).trim().split(/\s+/).filter(Boolean);
  const emphasisWords = new Set(
    scene.emphasis
      .flatMap((value) => value.toLowerCase().split(/\s+/))
      .map((value) => value.replace(/[^a-z0-9]/g, ''))
      .filter(Boolean),
  );

  return (
    <AbsoluteFill
      style={{
        background:
          `radial-gradient(circle at 50% 12%, ${theme.secondary}25, transparent 31%), ` +
          `radial-gradient(circle at 82% 54%, ${theme.accent}10, transparent 32%), ${theme.background}`,
        boxSizing: 'border-box',
        color: theme.foreground,
        fontFamily: 'Arial, Helvetica, sans-serif',
        overflow: 'hidden',
        padding: `${topPadding}px 68px 330px`,
      }}
    >
      <PremiumVfxBackdrop theme={theme} format="short" />
      <div
        style={{
          ...presentation,
          ...camera,
          height: '100%',
          opacity: (typeof presentation.opacity === 'number' ? presentation.opacity : 1) * envelope,
          position: 'relative',
          transform: `${presentationTransform} ${cameraTransform}`.trim(),
          zIndex: 2,
        }}
      >
        <div
          style={{
            color: theme.accent,
            fontSize: 21,
            fontWeight: 900,
            letterSpacing: 3.4,
            marginBottom: 24,
            opacity: labelProgress,
            textTransform: 'uppercase',
            transform: `translateY(${(1 - labelProgress) * 18}px)`,
          }}
        >
          {sceneLabel(scene)}
        </div>
        <div
          style={{
            fontSize: headlineSize,
            fontWeight: 900,
            letterSpacing: -3.2,
            lineHeight: 0.95,
            maxWidth: 930,
            opacity: headlineProgress,
          }}
        >
          {headlineWords.map((word, index) => {
            const wordProgress = headlineWordProgress(frame, fps, index);
            const normalized = word.toLowerCase().replace(/[^a-z0-9]/g, '');
            const accentWord =
              emphasisWords.has(normalized) ||
              (headlineWords.length <= 7 && index === headlineWords.length - 1);
            return (
              <span
                key={`${word}-${index}`}
                style={{
                  color: accentWord ? theme.accent : '#FFFFFF',
                  display: 'inline-block',
                  filter: `blur(${((1 - wordProgress) * 9).toFixed(2)}px)`,
                  marginRight: 16,
                  opacity: wordProgress,
                  textShadow: accentWord ? `0 0 30px ${theme.accent}33` : 'none',
                  transform: `translate3d(0,${((1 - wordProgress) * 54).toFixed(2)}px,0) rotateX(${((1 - wordProgress) * -12).toFixed(2)}deg) scale(${(0.94 + wordProgress * 0.06).toFixed(3)})`,
                  transformOrigin: 'center bottom',
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
        {scene.subheadline ? (
          <div
            style={{
              fontSize: 31,
              fontWeight: 650,
              lineHeight: 1.24,
              marginTop: 22,
              opacity: subProgress * 0.66,
              transform: `translateY(${(1 - subProgress) * 18}px)`,
            }}
          >
            {scene.subheadline}
          </div>
        ) : null}
        <div
          style={{
            marginTop: layout === 'source' ? 28 : 40,
            opacity: visualProgress,
            transform: `translateY(${(1 - visualProgress) * 34}px) scale(${0.985 + visualProgress * 0.015})`,
          }}
        >
          <VerticalSceneVisual scene={scene} theme={theme} hasSourceAsset={hasSourceAsset} />
        </div>
      </div>
      <div
        style={{
          background: `linear-gradient(90deg, ${theme.accent}, ${theme.secondary})`,
          borderRadius: 99,
          bottom: 94,
          boxShadow: `0 0 26px ${theme.accent}55`,
          height: 6,
          left: 68,
          opacity: 0.62,
          position: 'absolute',
          width: 92,
          zIndex: 3,
        }}
      />
      <TransitionAccent theme={theme} durationInFrames={durationInFrames} />
    </AbsoluteFill>
  );
};

const activeCaptionAt = (cues: CaptionCueV1[], seconds: number): CaptionCueV1 | undefined =>
  cues.find((cue) => seconds >= cue.start && seconds < cue.end);

const cueWords = (cue: CaptionCueV1): string[] => {
  if (cue.word_timings?.length) return cue.word_timings.map((word) => word.text);
  if (cue.words.length) return cue.words;
  return cue.text.trim().split(/\s+/).filter(Boolean);
};

const VerticalCaptionTrack = ({cues, theme}: {cues: CaptionCueV1[]; theme: ChannelTheme}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const seconds = frame / fps;
  const cue = activeCaptionAt(cues, seconds);
  if (!cue) return null;

  const words = cueWords(cue);
  const active = activeWordIndex(cue, seconds);
  const localFrame = Math.max(0, frame - Math.round(cue.start * fps));
  const reveal = staggerProgress(localFrame, fps, 0);

  return (
    <div
      style={{
        bottom: 160,
        left: 54,
        position: 'absolute',
        right: 54,
        textAlign: 'center',
        transform: `translateY(${(1 - reveal) * 20}px)`,
        opacity: reveal,
      }}
    >
      <div
        style={{
          backdropFilter: 'blur(20px)',
          background: theme.captionStyle === 'punch' ? 'rgba(7,4,12,0.80)' : 'rgba(3,8,14,0.74)',
          border: `1px solid ${theme.border}`,
          borderRadius: 26,
          boxShadow: '0 20px 60px rgba(0,0,0,0.34)',
          color: '#FFFFFF',
          display: 'inline-block',
          fontFamily: 'Arial, Helvetica, sans-serif',
          fontSize: theme.captionStyle === 'punch' ? 57 : 53,
          fontWeight: 900,
          letterSpacing: -1.2,
          lineHeight: 1.08,
          maxWidth: 900,
          padding: '20px 28px 24px',
        }}
      >
        {words.map((word, index) => (
          <span
            key={`${word}-${index}`}
            style={{
              background: index === active ? theme.accent : 'transparent',
              borderRadius: index === active ? 10 : 0,
              boxShadow: index === active ? `0 0 26px ${theme.accent}44` : 'none',
              color: index === active ? '#07100D' : '#FFFFFF',
              display: 'inline-block',
              margin: '2px 4px',
              opacity: active >= 0 && Math.abs(index - active) > 4 ? 0.62 : 1,
              padding: index === active ? '2px 8px 5px' : '2px 3px 5px',
              textShadow: index === active ? 'none' : '0 2px 14px rgba(0,0,0,.42)',
              transform: index === active ? 'translateY(-2px) scale(1.075)' : 'scale(1)',
            }}
          >
            {word}
          </span>
        ))}
      </div>
    </div>
  );
};

export const ShortComposition = ({pkg, theme}: {pkg: RenderPackageV1; theme: ChannelTheme}) => {
  validateShortPackage(pkg);
  const windows = sceneFrameWindows(pkg);

  return (
    <AbsoluteFill style={{background: theme.background, fontFamily: 'Arial, Helvetica, sans-serif'}}>
      {pkg.manifest.audio_path ? <Audio src={staticFile(pkg.manifest.audio_path)} /> : null}
      {pkg.scenes.scenes.map((scene, index) => {
        const window = windows[index];
        if (!window) return null;
        const editWindow = overlappedSceneWindow(
          window,
          index,
          pkg.scenes.scenes.length,
          Math.max(8, Math.round(pkg.manifest.fps * 0.28)),
        );
        const hasSourceAsset =
          sceneSupportsVerifiedAsset(scene) &&
          Boolean(resolveSceneAsset(scene, pkg.assets.records));
        return (
          <Sequence key={scene.id} from={editWindow.from} durationInFrames={editWindow.durationInFrames}>
            <VerticalScene
              scene={scene}
              theme={theme}
              durationInFrames={editWindow.durationInFrames}
              hasSourceAsset={hasSourceAsset}
            />
          </Sequence>
        );
      })}
      <VerticalCaptionTrack cues={pkg.captions.cues} theme={theme} />
    </AbsoluteFill>
  );
};
