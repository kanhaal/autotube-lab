type ChartPoint = {label: string; value: number};

export const Chart = ({points, accent = '#67F5C5'}: {points: ChartPoint[]; accent?: string}) => {
  const max = Math.max(1, ...points.map((point) => point.value));
  return (
    <div style={{alignItems: 'flex-end', display: 'flex', gap: 24, height: 360}}>
      {points.map((point) => (
        <div key={point.label} style={{alignItems: 'center', display: 'flex', flex: 1, flexDirection: 'column', gap: 12}}>
          <div style={{fontSize: 22, fontWeight: 700}}>{point.value}</div>
          <div style={{background: accent, borderRadius: '16px 16px 6px 6px', height: `${Math.max(6, (point.value / max) * 280)}px`, width: '72%'}} />
          <div style={{fontSize: 20, opacity: 0.7, textAlign: 'center'}}>{point.label}</div>
        </div>
      ))}
    </div>
  );
};
