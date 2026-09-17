import type {ComponentType, ReactNode} from 'react';

import {BrowserFrame} from '../components/BrowserFrame';
import {Chart} from '../components/Chart';
import {SafeFrame} from '../components/SafeFrame';
import {SourceBadge} from '../components/SourceBadge';
import {Stat} from '../components/Stat';
import {Timeline} from '../components/Timeline';
import {Headline} from '../components/Typography';
import type {AssetRecordV1, SceneSpecV1} from '../types';

type Theme = Record<string, unknown>;

type SceneProps = {
  scene: SceneSpecV1;
  theme: Theme;
  assets: AssetRecordV1[];
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

const themeColor = (theme: Theme, key: string, fallback: string): string => {
  const value = theme[key];
  return typeof value === 'string' && value ? value : fallback;
};

const frameStyle = (theme: Theme) => ({
  background: themeColor(theme, 'background', '#060912'),
  color: themeColor(theme, 'foreground', '#F8FAFF'),
  fontFamily: 'Inter, Arial, sans-serif',
});

const accent = (theme: Theme) => themeColor(theme, 'accent', '#67F5C5');

const supportingText = (scene: SceneSpecV1) => scene.subheadline || scene.narration || scene.purpose;

const Panel = ({children, theme}: {children: ReactNode; theme: Theme}) => (
  <div
    style={{
      background: 'rgba(255,255,255,0.06)',
      border: `1px solid ${themeColor(theme, 'border', 'rgba(255,255,255,0.14)')}`,
      borderRadius: 28,
      padding: 34,
    }}
  >
    {children}
  </div>
);

const SceneShell = ({scene, theme, children, eyebrow}: SceneProps & {children?: ReactNode; eyebrow?: string}) => (
  <SafeFrame style={frameStyle(theme)}>
    <div style={{display: 'flex', flexDirection: 'column', gap: 28, height: '100%', justifyContent: 'center'}}>
      {eyebrow ? <SourceBadge label={eyebrow} /> : null}
      {scene.headline ? <Headline text={scene.headline} /> : null}
      {supportingText(scene) ? (
        <div style={{fontSize: 30, lineHeight: 1.35, maxWidth: 1260, opacity: 0.72}}>{supportingText(scene)}</div>
      ) : null}
      {children}
    </div>
  </SafeFrame>
);

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
  const {scene, theme} = props;
  const url = stringValue(scene.data, 'url', stringValue(scene.data, 'source_url', 'source.local'));
  const body = stringValue(scene.data, 'body', supportingText(scene));
  return (
    <SceneShell {...props} eyebrow="SOURCE">
      <BrowserFrame url={url}>
        <div style={{display: 'flex', flexDirection: 'column', gap: 18}}>
          <div style={{fontSize: 42, fontWeight: 800}}>{stringValue(scene.data, 'page_title', scene.headline || 'Source')}</div>
          <div style={{fontSize: 25, lineHeight: 1.5}}>{body || 'Verified source material'}</div>
          <div style={{background: accent(theme), borderRadius: 999, height: 7, marginTop: 8, width: '34%'}} />
        </div>
      </BrowserFrame>
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
  const points = recordList(scene.data, 'points').map((point, index) => ({
    label: typeof point.label === 'string' ? point.label : `Point ${index + 1}`,
    value: typeof point.value === 'number' ? point.value : 0,
  }));
  return (
    <SceneShell {...props} eyebrow="TREND">
      <Panel theme={theme}><Chart points={points.length ? points : [{label: 'Now', value: 1}]} accent={accent(theme)} /></Panel>
    </SceneShell>
  );
};

export const TimelineScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  const items = recordList(scene.data, 'items').map((item, index) => ({
    label: typeof item.label === 'string' ? item.label : `Step ${index + 1}`,
    detail: typeof item.detail === 'string' ? item.detail : undefined,
  }));
  return (
    <SceneShell {...props} eyebrow="TIMELINE">
      <Panel theme={theme}><Timeline items={items.length ? items : [{label: 'Now', detail: supportingText(scene)}]} accent={accent(theme)} /></Panel>
    </SceneShell>
  );
};

const splitScene = (props: SceneProps, eyebrow: string, leftLabel: string, rightLabel: string) => {
  const {scene, theme} = props;
  const left = stringValue(scene.data, 'before', stringValue(scene.data, 'left', 'Before'));
  const right = stringValue(scene.data, 'after', stringValue(scene.data, 'right', 'After'));
  return (
    <SceneShell {...props} eyebrow={eyebrow}>
      <div style={{display: 'grid', gap: 28, gridTemplateColumns: '1fr 1fr'}}>
        <Panel theme={theme}><div style={{fontSize: 20, fontWeight: 800, opacity: 0.5}}>{leftLabel}</div><div style={{fontSize: 34, fontWeight: 750, marginTop: 20}}>{left}</div></Panel>
        <Panel theme={theme}><div style={{color: accent(theme), fontSize: 20, fontWeight: 800}}>{rightLabel}</div><div style={{fontSize: 34, fontWeight: 750, marginTop: 20}}>{right}</div></Panel>
      </div>
    </SceneShell>
  );
};

export const BeforeAfterScene: SceneComponent = (props) => splitScene(props, 'BEFORE / AFTER', 'BEFORE', 'AFTER');
export const ComparisonScene: SceneComponent = (props) => splitScene(props, 'COMPARISON', 'OPTION A', 'OPTION B');

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
  const items = stringList(scene.data, 'items');
  return (
    <SceneShell {...props} eyebrow="KEY POINTS">
      <div style={{display: 'grid', gap: 18}}>
        {(items.length ? items : scene.emphasis).slice(0, 6).map((item, index) => (
          <Panel key={`${item}-${index}`} theme={theme}><span style={{color: accent(theme), fontWeight: 850, marginRight: 18}}>{String(index + 1).padStart(2, '0')}</span><span style={{fontSize: 28, fontWeight: 650}}>{item}</span></Panel>
        ))}
      </div>
    </SceneShell>
  );
};

export const ProcessScene: SceneComponent = (props) => {
  const {scene, theme} = props;
  const steps = stringList(scene.data, 'steps');
  return (
    <SceneShell {...props} eyebrow="HOW IT WORKS">
      <div style={{display: 'flex', gap: 18}}>
        {(steps.length ? steps : ['Input', 'Process', 'Output']).slice(0, 5).map((step, index) => (
          <div key={`${step}-${index}`} style={{background: index === 0 ? accent(theme) : 'rgba(255,255,255,.07)', borderRadius: 24, color: index === 0 ? '#06110D' : 'inherit', flex: 1, fontSize: 24, fontWeight: 760, padding: '34px 24px', textAlign: 'center'}}>{step}</div>
        ))}
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
  const posts = recordList(scene.data, 'posts');
  const cards = posts.length ? posts : [{author: 'Community', text: supportingText(scene)}];
  return (
    <SceneShell {...props} eyebrow="SOCIAL SIGNAL">
      <div style={{display: 'grid', gap: 20, gridTemplateColumns: cards.length > 1 ? '1fr 1fr' : '1fr'}}>
        {cards.slice(0, 4).map((post, index) => (
          <Panel key={index} theme={theme}>
            <div style={{color: accent(theme), fontSize: 20, fontWeight: 800}}>{typeof post.author === 'string' ? post.author : 'Community'}</div>
            <div style={{fontSize: 27, lineHeight: 1.4, marginTop: 14}}>{typeof post.text === 'string' ? post.text : 'Conversation is accelerating.'}</div>
          </Panel>
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

export const FallbackEditorialScene: SceneComponent = (props) => (
  <SceneShell {...props} eyebrow="EDITORIAL">
    <div style={{fontSize: 24, fontWeight: 700, opacity: 0.5}}>Verified context • restrained visual fallback</div>
  </SceneShell>
);

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
