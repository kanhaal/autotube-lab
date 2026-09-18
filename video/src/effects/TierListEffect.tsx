import {spring, useCurrentFrame, useVideoConfig} from 'remotion';

import type {EffectComponentProps} from './types';

export type TierListEffectProps = EffectComponentProps;

const TIER_NAMES = ['S', 'A', 'B', 'C', 'D'] as const;

const readTiers = (value: unknown): Record<string, string[]> => {
  if (!value || typeof value !== 'object') return {};
  const raw = value as Record<string, unknown>;
  const result: Record<string, string[]> = {};
  for (const tier of TIER_NAMES) {
    const items = raw[tier];
    result[tier] = Array.isArray(items)
      ? items.filter((item): item is string => typeof item === 'string')
      : [];
  }
  return result;
};

export const TierListEffect = ({effect, children, theme}: TierListEffectProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const tiers = readTiers(effect.tiers);
  const hasItems = TIER_NAMES.some((tier) => tiers[tier]?.length);

  return (
    <>
      {children}
      {hasItems ? (
        <div
          style={{
            backdropFilter: 'blur(22px)',
            background: 'rgba(6,8,14,.82)',
            border: `1px solid ${theme.border}`,
            borderRadius: 24,
            bottom: '8%',
            boxShadow: '0 30px 100px rgba(0,0,0,.45)',
            left: '8%',
            padding: 16,
            position: 'absolute',
            right: '8%',
            top: '12%',
            zIndex: 69,
          }}
        >
          {TIER_NAMES.map((tier, tierIndex) => (
            <div
              key={tier}
              style={{
                alignItems: 'center',
                borderBottom: tier === 'D' ? 0 : `1px solid ${theme.border}`,
                display: 'grid',
                gridTemplateColumns: '70px 1fr',
                minHeight: '18%',
              }}
            >
              <div style={{color: tierIndex < 2 ? theme.accent : theme.foreground, fontSize: 36, fontWeight: 950, textAlign: 'center'}}>
                {tier}
              </div>
              <div style={{display: 'flex', flexWrap: 'wrap', gap: 12, padding: 12}}>
                {(tiers[tier] || []).map((item, itemIndex) => {
                  const progress = spring({
                    frame: frame - tierIndex * 5 - itemIndex * 4,
                    fps,
                    config: {damping: 11, stiffness: 165, mass: 0.8},
                  });
                  return (
                    <div
                      key={`${tier}-${item}`}
                      style={{
                        background: `linear-gradient(145deg, ${theme.accent}22, rgba(255,255,255,.06))`,
                        border: `1px solid ${theme.border}`,
                        borderRadius: 14,
                        fontSize: 22,
                        fontWeight: 800,
                        opacity: progress,
                        padding: '12px 16px',
                        transform: `translateY(${(1 - progress) * -34}px) scale(${0.78 + progress * 0.22})`,
                      }}
                    >
                      {item}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </>
  );
};
