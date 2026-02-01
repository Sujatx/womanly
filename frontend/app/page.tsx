// app/page.tsx
import Link from 'next/link';
import { getProducts, toCard } from '@/lib/api-client';
import { ProductCard } from '@/components/ProductCard';
import { ArrowRight } from 'lucide-react';

export default async function Home() {
  const featuredData = await getProducts(1, 8);
  const featured = featuredData.items.map(toCard);

  return (
    <div className="space-y-24" style={{ paddingBottom: '8rem' }}>
      {/* VEXO Editorial Hero */}
      <section className="vexo-hero">
        <div className="bg-text">WOMANLY</div>
        
        <h1 className="vexo-hero-title">
          GEAR UP EVERY SEASON EVERY WORKOUT!
        </h1>
        
        <div style={{ display: 'flex', gap: '1rem', zIndex: 10 }}>
          <Link href="/collections/new-in" className="vexo-button">
            SHOP NOW <ArrowRight size={20} />
          </Link>
          <Link href="/collections/all" className="vexo-button vexo-button-outline">
            EXPLORE ALL
          </Link>
        </div>

        {/* Hero Background Image Cutout (Mockup) */}
        <div className="vexo-hero-image-wrapper">
          <img 
            src="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1200&auto=format&fit=crop" 
            alt="Hero Model"
            style={{ width: '100%', height: 'auto', borderRadius: 'var(--radius-lg)' }}
          />
        </div>
      </section>

      {/* Seasonal Collections */}
      <section className="container grid grid-cols-1 md:grid-cols-2" style={{ gap: '2rem' }}>
        <div className="collection-card">
          <img src="https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=1000&auto=format&fit=crop" alt="Winter" className="media-cover" />
          <div className="collection-card-content">
            <span className="collection-tag">01/WINTER 2025</span>
            <div>
              <h2 style={{ color: 'white' }}>TOP WORKOUT GEAR FOR PEAK PERFORMANCE!</h2>
              <Link href="/collections/winter" className="vexo-button" style={{ marginTop: '1rem', padding: '0.6rem 1.5rem', fontSize: '0.8rem' }}>
                VIEW COLLECTION
              </Link>
            </div>
          </div>
        </div>

        <div className="collection-card">
          <img src="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=1000&auto=format&fit=crop" alt="Summer" className="media-cover" />
          <div className="collection-card-content">
            <span className="collection-tag">02/SUMMER 2025</span>
            <div>
              <h2 style={{ color: 'white' }}>LATEST STYLES AND INNOVATIONS IN GEAR.</h2>
              <Link href="/collections/summer" className="vexo-button" style={{ marginTop: '1rem', padding: '0.6rem 1.5rem', fontSize: '0.8rem' }}>
                VIEW COLLECTION
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Trending Background Text Section */}
      <section className="bg-text-container">
        <div className="bg-text">TRENDING</div>
        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '3rem' }}>
            <h2 style={{ margin: 0 }}>NEXT WORKOUT!</h2>
            <Link href="/collections/trending" className="text-sm" style={{ fontWeight: 900, textDecoration: 'underline' }}>VIEW ALL TRENDING</Link>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4" style={{ gap: '2.5rem' }}>
            {featured.map((p) => (
              <ProductCard key={p.handle} product={p} />
            ))}
          </div>
        </div>
      </section>

      {/* Feature Section: High Fashion Blurb */}
      <section className="container" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center' }}>
        <div className="hover-zoom" style={{ borderRadius: 'var(--radius-lg)' }}>
          <img src="https://images.unsplash.com/photo-1539109136881-3be0616acf4b?q=80&w=800&auto=format&fit=crop" alt="Fashion" className="media-cover" />
        </div>
        <div style={{ maxWidth: '400px' }}>
          <p style={{ fontSize: '1.2rem', color: 'var(--fg)', fontWeight: 600 }}>
            Stay warm, stay fit. Our winter workout wear blends insulation with flexibility to keep you going in the toughest conditions.
          </p>
          <Link href="/about" className="text-sm" style={{ fontWeight: 900, borderBottom: '2px solid var(--fg)' }}>LEARN MORE ABOUT OUR TECH</Link>
        </div>
      </section>
    </div>
  );
}
