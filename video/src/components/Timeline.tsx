import {useCurrentFrame, useVideoConfig} from 'remotion';

import {staggerProgress} from '../polish';

type TimelineItem = {label: string; detail?: string};

export const Timeline = ({items, accent = '#67F5C5'}: {items: TimelineItem[]; accent?: string}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 18}}>
      {items.map((item, index) => {
        const progress = staggerProgress(frame, fps, index + 1);
        return (
          <div
            key={`${item.label}-${index}`}
            style={{
              display: 'grid',
              gap: 20,
              gridTemplateColumns: '42px 1fr',
              opacity: progress,
              transform: `translateX(${(1 - progress) * 28}px)`,
            }}
          >
            <div style={{alignItems: 'center', display: 'flex', flexDirection: 'column'}}>
              <div
                style={{
                  background: accent,
                  border: '4px solid rgba(255,255,255,0.10)',
                  borderRadius: 99,
                  boxShadow: `0 0 24px ${accent}55`,
                  height: 18,
                  marginTop: 8,
                  width: 18,
                }}
              />
              {index < items.length - 1 ? (
                <div
                  style={{
                    background: `linear-gradient(${accent}88, rgba(255,255,255,0.10))`,
                    flex: 1,
                    marginTop: 6,
                    minHeight: 28,
                    transform: `scaleY(${progress})`,
                    transformOrigin: 'top',
                    width: 2,
                  }}
                />
              ) : null}
            </div>
            <div style={{paddingBottom: 16}}>
              <div style={{fontSize: 32, fontWeight: 800, letterSpacing: -0.4}}>{item.label}</div>
              {item.detail ? <div style={{fontSize: 23, marginTop: 6, opacity: 0.62}}>{item.detail}</div> : null}
            </div>
          </div>
        );
      })}
    </div>
  );
};
