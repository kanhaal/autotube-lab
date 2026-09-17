type TimelineItem = {label: string; detail?: string};

export const Timeline = ({items, accent = '#67F5C5'}: {items: TimelineItem[]; accent?: string}) => (
  <div style={{display: 'flex', flexDirection: 'column', gap: 26}}>
    {items.map((item, index) => (
      <div key={`${item.label}-${index}`} style={{display: 'grid', gap: 20, gridTemplateColumns: '36px 1fr'}}>
        <div style={{alignItems: 'center', display: 'flex', flexDirection: 'column'}}>
          <div style={{background: accent, borderRadius: 99, height: 16, marginTop: 8, width: 16}} />
          {index < items.length - 1 ? <div style={{background: 'rgba(255,255,255,0.18)', flex: 1, marginTop: 8, width: 2}} /> : null}
        </div>
        <div style={{paddingBottom: 18}}>
          <div style={{fontSize: 32, fontWeight: 750}}>{item.label}</div>
          {item.detail ? <div style={{fontSize: 24, marginTop: 6, opacity: 0.68}}>{item.detail}</div> : null}
        </div>
      </div>
    ))}
  </div>
);
