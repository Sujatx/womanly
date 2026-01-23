// app/page.tsx
// Home: hero + categories + featured products from DummyJSON.

import Link from 'next/link';
import { getProducts, toCard } from '@/lib/api-client';
import { ProductCard } from '@/components/ProductCard';

export default async function Home() {
  // Fetch a small set for a fast LCP
  // We can pass 'womens-dresses' or similar as category if we want specific featured items
  // Or just fetch latest. Let's fetch latest 8.
  const featuredData = await getProducts(1, 8);
  const featured = featuredData.items.map(toCard);

  return (
    <div className="space-y-8">
      {/* Hero */}
      <section
        style={{
          borderRadius: 16,
          padding: '2rem',
          background:
            'linear-gradient(135deg, rgba(17,17,17,.9), rgba(17,17,17,.6)), url(https://images.unsplash.com/photo-1520975693419-6349b6ee6e9f?q=80&w=1400&auto=format&fit=crop) center/cover',
          color: '#fff',
        }}
      >
        <div style={{ maxWidth: 880 }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 700, lineHeight: 1.1 }}>
            New drops for the season
          </h1>
          <p style={{ marginTop: '.5rem', opacity: 0.9 }}>
            Dresses, tops, and edits picked for everyday bold. Free returns in 14 days.
          </p>
          <div style={{ marginTop: '1rem', display: 'flex', gap: '.5rem' }}>
            <Link
              href="/collections/new-in"
              className="rounded"
              style={{ background: '#fff', color: '#111', padding: '.6rem .9rem', borderRadius: 10, fontWeight: 600 }}
            >
              Shop New In →
            </Link>
          </div>
        </div>
      </section>

      {/* Shop by category */}
      <section className="space-y-3">
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Shop by category</h2>
        <div className="grid grid-cols-2 md:grid-cols-4" style={{ gap: '0.75rem' }}>
          {[
            { href: '/collections/new-in', label: 'New In' },
            { href: '/collections/dresses', label: 'Dresses' },
            { href: '/collections/tops', label: 'Tops' },
            { href: '/collections/bottoms', label: 'Bottoms' },
          ].map((c) => (
            <Link
              key={c.href}
              href={c.href}
              className="rounded"
              style={{
                border: '1px solid #eee',
                padding: '1rem',
                borderRadius: 12,
                background: '#fafafa',
                textAlign: 'center',
                fontWeight: 600,
              }}
            >
              {c.label}
            </Link>
          ))}
        </div>
      </section>

      {/* Featured products */}
      <section className="space-y-3">
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Featured</h2>
        {featured.length ? (
          <div className="grid grid-cols-2 md:grid-cols-4" style={{ gap: '0.75rem' }}>
            {featured.map((p) => (
              <ProductCard key={p.handle} product={p} />
            ))}
          </div>
        ) : (
          <p className="muted">Nothing to show right now.</p>
        )}
      </section>
    </div>
  );
}
