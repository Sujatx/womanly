import { useEffect, useState } from 'react';
import { Heart, ShoppingBag, ChevronLeft, ChevronRight, Check } from 'lucide-react';
import { fetchProduct, addToWishlist } from '@/lib/api-client';
import type { APIProduct } from '@/types/api';
import { useToast } from '@/contexts/ToastContext';
import { useAuth } from '@/contexts/AuthContext';

interface ProductDetailPageProps {
  productId: string;
  onAddToCart: (product: APIProduct, details: { quantity: number; variantId: number }) => void;
}

export function ProductDetailPage({ productId, onAddToCart }: ProductDetailPageProps) {
  const [product, setProduct] = useState<APIProduct | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [selectedVariantId, setSelectedVariantId] = useState<number | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [isAddingToWishlist, setIsAddingToWishlist] = useState(false);
  const { showToast } = useToast();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    async function loadProduct() {
      try {
        const data = await fetchProduct(productId);
        setProduct(data);
        if (data?.variants && data.variants.length > 0) {
          setSelectedVariantId(data.variants[0].id);
        }
      } catch (error) {
        showToast('Failed to load product', 'error');
      } finally {
        setLoading(false);
      }
    }
    loadProduct();
  }, [productId, showToast]);

  if (loading) {
    return (
      <section className="container mx-auto px-6 py-16 md:py-24">
        <div className="animate-pulse space-y-8">
          <div className="aspect-square bg-secondary/50 rounded-[var(--radius-lg)]" />
          <div className="space-y-4">
            <div className="h-8 bg-secondary/50 rounded w-3/4" />
            <div className="h-4 bg-secondary/50 rounded w-1/4" />
          </div>
        </div>
      </section>
    );
  }

  if (!product) {
    return (
      <section className="container mx-auto px-6 py-16 md:py-24 text-center">
        <h1 className="font-headline text-2xl mb-4">Product Not Found</h1>
        <a href="#/shop" className="text-accent hover:underline">
          Continue Shopping
        </a>
      </section>
    );
  }

  const selectedVariant = product.variants.find((v) => v.id === selectedVariantId);
  const images = product.product_images.sort((a, b) => a.display_order - b.display_order);
  const displayPrice = selectedVariant?.estimated_total || product.price;
  const isInStock = selectedVariant?.is_available && (selectedVariant?.available_stock || 0) > 0;

  const handleAddToCart = () => {
    if (!selectedVariantId) {
      showToast('Please select a variant', 'error');
      return;
    }
    if (!isInStock) {
      showToast('This item is out of stock', 'error');
      return;
    }
    onAddToCart(product, { quantity, variantId: selectedVariantId });
    showToast('Added to cart!', 'success');
  };

  const handleAddToWishlist = async () => {
    if (!isAuthenticated) {
      showToast('Please login to add items to your wishlist', 'info');
      window.location.hash = '#/auth';
      return;
    }

    try {
      setIsAddingToWishlist(true);
      console.log('[ProductDetail] Adding to wishlist, product.id:', product.id);
      await addToWishlist(Number(product.id));
      showToast('Added to wishlist!', 'success');
    } catch (error) {
      console.error('[ProductDetail] Wishlist error:', error);
      const message = error instanceof Error ? error.message : 'Failed to add to wishlist';
      // Don't show error if already redirecting to auth
      if (!window.location.hash.includes('#/auth')) {
        showToast(message, 'error');
      }
    } finally {
      setIsAddingToWishlist(false);
    }
  };

  const nextImage = () => {
    setSelectedImageIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setSelectedImageIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  return (
    <section className="container mx-auto px-6 py-16 md:py-24">
      <div className="grid lg:grid-cols-2 gap-12">
        {/* Image Gallery */}
        <div>
          <div className="relative aspect-[4/5] bg-secondary rounded-[var(--radius-lg)] overflow-hidden mb-4">
            {images.length > 0 ? (
              <>
                <img
                  src={images[selectedImageIndex]?.image_url || product.thumbnail || ''}
                  alt={images[selectedImageIndex]?.alt_text || product.title}
                  className="w-full h-full object-cover"
                />
                {images.length > 1 && (
                  <>
                    <button
                      onClick={prevImage}
                      className="absolute left-4 top-1/2 -translate-y-1/2 p-2 bg-white/90 rounded-full hover:bg-white transition-colors"
                      aria-label="Previous image"
                    >
                      <ChevronLeft className="w-5 h-5" />
                    </button>
                    <button
                      onClick={nextImage}
                      className="absolute right-4 top-1/2 -translate-y-1/2 p-2 bg-white/90 rounded-full hover:bg-white transition-colors"
                      aria-label="Next image"
                    >
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </>
                )}
              </>
            ) : (
              <div className="w-full h-full flex items-center justify-center text-muted">
                No image available
              </div>
            )}
          </div>

          {/* Thumbnails */}
          {images.length > 1 && (
            <div className="grid grid-cols-4 gap-4">
              {images.slice(0, 4).map((img, idx) => (
                <button
                  key={img.id}
                  onClick={() => setSelectedImageIndex(idx)}
                  className={`aspect-square rounded-[var(--radius-md)] overflow-hidden border-2 transition-colors ${
                    selectedImageIndex === idx ? 'border-accent' : 'border-transparent'
                  }`}
                >
                  <img
                    src={img.image_url}
                    alt={img.alt_text || `Thumbnail ${idx + 1}`}
                    className="w-full h-full object-cover"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-6">
          <div>
            <p className="text-small text-muted uppercase tracking-wide mb-2">
              {product.brand || product.category_slug.replace(/-/g, ' ')}
            </p>
            <h1 className="font-headline text-4xl mb-4">{product.title}</h1>
            <p className="text-2xl font-medium">${displayPrice.toFixed(2)}</p>
          </div>

          <div className="py-6 border-y border-border">
            <p className="text-muted leading-relaxed">{product.description}</p>
          </div>

          {/* Variants */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-3">Select Variant</label>
              <div className="grid grid-cols-2 gap-3">
                {product.variants.map((variant) => (
                  <button
                    key={variant.id}
                    onClick={() => setSelectedVariantId(variant.id)}
                    disabled={!variant.is_available}
                    className={`p-4 border rounded-[var(--radius-sm)] text-left transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${
                      selectedVariantId === variant.id
                        ? 'border-accent bg-accent/5'
                        : 'border-border hover:border-accent/50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-sm">
                          {variant.size && `Size: ${variant.size}`}
                          {variant.color && ` | ${variant.color}`}
                        </p>
                        {variant.material && (
                          <p className="text-xs text-muted mt-1">{variant.material}</p>
                        )}
                        <p className="text-sm mt-1">
                          ${(product.price + variant.price_adjustment).toFixed(2)}
                        </p>
                      </div>
                      {selectedVariantId === variant.id && (
                        <Check className="w-5 h-5 text-accent flex-shrink-0" />
                      )}
                    </div>
                    <p className="text-xs text-muted mt-2">
                      {variant.is_available
                        ? `${variant.available_stock || 0} in stock`
                        : 'Out of stock'}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Quantity */}
            <div>
              <label className="block text-sm font-medium mb-3">Quantity</label>
              <div className="flex items-center gap-3 w-fit">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-4 py-2 border border-border rounded-[var(--radius-sm)] hover:border-accent transition-colors"
                >
                  -
                </button>
                <span className="px-6 py-2 min-w-[4rem] text-center">{quantity}</span>
                <button
                  onClick={() =>
                    setQuantity(Math.min((selectedVariant?.available_stock || 10), quantity + 1))
                  }
                  className="px-4 py-2 border border-border rounded-[var(--radius-sm)] hover:border-accent transition-colors"
                >
                  +
                </button>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4 pt-6">
            <button
              onClick={handleAddToCart}
              disabled={!isInStock}
              className="flex-1 bg-foreground text-white py-4 rounded-[var(--radius-sm)] hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <ShoppingBag className="w-5 h-5" />
              {isInStock ? 'Add to Cart' : 'Out of Stock'}
            </button>
            <button
              onClick={handleAddToWishlist}
              disabled={isAddingToWishlist}
              className="p-4 border border-border rounded-[var(--radius-sm)] hover:border-accent hover:text-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Add to wishlist"
            >
              <Heart className="w-5 h-5" />
            </button>
          </div>

          {/* Additional Info */}
          <div className="space-y-4 pt-8 border-t border-border text-sm text-muted">
            <p>SKU: {selectedVariant?.sku || 'N/A'}</p>
            <p>Category: {product.category_slug.replace(/-/g, ' ')}</p>
            <p>Free shipping on orders over $100</p>
            <p>Easy returns within 30 days</p>
          </div>
        </div>
      </div>
    </section>
  );
}
