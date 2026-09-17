export const SourceBadge = ({label}: {label: string}) => (
  <div
    style={{
      alignSelf: 'flex-start',
      background: 'rgba(255,255,255,0.08)',
      border: '1px solid rgba(255,255,255,0.15)',
      borderRadius: 999,
      fontSize: 22,
      fontWeight: 650,
      letterSpacing: 0.3,
      padding: '10px 18px',
    }}
  >
    {label}
  </div>
);
