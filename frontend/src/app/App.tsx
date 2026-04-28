import { lazy, Suspense, useEffect, useMemo, useState } from 'react';
import { Navbar } from '@/app/components/Navbar';
import { Footer } from '@/app/components/Footer';
import type { Product, CartItem } from '@/app/data/products';
import type { APIProduct } from '@/types/api';
import { fetchProducts } from '@/lib/api-client';
import { transformProduct } from '@/lib/transformers';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';

const SearchModal = lazy(() => import('@/app/components/SearchModal').then((mod) => ({ default: mod.SearchModal })));
const ProductDetailModal = lazy(() => import('@/app/components/ProductDetailModal').then((mod) => ({ default: mod.ProductDetailModal })));
const CartDrawer = lazy(() => import('@/app/components/CartDrawer').then((mod) => ({ default: mod.CartDrawer })));

const HomePage = lazy(() => import('@/app/pages/HomePage').then((mod) => ({ default: mod.HomePage })));
const ShopPage = lazy(() => import('@/app/pages/ShopPage').then((mod) => ({ default: mod.ShopPage })));
const WishlistPage = lazy(() => import('@/app/pages/WishlistPage').then((mod) => ({ default: mod.WishlistPage })));
const OrdersPage = lazy(() => import('@/app/pages/OrdersPage').then((mod) => ({ default: mod.OrdersPage })));
const CheckoutPage = lazy(() => import('@/app/pages/CheckoutPage').then((mod) => ({ default: mod.CheckoutPage })));
const AuthPage = lazy(() => import('@/app/pages/AuthPage').then((mod) => ({ default: mod.AuthPage })));
const VerifyEmailPage = lazy(() => import('@/app/pages/VerifyEmailPage').then((mod) => ({ default: mod.VerifyEmailPage })));
const ProductDetailPage = lazy(() => import('@/app/pages/ProductDetailPage').then((mod) => ({ default: mod.ProductDetailPage })));
const AboutPage = lazy(() => import('@/app/pages/AboutPage').then((mod) => ({ default: mod.AboutPage })));
const ProfilePage = lazy(() => import('@/app/pages/ProfilePage').then((mod) => ({ default: mod.ProfilePage })));
const AddressesPage = lazy(() => import('@/app/pages/AddressesPage').then((mod) => ({ default: mod.AddressesPage })));

function normalizeHashPath(rawHash: string): string {
  const hashWithoutPrefix = rawHash.replace(/^#/, '') || '/';
  const pathOnly = hashWithoutPrefix.split('?')[0] || '/';
  const path = pathOnly;
  const withLeadingSlash = path.startsWith('/') ? path : `/${path}`;
  return withLeadingSlash.length > 1 ? withLeadingSlash.replace(/\/$/, '') : withLeadingSlash;
}

function App() {
  const [routePath, setRoutePath] = useState(() => normalizeHashPath(window.location.hash));
  const [searchOpen, setSearchOpen] = useState(false);
  const [cartOpen, setCartOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();

  useEffect(() => {
    const onHashChange = () => {
      setRoutePath(normalizeHashPath(window.location.hash));
      // Scroll to top on route change
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    window.addEventListener('hashchange', onHashChange);
    if (!window.location.hash) {
      window.location.hash = '#/';
    }

    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  useEffect(() => {
    async function loadProducts() {
      try {
        const apiProducts = await fetchProducts(1, 100);
        const transformed = apiProducts.map(transformProduct);
        setProducts(transformed);
      } catch (err) {
        console.error('Failed to load products', err);
      } finally {
        setLoading(false);
      }
    }
    loadProducts();
  }, []);

  const cartItemCount = useMemo(
    () => cartItems.reduce((sum, item) => sum + item.quantity, 0),
    [cartItems],
  );

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
    showToast('Added to cart!', 'success');
  };

  const handleAddToCartFromAPI = (product: APIProduct, details: { quantity: number; variantId: number }) => {
    // Transform API product to Product format and add to cart
    const variant = product.variants.find(v => v.id === details.variantId);
    if (!variant) {
      showToast('Variant not found', 'error');
      return;
    }

    const transformedProduct = transformProduct(product);
    const cartItem: CartItem = {
      ...transformedProduct,
      quantity: details.quantity,
      selectedSize: variant.size || '',
      selectedColor: variant.color || '',
    };

    setCartItems((prev) => {
      const existingIndex = prev.findIndex(
        (item) =>
          item.id === cartItem.id &&
          item.selectedSize === cartItem.selectedSize &&
          item.selectedColor === cartItem.selectedColor
      );

      if (existingIndex >= 0) {
        const updated = [...prev];
        updated[existingIndex].quantity += cartItem.quantity;
        return updated;
      }

      return [...prev, cartItem];
    });

    setCartOpen(true);
  };

  const handleUpdateQuantity = (itemKey: string, quantity: number) => {
    if (quantity < 1) {
      handleRemoveFromCart(itemKey);
      return;
    }

    setCartItems((prev) =>
      prev.map((item) =>
        `${item.id}-${item.selectedSize}-${item.selectedColor}` === itemKey
          ? { ...item, quantity }
          : item
      )
    );
  };

  const handleRemoveFromCart = (itemKey: string) => {
    setCartItems((prev) =>
      prev.filter((item) => `${item.id}-${item.selectedSize}-${item.selectedColor}` !== itemKey),
    );
  };

  function renderRoute() {
    // Extract product ID from hash if it's a product detail route
    const productMatch = routePath.match(/^\/product\/(.+)$/);
    if (productMatch) {
      return <ProductDetailPage productId={productMatch[1]} onAddToCart={handleAddToCartFromAPI} />;
    }

    switch (routePath) {
      case '/':
        return <HomePage products={products} loading={loading} onQuickView={setSelectedProduct} />;
      case '/shop':
        return <ShopPage products={products} loading={loading} onQuickView={setSelectedProduct} />;
      case '/wishlist':
        return <WishlistPage />;
      case '/orders':
        return <OrdersPage />;
      case '/checkout':
        return <CheckoutPage items={cartItems} />;
      case '/auth':
      case '/login':
      case '/signup':
        return <AuthPage />;
      case '/auth/verify':
        return <VerifyEmailPage />;
      case '/about':
        return <AboutPage />;
      case '/profile':
        return <ProfilePage />;
      case '/addresses':
        return <AddressesPage />;
      default:
        return (
          <section className="container mx-auto px-6 py-16 md:py-24">
            <h1 className="font-headline mb-4">Page Not Found</h1>
            <p className="text-muted mb-6">The page you are looking for does not exist.</p>
            <a href="#/" className="inline-block bg-foreground text-white px-6 py-3 rounded-[var(--radius-sm)] hover:bg-accent transition-colors">
              Back to Home
            </a>
          </section>
        );
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <Navbar
        onSearchOpen={() => setSearchOpen(true)}
        onCartOpen={() => setCartOpen(true)}
        cartItemCount={cartItemCount}
      />

      {/* Main Content */}
      <main id="main-content" className="flex-1">
        <Suspense fallback={<div className="container mx-auto px-6 py-16 text-muted">Loading...</div>}>
          {renderRoute()}
        </Suspense>
      </main>

      {/* Footer */}
      <Footer />

      {/* Modals & Overlays (rendered as portals) */}
      <Suspense fallback={null}>
        <SearchModal isOpen={searchOpen} onClose={() => setSearchOpen(false)} products={products} />

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
      </Suspense>
    </div>
  );
}

export default App;