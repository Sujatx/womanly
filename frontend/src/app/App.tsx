import { useState } from 'react';
import { Navbar } from '@/app/components/Navbar';
import { SearchModal } from '@/app/components/SearchModal';
import { Hero } from '@/app/components/Hero';
import { ProductCard } from '@/app/components/ProductCard';
import { ProductDetailModal } from '@/app/components/ProductDetailModal';
import { CartDrawer } from '@/app/components/CartDrawer';
import { Footer } from '@/app/components/Footer';
import { products } from '@/app/data/products';
import type { Product, CartItem } from '@/app/data/products';

function App() {
  const [searchOpen, setSearchOpen] = useState(false);
  const [cartOpen, setCartOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);

  const handleAddToCart = (product: Product, details: { quantity: number; selectedSize: string; selectedColor: string }) => {
    const newItem: CartItem = {
      ...product,
      ...details,
    };

    setCartItems((prev) => {
      // Check if item with same product, size, and color exists
      const existingIndex = prev.findIndex(
        (item) =>
          item.id === newItem.id &&
          item.selectedSize === newItem.selectedSize &&
          item.selectedColor === newItem.selectedColor
      );

      if (existingIndex >= 0) {
        // Update quantity
        const updated = [...prev];
        updated[existingIndex].quantity += newItem.quantity;
        return updated;
      }

      // Add new item
      return [...prev, newItem];
    });

    setSelectedProduct(null);
    setCartOpen(true);
  };

  const handleUpdateQuantity = (id: string, quantity: number) => {
    if (quantity < 1) {
      handleRemoveFromCart(id);
      return;
    }

    setCartItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, quantity } : item
      )
    );
  };

  const handleRemoveFromCart = (id: string) => {
    setCartItems((prev) => prev.filter((item) => item.id !== id));
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Skip to content link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-accent text-white px-4 py-2 rounded-[var(--radius-sm)] z-[var(--z-toast)]"
      >
        Skip to main content
      </a>

      {/* Navbar */}
      <Navbar
        onSearchOpen={() => setSearchOpen(true)}
        onCartOpen={() => setCartOpen(true)}
        cartItemCount={cartItems.reduce((sum, item) => sum + item.quantity, 0)}
      />

      {/* Main Content */}
      <main id="main-content" className="flex-1">
        {/* Hero Section */}
        <Hero
          variant="full-bleed"
          image="https://images.unsplash.com/photo-1483985988355-763728e1935b?w=1600&q=90"
          heading="Spring Collection 2026"
          subheading="Discover our latest arrivals crafted with timeless elegance and modern sensibility"
          ctaText="Explore Collection"
          ctaHref="#collection"
        />

        {/* Featured Collections */}
        <section className="container mx-auto px-6 py-16 md:py-24">
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
                href={`#collection/${collection.toLowerCase()}`}
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
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-[var(--motion-major)]"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
                <div className="absolute bottom-8 left-8 right-8 text-white">
                  <h3 className="font-headline text-3xl mb-2">{collection}</h3>
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

        {/* Product Grid */}
        <section id="collection" className="bg-secondary py-16 md:py-24">
          <div className="container mx-auto px-6">
            <div className="flex items-center justify-between mb-12">
              <h2 className="font-headline">New Arrivals</h2>
              <div className="flex items-center gap-4">
                <span className="text-small text-muted hidden md:inline">
                  {products.length} Products
                </span>
                <select className="px-6 py-3 bg-white/40 backdrop-blur-xl border border-white/60 rounded-full text-foreground text-small font-medium cursor-pointer hover:bg-white/60 hover:border-white/80 transition-all duration-[var(--motion-micro)] appearance-none bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMS41TDYgNi41TDExIDEuNSIgc3Ryb2tlPSIjMTExMDE0IiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+')] bg-[length:12px] bg-[right_1rem_center] bg-no-repeat pr-10 shadow-sm focus:outline-none focus:ring-0 focus:border-white/80">
                  <option>Featured</option>
                  <option>Price: Low to High</option>
                  <option>Price: High to Low</option>
                  <option>Newest</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {products.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onQuickView={setSelectedProduct}
                />
              ))}
            </div>
          </div>
        </section>

        {/* Editorial Section */}
        <Hero
          variant="image-right"
          image="https://images.unsplash.com/photo-1487412912498-0447578fcca8?w=800&q=90"
          heading="Crafted for the Modern Woman"
          subheading="Every piece in our collection is thoughtfully designed and ethically produced. We believe in quality over quantity, creating garments that last beyond seasons."
          ctaText="Our Story"
          ctaHref="#about"
        />

        {/* Values Section */}
        <section className="container mx-auto px-6 py-16 md:py-24">
          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent/10 flex items-center justify-center">
                <svg className="w-8 h-8 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-xl font-medium mb-2">Quality Craftsmanship</h3>
              <p className="text-muted">
                Each garment is meticulously crafted using the finest materials and traditional techniques
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent/10 flex items-center justify-center">
                <svg className="w-8 h-8 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-medium mb-2">Sustainable Practices</h3>
              <p className="text-muted">
                We're committed to ethical production and environmental responsibility at every step
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent/10 flex items-center justify-center">
                <svg className="w-8 h-8 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-medium mb-2">Thoughtful Design</h3>
              <p className="text-muted">
                Timeless pieces designed to transcend trends and become cherished wardrobe staples
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <Footer />

      {/* Modals & Overlays (rendered as portals) */}
      <SearchModal isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
      
      <ProductDetailModal
        product={selectedProduct}
        onClose={() => setSelectedProduct(null)}
        onAddToCart={(details) => {
          if (selectedProduct) {
            handleAddToCart(selectedProduct, details);
          }
        }}
      />

      <CartDrawer
        isOpen={cartOpen}
        onClose={() => setCartOpen(false)}
        items={cartItems}
        onUpdateQuantity={handleUpdateQuantity}
        onRemove={handleRemoveFromCart}
      />
    </div>
  );
}

export default App;