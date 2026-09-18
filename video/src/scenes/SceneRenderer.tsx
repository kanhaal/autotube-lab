import type {ComponentType, ReactNode} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';

import {BrowserFrame} from '../components/BrowserFrame';
import {Chart} from '../components/Chart';
import {SafeFrame} from '../components/SafeFrame';
import {SourceBadge} from '../components/SourceBadge';
import {Stat} from '../components/Stat';
import {Timeline} from '../components/Timeline';
import {layoutForScene, staggerProgress} from '../polish';
import {
  cinematicCameraStyle,
  editorialFocusWeight,
  editorialItemStyle,
  headlineWordProgress,
  PremiumVfxBackdrop,
} from '../vfx';
import type {AssetRecordV1, SceneSpecV1} from '../types';

type Theme = Record<string, unknown>;

type SceneProps = {
  scene: SceneSpecV1;
  theme: Theme;
  assets: AssetRecordV1[];
  durationInFrames?: number;
};

type SceneComponent = ComponentType<SceneProps>;

const stringValue = (data: Record<string, unknown>, key: string, fallback = ''): string => {
  const value = data[key];
  return typeof value === 'string' && value.trim() ? value : fallback;
};

const numberValue = (data: Record<string, unknown>, key: string, fallback = 0): number => {
  const value = data[key];
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
};

const stringList = (data: Record<string, unknown>, key: string): string[] => {
  const value = data[key];
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : [];
};

const recordList = (data: Record<string, unknown>, key: string): Array<Record<string, unknown>> => {
  const value = data[key];
  return Array.isArray(value)
    ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === 'object' && !Array.isArray(item))
    : [];
};


export const chartPointsForScene = (scene: SceneSpecV1): Array<{label: string; value: number}> => {
  const explicit = recordList(scene.data, 'points').map((point, index) => ({
    label: typeof point.label === 'string' ? point.label : `Point ${index + 1}`,
    value: typeof point.value === 'number' && Number.isFinite(point.value) ? point.value : 0,
  }));
  if (explicit.length) return explicit;

  const labels = stringList(scene.data, 'labels');
  const rawValues = scene.data.values;
  const values = Array.isArray(rawValues)
    ? rawValues.filter((value): value is number => typeof value === 'number' && Number.isFinite(value))
    : [];
  return labels.slice(0, values.length).map((label, index) => ({
    label,
    value: values[index],
  }));
};

export const timelineItemsForScene = (scene: SceneSpecV1): Array<{label: string; detail?: string}> => {
  const explicit = recordList(scene.data, 'items').map((item, index) => ({
    label: typeof item.label === 'string' ? item.label : `Step ${index + 1}`,
    detail: typeof item.detail === 'string' ? item.detail : undefined,
  }));
  if (explicit.length) return explicit;

  return stringList(scene.data, 'items').map((label) => ({label}));
};

const themeColor = (theme: Theme, key: string, fallback: string): string => {
  const value = theme[key];
  return typeof value === 'string' && value ? value : fallback;
};

const frameStyle = (theme: Theme) => ({
  background:
    `radial-gradient(circle at 78% 16%, ${themeColor(theme, 'secondary', '#5AA7FF')}18, transparent 30%), ` +
    `radial-gradient(circle at 18% 88%, ${themeColor(theme, 'accent', '#67F5C5')}12, transparent 28%), ` +
    themeColor(theme, 'background', '#060912'),
  color: themeColor(theme, 'foreground', '#F8FAFF'),
  fontFamily: 'Arial, Helvetica, sans-serif',
});

const accent = (theme: Theme) => themeColor(theme, 'accent', '#67F5C5');

const supportingText = (scene: SceneSpecV1) => scene.subheadline || scene.narration || scene.purpose;

const Panel = ({children, theme}: {children: ReactNode; theme: Theme}) => (
  <div
    style={{
      backdropFilter: 'blur(18px)',
      background: 'linear-gradient(145deg, rgba(255,255,255,0.085), rgba(255,255,255,0.035))',
      border: `1px solid ${themeColor(theme, 'border', 'rgba(255,255,255,0.14)')}`,
      borderRadius: 30,
      boxShadow: '0 28px 80px rgba(0,0,0,0.26)',
      padding: 36,
    }}
  >
    {children}
  </div>
);

const SceneShell = ({scene, theme, children, eyebrow, durationInFrames}: SceneProps & {children?: ReactNode; eyebrow?: string}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const layout = layoutForScene(scene.scene_type, 'long');
  const labelProgress = staggerProgress(frame, fps, 0);
  const headlineProgress = staggerProgress(frame, fps, 1);
  const bodyProgress = staggerProgress(frame, fps, 2);
  const visualProgress = staggerProgress(frame, fps, 3);
  const supporting = scene.subheadline || (layout === 'hero' ? scene.narration : '');
  const headlineSize = layout === 'hero' ? 92 : layout === 'source' ? 76 : 72;
  const family = theme.transitionFamily === 'snap' ? 'snap' : 'precision';
  const motionIntensity = typeof theme.motionIntensity === 'number' ? theme.motionIntensity : 0.8;
  const camera = cinematicCameraStyle(
    frame,
    durationInFrames ?? Math.max(1, fps * 7),
    fps,
    family,
    motionIntensity * 0.42,
  );
  const headlineWords = scene.headline.trim().split(/\s+/).filter(Boolean);
  const emphasized = new Set(
    scene.emphasis
      .flatMap((value) => value.toLowerCase().split(/\s+/))
      .map((value) => value.replace(/[^a-z0-9]/g, ''))
      .filter(Boolean),
  );

  const textBlock = (
    <div style={{maxWidth: layout === 'source' ? 720 : layout === 'data' ? 680 : 1380}}>
      {eyebrow ? (
        <div style={{opacity: labelProgress, transform: `translateY(${(1 - labelProgress) * 18}px)`}}>
          <SourceBadge label={eyebrow} />
        </div>
      ) : null}
      {scene.headline ? (
        <div
          style={{
            fontSize: headlineSize,
            fontWeight: 900,
            letterSpacing: -3.2,
            lineHeight: 0.96,
            marginTop: eyebrow ? 26 : 0,
            maxWidth: layout === 'hero' ? 1380 : 760,
            opacity: headlineProgress,
          }}
        >
          {headlineWords.map((word, index) => {
            const progress = headlineWordProgress(frame, fps, index);
            const normalized = word.toLowerCase().replace(/[^a-z0-9]/g, '');
            const accentWord =
              emphasized.has(normalized) ||
              (layout === 'hero' && headlineWords.length <= 7 && index === headlineWords.length - 1);
            return (
              <span
                key={`${word}-${index}`}
                style={{
                  color: accentWord ? accent(theme) : 'inherit',
                  display: 'inline-block',
                  filter: `blur(${((1 - progress) * 7).toFixed(2)}px)`,
                  marginRight: 18,
                  opacity: progress,
                  textShadow: accentWord
                    ? `0 0 34px ${accent(theme)}22`
                    : family === 'snap' && progress < 0.98
                      ? `${((1 - progress) * 3).toFixed(2)}px 0 ${themeColor(theme, 'secondary', '#9CFF57')}55, ${((progress - 1) * 3).toFixed(2)}px 0 ${accent(theme)}44`
                      : 'none',
                  transform: `translate3d(0,${((1 - progress) * 42).toFixed(2)}px,0) rotateX(${((1 - progress) * -9).toFixed(2)}deg)`,
                  transformOrigin: 'center bottom',
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      ) : null}
      {supporting ? (
        <div
          style={{
            fontSize: layout === 'hero' ? 31 : 27,
            fontWeight: 560,
            lineHeight: 1.35,
            marginTop: 24,
            maxWidth: 900,
            opacity: bodyProgress * 0.72,
            transform: `translateY(${(1 - bodyProgress) * 18}px)`,
          }}
        >
          {supporting}
        </div>
      ) : null}
    </div>
  );

  return (
    <SafeFrame style={frameStyle(theme)}>
      <PremiumVfxBackdrop
        theme={theme as unknown as import('../themes/types').ChannelTheme}
        format="long"
      />
      <div
        style={{
          ...camera,
          alignItems: layout === 'data' ? 'center' : 'stretch',
          display: layout === 'data' ? 'grid' : 'flex',
          flexDirection: 'column',
          gap: layout === 'data' ? 76 : 34,
          gridTemplateColumns: layout === 'data' ? '0.78fr 1.22fr' : undefined,
          height: '100%',
          justifyContent: 'center',
          position: 'relative',
          zIndex: 2,
        }}
      >
        {textBlock}
        {children ? (
          <div
            style={{
              minWidth: 0,
              opacity: visualProgress,
              transform: `translateY(${(1 - visualProgress) * 34}px) scale(${0.985 + visualProgress * 0.015})`,
            }}
          >
            {children}
          </div>
        ) : null}
      </div>
    </SafeFrame>
  );
};

export const HookScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  return (
    <SceneShell {...props} eyebrow="THE SIGNAL">
      <div style={{background: accent(theme), borderRadius: 999, height: 12, marginTop: 12, width: 180}} />
      <div style={{fontSize: 24, fontWeight: 750, letterSpacing: 2, opacity: 0.55, textTransform: 'uppercase'}}>
        {scene.emphasis.slice(0, 3).join(' • ') || 'What changed and why it matters'}
      </div>
    </SceneShell>
  );
};

export const HeadlineScene: SceneComponent = (props) => <SceneShell {...props} eyebrow="UPDATE" />;

export const SourceBrowserScene: SceneComponent = (props) => {
  const {scene, theme, assets} = props;
  const url = stringValue(scene.data, 'url', stringValue(scene.data, 'source_url', 'source.local'));
  const body = stringValue(scene.data, 'body', supportingText(scene));
  const hasCapturedVisual =
    scene.asset_ids.some((id) => assets.some((asset) => asset.id === id)) ||
    assets.some((asset) => asset.scene_id === scene.id);
  return (
    <SceneShell {...props} eyebrow="SOURCE">
      {hasCapturedVisual ? (
        <div
          style={{
            alignItems: 'center',
            color: accent(theme),
            display: 'flex',
            fontSize: 21,
            fontWeight: 800,
            gap: 12,
            letterSpacing: 1.2,
            textTransform: 'uppercase',
          }}
        >
          <span style={{background: accent(theme), borderRadius: 99, boxShadow: `0 0 22px ${accent(theme)}66`, height: 12, width: 12}} />
          Captured evidence
        </div>
      ) : (
        <BrowserFrame url={url}>
          <div style={{display: 'flex', flexDirection: 'column', gap: 18}}>
            <div style={{fontSize: 42, fontWeight: 800}}>{stringValue(scene.data, 'page_title', scene.headline || 'Source')}</div>
            <div style={{fontSize: 25, lineHeight: 1.5}}>{body || 'Verified source material'}</div>
            <div style={{background: accent(theme), borderRadius: 999, height: 7, marginTop: 8, width: '34%'}} />
          </div>
        </BrowserFrame>
      )}
    </SceneShell>
  );
};

export const DeviceScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  return (
    <SceneShell {...props} eyebrow="PRODUCT">
      <div style={{display: 'flex', justifyContent: 'center'}}>
        <div style={{background: '#0E121A', border: '10px solid #252B36', borderRadius: 58, boxShadow: '0 35px 90px rgba(0,0,0,.4)', height: 470, padding: 28, width: 260}}>
          <div style={{background: accent(theme), borderRadius: 999, height: 8, margin: '0 auto 30px', opacity: 0.7, width: 72}} />
          <div style={{fontSize: 30, fontWeight: 800}}>{stringValue(scene.data, 'device_name', scene.headline || 'Device')}</div>
          <div style={{fontSize: 20, lineHeight: 1.45, marginTop: 18, opacity: 0.65}}>{stringValue(scene.data, 'feature', supportingText(scene))}</div>
        </div>
      </div>
    </SceneShell>
  );
};

export const GithubScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  const repo = stringValue(scene.data, 'repo', stringValue(scene.data, 'repository', 'owner/project'));
  const stars = numberValue(scene.data, 'stars', 0);
  const language = stringValue(scene.data, 'language', 'Open source');
  return (
    <SceneShell {...props} eyebrow="GITHUB">
      <Panel theme={theme}>
        <div style={{display: 'flex', justifyContent: 'space-between', gap: 28}}>
          <div>
            <div style={{fontFamily: 'monospace', fontSize: 42, fontWeight: 800}}>{repo}</div>
            <div style={{fontSize: 24, marginTop: 18, opacity: 0.68}}>{stringValue(scene.data, 'description', supportingText(scene))}</div>
          </div>
          <div style={{textAlign: 'right'}}>
            <div style={{color: accent(theme), fontSize: 46, fontWeight: 850}}>{stars.toLocaleString()}</div>
            <div style={{fontSize: 20, opacity: 0.55}}>stars</div>
          </div>
        </div>
        <div style={{fontSize: 21, marginTop: 28, opacity: 0.6}}>{language}</div>
      </Panel>
    </SceneShell>
  );
};

export const GameStoreScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  return (
    <SceneShell {...props} eyebrow="GAME / STORE">
      <div style={{display: 'grid', gap: 28, gridTemplateColumns: '0.85fr 1.15fr'}}>
        <div style={{background: `linear-gradient(145deg, ${accent(theme)}, #161B28)`, borderRadius: 30, minHeight: 330, padding: 32}}>
          <div style={{fontSize: 54, fontWeight: 900, marginTop: 140}}>{stringValue(scene.data, 'game', scene.headline || 'Game')}</div>
        </div>
        <Panel theme={theme}>
          <div style={{fontSize: 34, fontWeight: 800}}>{stringValue(scene.data, 'status', 'Now trending')}</div>
          <div style={{fontSize: 25, lineHeight: 1.45, marginTop: 18, opacity: 0.68}}>{stringValue(scene.data, 'detail', supportingText(scene))}</div>
          <div style={{color: accent(theme), fontSize: 28, fontWeight: 800, marginTop: 30}}>{stringValue(scene.data, 'price', stringValue(scene.data, 'release', ''))}</div>
        </Panel>
      </div>
    </SceneShell>
  );
};

export const StatScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  return (
    <SceneShell {...props} eyebrow="BY THE NUMBERS">
      <div style={{color: accent(theme)}}>
        <Stat label={stringValue(scene.data, 'label', scene.subheadline || 'Key metric')} value={numberValue(scene.data, 'value', 0)} suffix={stringValue(scene.data, 'suffix')} />
      </div>
    </SceneShell>
  );
};

export const ChartScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  const points = chartPointsForScene(scene);
  return (
    <SceneShell {...props} eyebrow="TREND">
      <Panel theme={theme}><Chart points={points.length ? points : [{label: 'Now', value: 1}]} accent={accent(theme)} /></Panel>
    </SceneShell>
  );
};

export const TimelineScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  const items = timelineItemsForScene(scene);
  return (
    <SceneShell {...props} eyebrow="TIMELINE">
      <Panel theme={theme}><Timeline items={items.length ? items : [{label: 'Now', detail: supportingText(scene)}]} accent={accent(theme)} /></Panel>
    </SceneShell>
  );
};

const splitScene = (
  props: SceneProps,
  eyebrow: string,
  leftLabel: string,
  rightLabel: string,
  frame: number,
  fps: number,
) => {
  const {scene, theme} = props;
  const left = stringValue(scene.data, 'before', stringValue(scene.data, 'left', 'Before'));
  const right = stringValue(scene.data, 'after', stringValue(scene.data, 'right', 'After'));
  const family = theme.transitionFamily === 'snap' ? 'snap' : 'precision';
  return (
    <SceneShell {...props} eyebrow={eyebrow}>
      <div style={{display: 'grid', gap: 28, gridTemplateColumns: '1fr 1fr', perspective: 1500}}>
        <div style={editorialItemStyle(frame, fps, 0, family)}>
          <Panel theme={theme}>
            <div style={{fontSize: 20, fontWeight: 800, opacity: 0.5}}>{leftLabel}</div>
            <div style={{fontSize: 34, fontWeight: 750, marginTop: 20}}>{left}</div>
          </Panel>
        </div>
        <div style={editorialItemStyle(frame, fps, 1, family)}>
          <Panel theme={theme}>
            <div style={{color: accent(theme), fontSize: 20, fontWeight: 800}}>{rightLabel}</div>
            <div style={{fontSize: 34, fontWeight: 750, marginTop: 20}}>{right}</div>
          </Panel>
        </div>
      </div>
    </SceneShell>
  );
};

export const BeforeAfterScene: SceneComponent = (props) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return splitScene(props, 'BEFORE / AFTER', 'BEFORE', 'AFTER', frame, fps);
};

export const ComparisonScene: SceneComponent = (props) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return splitScene(props, 'COMPARISON', 'OPTION A', 'OPTION B', frame, fps);
};

export const QuoteScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  const quote = stringValue(scene.data, 'quote', scene.narration || scene.headline);
  return (
    <SceneShell {...props} eyebrow="QUOTE">
      <div style={{borderLeft: `10px solid ${accent(theme)}`, fontSize: 48, fontWeight: 680, lineHeight: 1.25, maxWidth: 1320, padding: '12px 0 12px 38px'}}>“{quote}”</div>
      <div style={{fontSize: 23, opacity: 0.55}}>{stringValue(scene.data, 'attribution', scene.source_ids[0] || '')}</div>
    </SceneShell>
  );
};

export const ListScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const items = stringList(scene.data, 'items');
  const family = theme.transitionFamily === 'snap' ? 'snap' : 'precision';
  return (
    <SceneShell {...props} eyebrow="KEY POINTS">
      <div style={{display: 'grid', gap: 18}}>
        {(items.length ? items : scene.emphasis).slice(0, 6).map((item, index) => (
          <div key={`${item}-${index}`} style={editorialItemStyle(frame, fps, index, family)}>
            <Panel theme={theme}>
              <span style={{color: accent(theme), fontWeight: 900, marginRight: 18}}>{String(index + 1).padStart(2, '0')}</span>
              <span style={{fontSize: 28, fontWeight: 700}}>{item}</span>
            </Panel>
          </div>
        ))}
      </div>
    </SceneShell>
  );
};

export const ProcessScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const steps = (stringList(scene.data, 'steps').length ? stringList(scene.data, 'steps') : ['Input', 'Process', 'Output']).slice(0, 5);
  const family = theme.transitionFamily === 'snap' ? 'snap' : 'precision';
  const duration = props.durationInFrames ?? Math.max(1, fps * 7);
  return (
    <SceneShell {...props} eyebrow="HOW IT WORKS">
      <div style={{display: 'flex', gap: 18, perspective: 1500}}>
        {steps.map((step, index) => {
          const motion = editorialItemStyle(frame, fps, index, family);
          const focus = editorialFocusWeight(frame, duration, index, steps.length);
          const motionOpacity = typeof motion.opacity === 'number' ? motion.opacity : 1;
          const motionTransform = typeof motion.transform === 'string' ? motion.transform : '';
          return (
            <div
              key={`${step}-${index}`}
              style={{
                ...motion,
                background: 'linear-gradient(145deg, rgba(255,255,255,.082), rgba(255,255,255,.035))',
                border: `1px solid ${themeColor(theme, 'border', 'rgba(255,255,255,.14)')}`,
                borderRadius: 24,
                boxShadow: `0 ${Math.round(14 + focus * 10)}px ${Math.round(36 + focus * 24)}px rgba(0,0,0,.22), 0 0 ${Math.round(focus * 36)}px ${accent(theme)}22`,
                flex: 1,
                fontSize: 24,
                fontWeight: 800,
                opacity: motionOpacity * (0.7 + focus * 0.3),
                overflow: 'hidden',
                padding: '34px 24px 38px',
                position: 'relative',
                textAlign: 'center',
                transform: `${motionTransform} scale(${(0.985 + focus * 0.022).toFixed(4)})`,
              }}
            >
              <div style={{position: 'relative', zIndex: 1}}>{step}</div>
              <div
                style={{
                  background: `linear-gradient(90deg, transparent, ${accent(theme)}, transparent)`,
                  bottom: 0,
                  height: 4,
                  left: 18,
                  opacity: 0.18 + focus * 0.82,
                  position: 'absolute',
                  right: 18,
                  transform: `scaleX(${focus.toFixed(4)})`,
                  transformOrigin: 'center',
                }}
              />
            </div>
          );
        })}
      </div>
    </SceneShell>
  );
};

export const CodeScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  const code = stringValue(scene.data, 'code', stringValue(scene.data, 'snippet', '// code example'));
  return (
    <SceneShell {...props} eyebrow="CODE">
      <pre style={{background: '#0B0F17', border: '1px solid rgba(255,255,255,.12)', borderRadius: 28, color: '#DDE7F2', fontFamily: 'ui-monospace, SFMono-Regular, Consolas, monospace', fontSize: 25, lineHeight: 1.5, margin: 0, overflow: 'hidden', padding: 34, whiteSpace: 'pre-wrap'}}>
        <span style={{color: accent(theme)}}>{stringValue(scene.data, 'language', 'code')}</span>{'\n\n'}{code}
      </pre>
    </SceneShell>
  );
};

export const MapScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  const markers = stringList(scene.data, 'markers');
  return (
    <SceneShell {...props} eyebrow="WHERE">
      <div style={{background: 'linear-gradient(135deg,#0D1421,#121A2B)', borderRadius: 30, minHeight: 360, overflow: 'hidden', position: 'relative'}}>
        <div style={{backgroundImage: 'linear-gradient(rgba(255,255,255,.06) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.06) 1px, transparent 1px)', backgroundSize: '52px 52px', inset: 0, position: 'absolute'}} />
        {(markers.length ? markers : ['Primary location']).slice(0, 5).map((marker, index) => (
          <div key={marker} style={{left: `${18 + (index * 17) % 70}%`, position: 'absolute', top: `${22 + (index * 23) % 56}%`}}>
            <div style={{background: accent(theme), borderRadius: 99, boxShadow: `0 0 30px ${accent(theme)}`, height: 18, width: 18}} />
            <div style={{fontSize: 19, fontWeight: 700, marginTop: 8, whiteSpace: 'nowrap'}}>{marker}</div>
          </div>
        ))}
      </div>
    </SceneShell>
  );
};

export const SocialContextScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const posts = recordList(scene.data, 'posts');
  const cards = posts.length ? posts : [{author: 'Community', text: supportingText(scene)}];
  const family = theme.transitionFamily === 'snap' ? 'snap' : 'precision';
  return (
    <SceneShell {...props} eyebrow="SOCIAL SIGNAL">
      <div style={{display: 'grid', gap: 20, gridTemplateColumns: cards.length > 1 ? '1fr 1fr' : '1fr'}}>
        {cards.slice(0, 4).map((post, index) => (
          <div key={index} style={editorialItemStyle(frame, fps, index, family)}>
            <Panel theme={theme}>
              <div style={{color: accent(theme), fontSize: 20, fontWeight: 900}}>{typeof post.author === 'string' ? post.author : 'Community'}</div>
              <div style={{fontSize: 27, fontWeight: 620, lineHeight: 1.4, marginTop: 14}}>{typeof post.text === 'string' ? post.text : 'Conversation is accelerating.'}</div>
            </Panel>
          </div>
        ))}
      </div>
    </SceneShell>
  );
};

export const ChapterScene: SceneComponent = (props) => (
  <SceneShell {...props} eyebrow="NEXT CHAPTER">
    <div style={{fontSize: 24, fontWeight: 750, letterSpacing: 2, opacity: 0.5, textTransform: 'uppercase'}}>Context → Evidence → Implication</div>
  </SceneShell>
);

export const ConclusionScene: SceneComponent = (props) => {
  const {theme} = props;
  return (
    <SceneShell {...props} eyebrow="WHY IT MATTERS">
      <div style={{background: accent(theme), borderRadius: 999, height: 10, width: 240}} />
    </SceneShell>
  );
};

export const FallbackEditorialScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  return (
    <SceneShell {...props} eyebrow="EDITORIAL">
      <div style={{display: 'grid', gap: 24, gridTemplateColumns: '1.2fr 0.8fr', maxWidth: 1360}}>
        <Panel theme={theme}>
          <div style={{color: accent(theme), fontSize: 20, fontWeight: 900, letterSpacing: 2.2, textTransform: 'uppercase'}}>
            Context first
          </div>
          <div style={{fontSize: 34, fontWeight: 780, lineHeight: 1.22, marginTop: 18}}>
            {scene.emphasis.slice(0, 3).join(' • ') || 'Verified context without invented imagery'}
          </div>
          <div style={{fontSize: 23, lineHeight: 1.45, marginTop: 20, opacity: 0.58}}>
            Original editorial treatment keeps the pace moving when a source visual is unavailable.
          </div>
        </Panel>
        <div
          style={{
            alignItems: 'flex-end',
            background: `linear-gradient(145deg, ${accent(theme)}DD, ${themeColor(theme, 'secondary', accent(theme))}88)`,
            borderRadius: 30,
            boxShadow: `0 28px 80px ${accent(theme)}20`,
            color: '#07100D',
            display: 'flex',
            fontSize: 22,
            fontWeight: 900,
            justifyContent: 'flex-start',
            letterSpacing: 2,
            minHeight: 260,
            padding: 32,
            textTransform: 'uppercase',
          }}
        >
          Signal / context
        </div>
      </div>
    </SceneShell>
  );
};

export const SCENE_REGISTRY: Record<string, SceneComponent> = {
  hook: HookScene,
  headline: HeadlineScene,
  source_browser: SourceBrowserScene,
  device: DeviceScene,
  github: GithubScene,
  game_store: GameStoreScene,
  stat: StatScene,
  chart: ChartScene,
  timeline: TimelineScene,
  before_after: BeforeAfterScene,
  comparison: ComparisonScene,
  quote: QuoteScene,
  list: ListScene,
  process: ProcessScene,
  code: CodeScene,
  map: MapScene,
  social_context: SocialContextScene,
  chapter: ChapterScene,
  conclusion: ConclusionScene,
  fallback_editorial: FallbackEditorialScene,
};

export const sceneComponentFor = (type: string): SceneComponent => {
  const component = SCENE_REGISTRY[type];
  if (!component) throw new Error(`Unknown scene type: ${type}`);
  return component;
};

export const SceneRenderer = ({scene, theme, assets}: SceneProps) => {
  const Component = sceneComponentFor(scene.scene_type);
  return <Component scene={scene} theme={theme} assets={assets} />;
};
