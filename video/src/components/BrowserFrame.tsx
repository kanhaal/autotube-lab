import type {PropsWithChildren} from 'react';

export const BrowserFrame = ({children, url}: PropsWithChildren<{url?: string}>) => (
  <div
    style={{
      background: '#10131A',
      border: '1px solid rgba(255,255,255,0.14)',
      borderRadius: 24,
      boxShadow: '0 30px 80px rgba(0,0,0,0.35)',
      overflow: 'hidden',
    }}
  >
    <div
      style={{
        alignItems: 'center',
        background: '#181C25',
        display: 'flex',
        gap: 12,
        minHeight: 58,
        padding: '0 18px',
      }}
    >
      <span style={{background: '#FF6B6B', borderRadius: 99, height: 12, width: 12}} />
      <span style={{background: '#FFD166', borderRadius: 99, height: 12, width: 12}} />
      <span style={{background: '#67F5C5', borderRadius: 99, height: 12, width: 12}} />
      {url ? (
        <div
          style={{
            background: 'rgba(255,255,255,0.06)',
            borderRadius: 10,
            color: 'rgba(255,255,255,0.62)',
            fontSize: 18,
            marginLeft: 12,
            overflow: 'hidden',
            padding: '7px 14px',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            width: '62%',
          }}
        >
          {url}
        </div>
      ) : null}
    </div>
    <div style={{background: '#F5F7FA', color: '#10131A', minHeight: 360, padding: 24}}>{children}</div>
  </div>
);
