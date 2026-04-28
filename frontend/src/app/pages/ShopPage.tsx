import { useEffect, useMemo, useState } from 'react';
import type { Product } from '@/app/data/products';
import { ProductCard } from '@/app/components/ProductCard';

interface ShopPageProps {
  products: Product[];
  loading: boolean;
  onQuickView: (product: Product) => void;
}

export function ShopPage({ products, loading, onQuickView }: ShopPageProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const categories = useMemo(
    () => ['all', ...new Set(products.map((product) => product.collection))],
    [products],
  );

  useEffect(() => {
    if (selectedCategory !== 'all' && !categories.includes(selectedCategory)) {
      setSelectedCategory('all');
    }
  }, [categories, selectedCategory]);
  
  const filteredProducts = selectedCategory === 'all' 
    ? products 
    : products.filter(p => p.collection === selectedCategory);

  return (
    <section className="container mx-auto px-4 sm:px-6 py-12 md:py-16 lg:py-24">
      <div className="mb-8 md:mb-10">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between md:gap-6 mb-6">
          <div>
            <p className="text-small text-muted uppercase tracking-wide">Shop</p>
            <h1 className="font-headline text-2xl sm:text-3xl md:text-4xl">All Products</h1>
          </div>
          <p className="text-small text-muted">{filteredProducts.length} products</p>
        </div>

        {/* Category Filter - Mobile optimized */}
        <div className="flex flex-wrap gap-2 sm:gap-3">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-3 sm:px-4 py-2 rounded-[var(--radius-sm)] text-xs sm:text-sm transition-colors touch-activation ${
                selectedCategory === category
                  ? 'bg-foreground text-white'
                  : 'bg-secondary text-foreground hover:bg-accent/10'
              }`}
            >
              {category === 'all' ? 'All' : category}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-6">
        {loading
          ? Array.from({ length: 12 }).map((_, i) => (
              <div key={i} className="space-y-4 animate-pulse">
                <div className="aspect-[3/4] bg-secondary/50 rounded-[var(--radius-lg)]" />
                <div className="space-y-2 px-1">
                  <div className="h-4 bg-secondary/50 rounded w-3/4" />
                  <div className="h-4 bg-secondary/50 rounded w-1/4" />
                </div>
              </div>
            ))
          : filteredProducts.map((product) => (
              <ProductCard key={product.id} product={product} onQuickView={onQuickView} />
            ))}
      </div>
    </section>
  );
}
