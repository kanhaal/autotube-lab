import type {CSSProperties} from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';

import {SourceBadge} from '../components/SourceBadge';
import {SceneRenderer} from '../scenes/SceneRenderer';
import type {AssetRecordV1, CameraPreset, CaptionCueV1, RenderEffectsProfileV1, SceneSpecV1, ShotStyle} from '../types';
import {headlineWordProgress, narrationEmphasisBeat} from '../vfx';
import type {ChannelTheme} from '../themes/types';
import {cameraRigStyle, microBeatEnvelope} from './camera';
import {GpuDepthStage} from './GpuDepthStage';
import {EditorialMedia, resolveEditorialMedia} from './media';
import {resolveShotStyle} from './shotDirector';

type DirectedSceneProps = {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  assets: AssetRecordV1[];
  captions: CaptionCueV1[];
  durationInFrames: number;
  absoluteFrom: number;
  format: 'long' | 'short';
  profile?: RenderEffectsProfileV1;
};

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));

const DepthBackground = ({
  theme,
  profile,
  opacity = 1,
}: {
  theme: ChannelTheme;
  profile?: RenderEffectsProfileV1;
  opacity?: number;
}) =>
  profile?.gpu_depth === false ? (
    <AbsoluteFill
      style={{
        background:
          `radial-gradient(circle at 72% 20%, ${theme.secondary}22, transparent 34%), ` +
          `radial-gradient(circle at 18% 82%, ${theme.accent}16, transparent 38%), ${theme.background}`,
        opacity,
      }}
    />
  ) : (
    <GpuDepthStage theme={theme} opacity={opacity} />
  );

const defaultCameraFor = (style: ShotStyle, theme: ChannelTheme): CameraPreset => {
  const energetic = theme.transitionFamily === 'snap';
  switch (style) {
    case 'source_full':
      return energetic ? 'handheld_micro' : 'dolly_in';
    case 'source_detail':
      return 'rack_push';
    case 'data_full':
      return 'crane_down';
    case 'graphic_3d':
      return energetic ? 'orbit_right' : 'orbit_left';
    case 'split_screen':
      return 'dolly_out';
    case 'chapter':
      return energetic ? 'whip_pan' : 'dolly_in';
    case 'kinetic_text':
      return energetic ? 'whip_pan' : 'locked';
    case 'editorial':
    default:
      return 'rack_push';
  }
};

const wordTokens = (scene: SceneSpecV1) =>
  (scene.headline || scene.narration).trim().split(/\s+/).filter(Boolean);

const KineticHeadline = ({
  scene,
  theme,
  format,
}: {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  format: 'long' | 'short';
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const words = wordTokens(scene);
  const emphasis = new Set(
    scene.emphasis
      .flatMap((value) => value.toLowerCase().split(/\s+/))
      .map((value) => value.replace(/[^a-z0-9]/g, ''))
      .filter(Boolean),
  );
  const size = format === 'short' ? (words.length > 9 ? 64 : 82) : words.length > 10 ? 74 : 98;
  return (
    <div
      style={{
        alignItems: 'flex-start',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        justifyContent: format === 'short' ? 'center' : 'flex-end',
        padding: format === 'short' ? '120px 64px 300px' : '90px 110px 110px',
        position: 'relative',
        zIndex: 4,
      }}
    >
      <div
        style={{
          color: theme.accent,
          fontSize: format === 'short' ? 18 : 20,
          fontWeight: 900,
          letterSpacing: 3,
          marginBottom: 20,
          textTransform: 'uppercase',
        }}
      >
        {scene.purpose || 'THE SIGNAL'}
      </div>
      <div
        style={{
          fontSize: size,
          fontWeight: 950,
          letterSpacing: format === 'short' ? -3.6 : -4.2,
          lineHeight: 0.92,
          maxWidth: format === 'short' ? 940 : 1500,
        }}
      >
        {words.map((word, index) => {
          const progress = headlineWordProgress(frame, fps, index);
          const token = word.toLowerCase().replace(/[^a-z0-9]/g, '');
          const accented = emphasis.has(token) || (words.length <= 7 && index === words.length - 1);
          return (
            <span
              key={word + '-' + index}
              style={{
                color: accented ? theme.accent : '#FFFFFF',
                display: 'inline-block',
                filter: 'blur(' + ((1 - progress) * 8).toFixed(2) + 'px)',
                marginRight: format === 'short' ? 13 : 18,
                opacity: progress,
                textShadow: accented ? '0 0 34px ' + theme.accent + '35' : 'none',
                transform:
                  'translate3d(0,' +
                  ((1 - progress) * 54).toFixed(2) +
                  'px,0) scale(' +
                  (0.91 + progress * 0.09).toFixed(4) +
                  ')',
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
            fontSize: format === 'short' ? 28 : 30,
            fontWeight: 620,
            lineHeight: 1.35,
            marginTop: 28,
            maxWidth: format === 'short' ? 880 : 1120,
            opacity: 0.66,
          }}
        >
          {scene.subheadline}
        </div>
      ) : null}
    </div>
  );
};

const SourceFullShot = (props: DirectedSceneProps) => {
  const {scene, theme, assets, format} = props;
  const asset = resolveEditorialMedia(scene, assets);
  if (!asset) return <KineticHeadline scene={scene} theme={theme} format={format} />;
  const target = scene.camera?.target ?? {};
  const positionX = clamp01(Number(target.x ?? 0.5)) * 100;
  const positionY = clamp01(Number(target.y ?? 0.38)) * 100;
  return (
    <AbsoluteFill style={{background: theme.background, overflow: 'hidden'}}>
      <EditorialMedia
        asset={asset}
        style={{
          objectPosition: positionX.toFixed(1) + '% ' + positionY.toFixed(1) + '%',
          transform: 'scale(1.035)',
        }}
      />
      <AbsoluteFill
        style={{
          background:
            'linear-gradient(90deg, rgba(3,6,11,.86) 0%, rgba(3,6,11,.52) 35%, transparent 68%), ' +
            'linear-gradient(0deg, rgba(3,6,11,.88) 0%, transparent 42%)',
        }}
      />
      <div
        style={{
          bottom: format === 'short' ? 300 : 90,
          left: format === 'short' ? 58 : 86,
          maxWidth: format === 'short' ? 870 : 880,
          position: 'absolute',
          zIndex: 5,
        }}
      >
        <SourceBadge label={asset.source_name || asset.source_url || 'Verified source'} />
        <div
          style={{
            fontSize: format === 'short' ? 64 : 64,
            fontWeight: 920,
            letterSpacing: -2.8,
            lineHeight: 0.98,
            marginTop: 18,
          }}
        >
          {scene.headline || scene.narration}
        </div>
        {scene.subheadline ? (
          <div style={{fontSize: format === 'short' ? 27 : 26, lineHeight: 1.35, marginTop: 16, opacity: 0.72}}>
            {scene.subheadline}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

const SourceDetailShot = (props: DirectedSceneProps) => {
  const {scene, theme, assets, format} = props;
  const asset = resolveEditorialMedia(scene, assets);
  if (!asset) return <KineticHeadline scene={scene} theme={theme} format={format} />;
  return (
    <AbsoluteFill style={{background: '#04070C', overflow: 'hidden'}}>
      <DepthBackground theme={theme} profile={props.profile} opacity={0.7} />
      <div
        style={{
          border: '1px solid ' + theme.border,
          borderRadius: format === 'short' ? 30 : 34,
          boxShadow: '0 38px 110px rgba(0,0,0,.46), 0 0 70px ' + theme.accent + '18',
          inset: format === 'short' ? '110px 48px 330px' : '72px 90px 100px',
          overflow: 'hidden',
          position: 'absolute',
          transform: 'perspective(1500px) rotateY(-1.3deg) rotateX(.6deg)',
        }}
      >
        <EditorialMedia asset={asset} style={{objectPosition: 'center top'}} />
      </div>
      <div
        style={{
          background: 'rgba(4,8,13,.76)',
          borderLeft: '4px solid ' + theme.accent,
          bottom: format === 'short' ? 270 : 82,
          fontSize: format === 'short' ? 28 : 26,
          fontWeight: 760,
          left: format === 'short' ? 54 : 110,
          maxWidth: format === 'short' ? 900 : 760,
          padding: '14px 18px',
          position: 'absolute',
          zIndex: 5,
        }}
      >
        {scene.subheadline || scene.headline || scene.narration}
      </div>
    </AbsoluteFill>
  );
};

const DataFullShot = (props: DirectedSceneProps) => {
  const {scene, theme, assets, durationInFrames, captions, absoluteFrom, format} = props;
  const {fps} = useVideoConfig();
  const frame = useCurrentFrame();
  const beat = narrationEmphasisBeat(
    captions,
    (absoluteFrom + frame) / Math.max(1, fps),
    scene.emphasis,
  );
  return (
    <AbsoluteFill style={{background: theme.background, overflow: 'hidden'}}>
      <DepthBackground theme={theme} profile={props.profile} opacity={0.82} />
      <div
        style={{
          inset: format === 'short' ? '70px 34px 255px' : '24px 34px 36px',
          position: 'absolute',
          zIndex: 3,
        }}
      >
        <SceneRenderer
          scene={scene}
          theme={theme}
          assets={assets}
          durationInFrames={durationInFrames}
          narrationBeat={beat}
        />
      </div>
    </AbsoluteFill>
  );
};

const Graphic3DShot = (props: DirectedSceneProps) => {
  const {scene, theme, assets, durationInFrames, captions, absoluteFrom, format} = props;
  const {fps} = useVideoConfig();
  const frame = useCurrentFrame();
  const beat = narrationEmphasisBeat(
    captions,
    (absoluteFrom + frame) / Math.max(1, fps),
    scene.emphasis,
  );
  return (
    <AbsoluteFill style={{background: theme.background, overflow: 'hidden'}}>
      <DepthBackground theme={theme} profile={props.profile} />
      <div
        style={{
          background: 'rgba(6,10,16,.62)',
          border: '1px solid ' + theme.border,
          borderRadius: 34,
          boxShadow: '0 46px 140px rgba(0,0,0,.48), 0 0 85px ' + theme.accent + '18',
          inset: format === 'short' ? '105px 46px 320px' : '70px 110px 90px',
          overflow: 'hidden',
          position: 'absolute',
          transform: 'perspective(1500px) rotateY(-2.2deg) rotateX(1deg)',
          transformOrigin: 'center',
          zIndex: 3,
        }}
      >
        <SceneRenderer
          scene={scene}
          theme={theme}
          assets={assets}
          durationInFrames={durationInFrames}
          narrationBeat={beat}
        />
      </div>
    </AbsoluteFill>
  );
};

const SplitScreenShot = (props: DirectedSceneProps) => {
  const {scene, theme, assets, format} = props;
  const asset = resolveEditorialMedia(scene, assets);
  const left = String(scene.data.before ?? scene.data.left ?? 'Before');
  const right = String(scene.data.after ?? scene.data.right ?? 'After');
  return (
    <AbsoluteFill
      style={{
        background: theme.background,
        display: 'grid',
        gridTemplateColumns: format === 'short' ? '1fr' : '1fr 1fr',
        gridTemplateRows: format === 'short' ? '1fr 1fr' : '1fr',
        overflow: 'hidden',
      }}
    >
      <div style={{overflow: 'hidden', position: 'relative'}}>
        {asset ? (
          <EditorialMedia asset={asset} style={{filter: 'saturate(.82) brightness(.72)'}} />
        ) : (
          <DepthBackground theme={theme} profile={props.profile} opacity={0.7} />
        )}
        <div
          style={{
            bottom: 42,
            fontSize: format === 'short' ? 34 : 46,
            fontWeight: 900,
            left: 46,
            position: 'absolute',
            right: 40,
            textShadow: '0 4px 24px rgba(0,0,0,.7)',
          }}
        >
          {left}
        </div>
      </div>
      <div
        style={{
          background: 'linear-gradient(145deg,' + theme.accent + '22,' + theme.secondary + '12), #080B12',
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        <DepthBackground theme={theme} profile={props.profile} opacity={0.72} />
        <div
          style={{
            bottom: 42,
            color: theme.accent,
            fontSize: format === 'short' ? 34 : 46,
            fontWeight: 900,
            left: 46,
            position: 'absolute',
            right: 40,
          }}
        >
          {right}
        </div>
      </div>
      <div
        style={{
          background: theme.accent,
          boxShadow: '0 0 30px ' + theme.accent + '66',
          height: format === 'short' ? 3 : '100%',
          left: format === 'short' ? 0 : '50%',
          position: 'absolute',
          top: format === 'short' ? '50%' : 0,
          width: format === 'short' ? '100%' : 3,
          zIndex: 5,
        }}
      />
    </AbsoluteFill>
  );
};

const ChapterShot = ({
  scene,
  theme,
  format,
  profile,
}: {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  format: 'long' | 'short';
  profile?: RenderEffectsProfileV1;
}) => (
  <AbsoluteFill style={{background: theme.background, overflow: 'hidden'}}>
    <DepthBackground theme={theme} profile={profile} />
    <div
      style={{
        alignItems: 'flex-start',
        display: 'flex',
        flexDirection: 'column',
        inset: 0,
        justifyContent: 'center',
        padding: format === 'short' ? '80px 64px 250px' : '70px 120px',
        position: 'absolute',
        zIndex: 3,
      }}
    >
      <div style={{color: theme.accent, fontSize: 20, fontWeight: 900, letterSpacing: 4}}>NEXT</div>
      <div
        style={{
          fontSize: format === 'short' ? 82 : 118,
          fontWeight: 950,
          letterSpacing: -5,
          lineHeight: 0.9,
          marginTop: 22,
          maxWidth: 1400,
        }}
      >
        {scene.headline || scene.subheadline || scene.narration}
      </div>
    </div>
  </AbsoluteFill>
);

const MicroBeatLayer = ({
  scene,
  theme,
  frame,
  fps,
  format,
}: {
  scene: SceneSpecV1;
  theme: ChannelTheme;
  frame: number;
  fps: number;
  format: 'long' | 'short';
}) => {
  const active = (scene.micro_beats ?? [])
    .map((beat) => ({
      beat,
      strength: microBeatEnvelope(frame, fps, Number(beat.at ?? 0)),
    }))
    .sort((a, b) => b.strength - a.strength)[0];
  if (!active || active.strength <= 0.01) return null;
  const strength = active.strength;
  const kind = active.beat.kind;
  if (kind === 'flash') {
    return <AbsoluteFill style={{background: theme.accent, opacity: strength * 0.13, zIndex: 30}} />;
  }
  if (kind === 'underline') {
    return (
      <div
        style={{
          background: theme.accent,
          bottom: format === 'short' ? 305 : 88,
          boxShadow: '0 0 24px ' + theme.accent + '66',
          height: 4,
          left: format === 'short' ? 60 : 90,
          position: 'absolute',
          transform: 'scaleX(' + strength.toFixed(4) + ')',
          transformOrigin: 'left',
          width: format === 'short' ? 540 : 650,
          zIndex: 30,
        }}
      />
    );
  }
  if (kind === 'tag_pop') {
    return (
      <div
        style={{
          display: 'flex',
          gap: 8,
          position: 'absolute',
          right: format === 'short' ? 48 : 78,
          top: format === 'short' ? 100 : 56,
          transform: 'scale(' + (0.8 + strength * 0.2).toFixed(4) + ')',
          zIndex: 30,
        }}
      >
        {scene.emphasis.slice(0, 3).map((tag) => (
          <span
            key={tag}
            style={{
              background: 'rgba(5,8,13,.82)',
              border: '1px solid ' + theme.accent + '66',
              borderRadius: 999,
              color: theme.accent,
              fontSize: 16,
              fontWeight: 850,
              padding: '8px 12px',
            }}
          >
            {tag}
          </span>
        ))}
      </div>
    );
  }
  if (kind === 'callout') {
    const target = scene.camera?.target ?? {x: 0.62, y: 0.38};
    return (
      <div
        style={{
          border: '2px solid ' + theme.accent,
          boxShadow: '0 0 34px ' + theme.accent + '55',
          height: 120,
          left: 'calc(' + clamp01(Number(target.x ?? 0.62) - 0.08) * 100 + '%)',
          opacity: strength,
          position: 'absolute',
          top: 'calc(' + clamp01(Number(target.y ?? 0.38) - 0.05) * 100 + '%)',
          width: 210,
          zIndex: 30,
        }}
      />
    );
  }
  return null;
};

export const DirectedScene = (props: DirectedSceneProps) => {
  const {scene, theme, durationInFrames, format, profile} = props;
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const shot = resolveShotStyle(scene);
  const camera = scene.camera ?? {};
  const preset = camera.preset ?? defaultCameraFor(shot, theme);
  const baseCamera = cameraRigStyle(
    preset,
    frame,
    durationInFrames,
    fps,
    Number(camera.intensity ?? (format === 'short' ? 1.02 : 0.82)) * Number(profile?.camera_intensity ?? 1),
    camera.target ?? {},
  );

  const strongest = (scene.micro_beats ?? []).reduce(
    (best, beat) => {
      const strength = microBeatEnvelope(frame, fps, Number(beat.at ?? 0)) * Number(profile?.microbeat_strength ?? 1);
      return strength > best.strength ? {kind: beat.kind, strength} : best;
    },
    {kind: '', strength: 0},
  );
  const baseTransform = typeof baseCamera.transform === 'string' ? baseCamera.transform : '';
  let microTransform = '';
  let microFilter = '';
  if (strongest.kind === 'focus_punch') {
    microTransform = ' scale(' + (1 + strongest.strength * 0.035).toFixed(4) + ')';
  } else if (strongest.kind === 'shake') {
    microTransform =
      ' translate3d(' +
      (Math.sin(frame * 5.3) * 7 * strongest.strength).toFixed(2) +
      'px,' +
      (Math.cos(frame * 6.7) * 4 * strongest.strength).toFixed(2) +
      'px,0)';
  } else if (strongest.kind === 'crop_shift') {
    microTransform = ' translate3d(' + (22 * strongest.strength).toFixed(2) + 'px,0,0)';
  }
  if (strongest.kind === 'focus_punch') {
    microFilter = 'brightness(' + (1 + strongest.strength * 0.08).toFixed(3) + ')';
  }

  let shotNode: React.ReactNode;
  if (shot === 'source_full') shotNode = <SourceFullShot {...props} />;
  else if (shot === 'source_detail') shotNode = <SourceDetailShot {...props} />;
  else if (shot === 'data_full') shotNode = <DataFullShot {...props} />;
  else if (shot === 'graphic_3d') shotNode = <Graphic3DShot {...props} />;
  else if (shot === 'split_screen') shotNode = <SplitScreenShot {...props} />;
  else if (shot === 'chapter') shotNode = <ChapterShot scene={scene} theme={theme} format={format} profile={profile} />;
  else shotNode = <AbsoluteFill style={{background: theme.background}}><DepthBackground theme={theme} profile={profile} opacity={0.9} /><KineticHeadline scene={scene} theme={theme} format={format} /></AbsoluteFill>;

  return (
    <AbsoluteFill style={{background: theme.background, overflow: 'hidden'}}>
      <div
        style={{
          ...baseCamera,
          filter: microFilter || undefined,
          height: '100%',
          transform: baseTransform + microTransform,
          width: '100%',
        }}
      >
        {shotNode}
      </div>
      <MicroBeatLayer scene={scene} theme={theme} frame={frame} fps={fps} format={format} />
    </AbsoluteFill>
  );
};
