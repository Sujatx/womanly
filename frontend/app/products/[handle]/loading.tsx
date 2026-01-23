// app/products/[handle]/loading.tsx
export default function LoadingProduct() {
  return (
    <div className="grid" style={{ gridTemplateColumns: '1fr', gap: '2rem' }}>
      <div style={{ aspectRatio:'1', background:'#f3f3f3', borderRadius:8 }} />
      <div>
        <div style={{ height: 24, width: 260, background:'#eee', borderRadius:6, marginBottom:'.5rem' }} />
        <div style={{ height: 16, width: 120, background:'#eee', borderRadius:6, marginBottom:'1rem' }} />
        <div style={{ display:'flex', gap:'.5rem', marginBottom:'1rem' }}>
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} style={{ height: 32, width: 72, background:'#f2f2f2', borderRadius:6 }} />
          ))}
        </div>
        <div style={{ height: 40, width: 200, background:'#f2f2f2', borderRadius:8 }} />
      </div>
    </div>
  );
}
