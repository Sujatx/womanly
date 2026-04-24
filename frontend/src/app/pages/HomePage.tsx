import { Hero } from '@/app/components/Hero';
import { ProductCard } from '@/app/components/ProductCard';
import type { Product } from '@/app/data/products';

interface HomePageProps {
  products: Product[];
  loading: boolean;
  onQuickView: (product: Product) => void;
}

export function HomePage({ products, loading, onQuickView }: HomePageProps) {
  return (
    <>
      <Hero
        variant="full-bleed"
        image="https://images.unsplash.com/photo-1483985988355-763728e1935b?w=1600&q=90"
        heading="Spring Collection 2026"
        subheading="Discover our latest arrivals crafted with timeless elegance and modern sensibility"
        ctaText="Explore Collection"
        ctaHref="#/shop"
      />

      <section id="collections" className="container mx-auto px-6 py-16 md:py-24">
        <div className="text-center mb-12">
          <h2 className="font-headline mb-4">Featured Collections</h2>
          <p className="text-lg text-muted max-w-2xl mx-auto">
            Curated pieces that embody quiet luxury and effortless sophistication
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {['Evening', 'Essentials', 'Knitwear'].map((collection) => (
            <a
              key={collection}
              href="#/shop"
              className="group relative aspect-[3/4] rounded-[var(--radius-lg)] overflow-hidden"
            >
              <img
                src={
                  collection === 'Evening'
                    ? 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=800&q=90'
                    : collection === 'Essentials'
                    ? 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800&q=90'
                    : 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=800&q=90'
                }
                alt={collection}
                loading="lazy"
                decoding="async"
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-[var(--motion-major)]"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
              <div className="absolute bottom-8 left-8 right-8 text-white">
                <h3 className="font-headline mb-2">{collection}</h3>
                <p className="text-small opacity-90">
                  {collection === 'Evening' && 'Elegant pieces for special occasions'}
                  {collection === 'Essentials' && 'Timeless wardrobe foundations'}
                  {collection === 'Knitwear' && 'Luxurious knits for every season'}
                </p>
              </div>
            </a>
          ))}
        </div>
      </section>

      <section id="shop" className="bg-secondary py-16 md:py-24">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between mb-12">
            <h2 className="font-headline">New Arrivals</h2>
            <a href="#/shop" className="text-small text-accent hover:underline">
              View all
            </a>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {loading
              ? Array.from({ length: 8 }).map((_, i) => (
                  <div key={i} className="space-y-4 animate-pulse">
                    <div className="aspect-[3/4] bg-secondary/50 rounded-[var(--radius-lg)]" />
                    <div className="space-y-2">
                      <div className="h-4 bg-secondary/50 rounded w-3/4" />
                      <div className="h-4 bg-secondary/50 rounded w-1/4" />
                    </div>
                  </div>
                ))
              : products.slice(0, 8).map((product) => (
                  <ProductCard key={product.id} product={product} onQuickView={onQuickView} />
                ))}
          </div>
        </div>
      </section>

      <Hero
        variant="image-right"
        image="https://images.unsplash.com/photo-1487412912498-0447578fcca8?w=800&q=90"
        heading="Crafted for the Modern Woman"
        subheading="Every piece in our collection is thoughtfully designed and ethically produced. We believe in quality over quantity, creating garments that last beyond seasons."
        ctaText="Our Story"
        ctaHref="#/about"
      />

      <section id="about" className="container mx-auto px-6 py-16 md:py-24">
        <div className="grid md:grid-cols-3 gap-12">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent/10 flex items-center justify-center">
              <svg className="w-8 h-8 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="font-medium mb-2">Quality Craftsmanship</h3>
            <p className="text-muted">Each garment is meticulously crafted using the finest materials.</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent/10 flex items-center justify-center">
              <svg className="w-8 h-8 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="font-medium mb-2">Sustainable Practices</h3>
            <p className="text-muted">We are committed to ethical production and environmental responsibility.</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent/10 flex items-center justify-center">
              <svg className="w-8 h-8 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 className="font-medium mb-2">Thoughtful Design</h3>
            <p className="text-muted">Timeless pieces designed to transcend trends.</p>
          </div>
        </div>
      </section>
    </>
  );
}
