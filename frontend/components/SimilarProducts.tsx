// components/SimilarProducts.tsx
// Sidebar list: shows similar products by category or falls back to any products.
// - Client component (fetch happens on the client).
// - Uses next/image for optimized thumbs.
// - Links to /products/{id} via Next navigation.

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';

type Row = { id: number; title: string; price: number; thumbnail?: string; images?: string[] };

export default function SimilarProducts({
  category,
  limit = 8,
  excludeId,
  title = 'Similar products',
}: {
  category?: string;
  limit?: number;
  excludeId?: number;
  title?: string;
}) {
  const [items, setItems] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    async function fetchProducts() {
      setLoading(true);
      try {
        // Try category first if provided
        let list: Row[] = [];
        if (category) {
          const res = await fetch(
            `https://dummyjson.com/products/category/${encodeURIComponent(category)}?limit=${limit}`,
            { cache: 'no-store' }
          );
          const data = await res.json();
          list = (data.products || []) as Row[];
        }
        // Fallback: any products if category missing or came back empty
        if (!list?.length) {
          const res2 = await fetch(`https://dummyjson.com/products?limit=${limit}`, { cache: 'no-store' });
          const data2 = await res2.json();
          list = (data2.products || []) as Row[];
        }
        // Exclude current product if provided
        if (excludeId) list = list.filter(p => p.id !== excludeId);
        if (alive) setItems(list);
      } catch {
        // Last-chance fallback: empty list; UI still renders safely
        if (alive) setItems([]);
      } finally {
        if (alive) setLoading(false);
      }
    }
    fetchProducts();
    return () => { alive = false; };
  }, [category, limit, excludeId]);

  return (
    <aside aria-label={title}>
      <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '.5rem' }}>{title}</h3>
      {loading && <p className="muted">Loading…</p>}
      {!loading && items.length === 0 && <p className="muted">Showing soon…</p>}

      <div style={{ display: 'grid', gap: '.75rem' }}>
        {items.map((p) => (
          <Link
            key={p.id}
            href={`/products/${p.id}`}
            style={{
              display: 'grid',
              gridTemplateColumns: '84px 1fr',
              gap: '.6rem',
              alignItems: 'center',
              border: '1px solid #eee',
              borderRadius: 10,
              padding: '.5rem',
              background: '#fff',
            }}
          >
            <div
              style={{
                width: 84,
                height: 112,
                borderRadius: 8,
                overflow: 'hidden',
                background: '#f3f3f3',
              }}
            >
              {p.thumbnail ? (
                <Image
                  src={p.thumbnail}
                  alt=""
                  width={300}
                  height={400}
                  sizes="84px"
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  loading="lazy"
                />
              ) : null}
            </div>
            <div style={{ minWidth: 0 }}>
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 500,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
                title={p.title}
              >
                {p.title}
              </div>
              <div style={{ fontSize: 12, opacity: 0.85 }}>₹{p.price}</div>
            </div>
          </Link>
        ))}
      </div>
    </aside>
  );
}
