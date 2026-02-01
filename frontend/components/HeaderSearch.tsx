'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Search, X, ArrowRight } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export default function HeaderSearch() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState('');
  const [items, setItems] = useState<any[]>([]);
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => { document.body.style.overflow = 'unset'; };
  }, [open]);

  useEffect(() => {
    const handle = setTimeout(async () => {
      if (!q.trim()) {
        setItems([]);
        return;
      }
      try {
        const res = await fetch(`${API_URL}/products?q=${encodeURIComponent(q)}&limit=6`);
        const data = await res.json();
        setItems(data.items || []);
      } catch {
        setItems([]);
      }
    }, 300);
    return () => clearTimeout(handle);
  }, [q]);

  function handleSelect(id: number) {
    setOpen(false);
    setQ('');
    router.push(`/products/${id}`);
  }

  return (
    <>
      <button 
        onClick={() => setOpen(true)}
        style={{ 
          background: 'none', 
          border: 'none', 
          cursor: 'pointer', 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.75rem',
          fontSize: '0.75rem',
          fontWeight: 900,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          opacity: 0.6,
          transition: 'opacity 0.2s'
        }}
        onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
        onMouseLeave={(e) => e.currentTarget.style.opacity = '0.6'}
      >
        <Search size={18} />
        SEARCH
      </button>

      {open && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'var(--bg)',
          zIndex: 10000,
          display: 'flex',
          flexDirection: 'column',
          padding: '2rem'
        }}>
          <div className="bg-text">SEARCH</div>
          
          <div className="container" style={{ position: 'relative', zIndex: 1, width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '4rem' }}>
              <button 
                onClick={() => setOpen(false)}
                className="vexo-button vexo-button-outline"
                style={{ width: '64px', height: '64px', padding: 0, borderRadius: '50%', display: 'grid', placeItems: 'center' }}
              >
                <X size={24} />
              </button>
            </div>

            <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
              <input
                ref={inputRef}
                type="text"
                placeholder="TYPE TO SEARCH..."
                value={q}
                onChange={(e) => setQ(e.target.value)}
                style={{
                  width: '100%',
                  background: 'none',
                  border: 'none',
                  borderBottom: '4px solid var(--fg)',
                  fontSize: '4rem',
                  fontWeight: 900,
                  padding: '1rem 0',
                  outline: 'none',
                  textTransform: 'uppercase'
                }}
              />

              <div style={{ marginTop: '4rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '2rem' }}>
                {items.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleSelect(item.id)}
                    style={{
                      display: 'flex',
                      gap: '1.5rem',
                      alignItems: 'center',
                      textAlign: 'left',
                      background: 'rgba(255,255,255,0.3)',
                      padding: '1.5rem',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border)',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                  >
                    <div style={{ width: '80px', height: '100px', borderRadius: 'var(--radius-xs)', overflow: 'hidden', flexShrink: 0 }}>
                      <img src={item.thumbnail || item.product_images?.[0]?.image_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <p style={{ fontSize: '0.9rem', fontWeight: 900, margin: 0, textTransform: 'uppercase' }}>{item.title}</p>
                      <p style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--muted)', marginTop: '0.25rem' }}>${item.price}</p>
                    </div>
                    <ArrowRight size={20} style={{ opacity: 0.3 }} />
                  </button>
                ))}
              </div>

              {q && items.length === 0 && (
                <p style={{ textAlign: 'center', marginTop: '4rem', fontWeight: 900, opacity: 0.2, fontSize: '2rem' }}>NO RESULTS FOUND</p>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}