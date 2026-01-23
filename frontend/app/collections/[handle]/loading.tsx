// app/collections/[handle]/loading.tsx
export default function LoadingCollection() {
  return (
    <div>
      <div style={{ height: 20, width: 220, background:'#f2f2f2', borderRadius:6, marginBottom: '0.75rem' }} />
      <div className="grid grid-cols-2 md:grid-cols-4" style={{ gap: '0.75rem' }}>
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} style={{ display:'flex', flexDirection:'column', gap:'.5rem' }}>
            <div style={{ aspectRatio:'1', background:'#f3f3f3', borderRadius:8 }} />
            <div style={{ height: 14, width:'80%', background:'#eee', borderRadius:6 }} />
            <div style={{ height: 12, width:'40%', background:'#eee', borderRadius:6 }} />
          </div>
        ))}
      </div>
    </div>
  );
}
