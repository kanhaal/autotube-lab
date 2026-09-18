import {useCurrentFrame, useVideoConfig} from 'remotion';

import {staggerProgress} from '../polish';

type TimelineItem = {label: string; detail?: string};

export const Timeline = ({items, accent = '#67F5C5'}: {items: TimelineItem[]; accent?: string}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sweep = ((frame * 5) % 260) - 80;

  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 15, position: 'relative'}}>
      {items.map((item, index) => {
        const progress = staggerProgress(frame, fps, index + 1);
        return (
          <div
            key={`${item.label}-${index}`}
            style={{
              display: 'grid',
              gap: 20,
              gridTemplateColumns: '46px 1fr',
              opacity: progress,
              transform: `translate3d(${(1 - progress) * 34}px,${(1 - progress) * 10}px,0) scale(${0.97 + progress * 0.03})`,
            }}
          >
            <div style={{alignItems: 'center', display: 'flex', flexDirection: 'column', position: 'relative'}}>
              <div
                style={{
                  background: accent,
                  border: '4px solid rgba(255,255,255,0.11)',
                  borderRadius: 99,
                  boxShadow: `0 0 0 8px ${accent}12, 0 0 30px ${accent}66`,
                  height: 18,
                  marginTop: 8,
                  position: 'relative',
                  width: 18,
                  zIndex: 2,
                }}
              />
              {index < items.length - 1 ? (
                <div
                  style={{
                    background: `linear-gradient(${accent}, ${accent}44 55%, rgba(255,255,255,0.08))`,
                    flex: 1,
                    marginTop: 6,
                    minHeight: 30,
                    overflow: 'hidden',
                    position: 'relative',
                    transform: `scaleY(${progress})`,
                    transformOrigin: 'top',
                    width: 3,
                  }}
                >
                  <div
                    style={{
                      background: 'rgba(255,255,255,.75)',
                      boxShadow: `0 0 18px ${accent}`,
                      height: 28,
                      left: 0,
                      position: 'absolute',
                      top: sweep,
                      width: '100%',
                    }}
                  />
                </div>
              ) : null}
            </div>
            <div
              style={{
                backdropFilter: 'blur(10px)',
                background: 'linear-gradient(90deg, rgba(255,255,255,.055), transparent)',
                borderLeft: `1px solid ${accent}22`,
                borderRadius: 18,
                padding: '10px 18px 16px',
              }}
            >
              <div style={{fontSize: 32, fontWeight: 850, letterSpacing: -0.55}}>{item.label}</div>
              {item.detail ? <div style={{fontSize: 23, lineHeight: 1.35, marginTop: 6, opacity: 0.58}}>{item.detail}</div> : null}
            </div>
          </div>
        );
      })}
    </div>
  );
};
