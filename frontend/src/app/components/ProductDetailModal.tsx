import { useEffect, useState } from 'react';
import { X, Heart, ChevronLeft, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import type { Product, CartItem } from '@/app/data/products';

interface ProductDetailModalProps {
  product: Product | null;
  onClose: () => void;
  onAddToCart: (item: Omit<CartItem, 'id' | 'name' | 'collection' | 'price' | 'salePrice' | 'images' | 'description' | 'sizes' | 'colors' | 'inStock' | 'badge'>) => void;
}

export function ProductDetailModal({ product, onClose, onAddToCart }: ProductDetailModalProps) {
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [selectedSize, setSelectedSize] = useState<string>('');
  const [selectedColor, setSelectedColor] = useState<string>('');
  const [quantity, setQuantity] = useState(1);

  // Reset selections when product changes
  useEffect(() => {
    if (product) {
      setSelectedImageIndex(0);
      setSelectedSize(product.sizes[0] || '');
      setSelectedColor(product.colors[0] || '');
      setQuantity(1);
    }
  }, [product]);

  // Lock scroll and handle ESC
  useEffect(() => {
    if (!product) return;

    document.body.style.overflow = 'hidden';
    document.body.style.paddingRight = '0px';

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);

    return () => {
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
      document.removeEventListener('keydown', handleEscape);
    };
  }, [product, onClose]);

  if (!product) return null;

  const handleAddToCart = () => {
    if (!selectedSize || !selectedColor) return;

    onAddToCart({
      quantity,
      selectedSize,
      selectedColor,
    });

    // Show success message (could be enhanced with toast)
    alert('Added to cart!');
  };

  const nextImage = () => {
    setSelectedImageIndex((prev) => (prev + 1) % product.images.length);
  };

  const prevImage = () => {
    setSelectedImageIndex((prev) => (prev - 1 + product.images.length) % product.images.length);
  };

  return (
    <AnimatePresence>
      {product && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.35, ease: [0.2, 0.8, 0.2, 1] }}
            className="fixed inset-0 bg-backdrop-black backdrop-blur-sm z-[var(--z-backdrop)]"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.35, ease: [0.2, 0.8, 0.2, 1] }}
            className="fixed inset-4 md:inset-8 z-[var(--z-modal)] overflow-hidden"
            role="dialog"
            aria-modal="true"
            aria-labelledby="product-title"
          >
            <div className="h-full bg-white rounded-[var(--radius-lg)] shadow-2xl overflow-hidden flex flex-col">
              {/* Header */}
              <div className="flex items-center justify-between p-4 md:p-6 border-b border-border">
                <h2 id="product-title" className="text-xl md:text-2xl font-medium">
                  {product.name}
                </h2>
                <button
                  onClick={onClose}
                  className="p-2 text-foreground hover:text-accent transition-colors"
                  aria-label="Close product details"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto">
                <div className="grid md:grid-cols-2 gap-8 p-4 md:p-8">
                  {/* Gallery */}
                  <div>
                    {/* Main Image */}
                    <div className="relative aspect-[4/5] bg-secondary rounded-[var(--radius-md)] overflow-hidden mb-4">
                      <img
                        src={product.images[selectedImageIndex]}
                        alt={`${product.name} - Image ${selectedImageIndex + 1}`}
                        className="w-full h-full object-cover"
                      />
                      
                      {/* Navigation Arrows */}
                      {product.images.length > 1 && (
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
                    </div>

                    {/* Thumbnails */}
                    {product.images.length > 1 && (
                      <div className="grid grid-cols-4 gap-2">
                        {product.images.map((img, idx) => (
                          <button
                            key={idx}
                            onClick={() => setSelectedImageIndex(idx)}
                            className={`aspect-square rounded-[var(--radius-sm)] overflow-hidden border-2 transition-colors ${
                              selectedImageIndex === idx
                                ? 'border-accent'
                                : 'border-transparent hover:border-border'
                            }`}
                          >
                            <img
                              src={img}
                              alt={`${product.name} thumbnail ${idx + 1}`}
                              className="w-full h-full object-cover"
                            />
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Details */}
                  <div className="md:sticky md:top-0">
                    <p className="text-small text-muted uppercase tracking-wide mb-2">
                      {product.collection}
                    </p>
                    <h3 className="text-3xl md:text-4xl font-headline mb-4">
                      {product.name}
                    </h3>
                    
                    {/* Price */}
                    <div className="flex items-center gap-3 mb-6">
                      <span className="text-2xl font-medium">
                        ${product.salePrice || product.price}
                      </span>
                      {product.salePrice && product.salePrice < product.price && (
                        <span className="text-lg text-muted line-through">
                          ${product.price}
                        </span>
                      )}
                    </div>

                    {/* Description */}
                    <p className="text-muted leading-relaxed mb-6">
                      {product.description}
                    </p>

                    {/* Color Selection */}
                    <div className="mb-6">
                      <label className="block mb-3 font-medium">
                        Color: {selectedColor}
                      </label>
                      <div className="flex gap-3">
                        {product.colors.map((color) => (
                          <button
                            key={color}
                            onClick={() => setSelectedColor(color)}
                            className={`px-4 py-2 border-2 rounded-[var(--radius-sm)] transition-colors ${
                              selectedColor === color
                                ? 'border-accent bg-accent/5'
                                : 'border-border hover:border-accent/50'
                            }`}
                            aria-pressed={selectedColor === color}
                          >
                            {color}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Size Selection */}
                    <div className="mb-6">
                      <div className="flex items-center justify-between mb-3">
                        <label className="font-medium">
                          Size: {selectedSize}
                        </label>
                        <button className="text-small text-accent hover:underline">
                          Size Guide
                        </button>
                      </div>
                      <div className="grid grid-cols-5 gap-2">
                        {product.sizes.map((size) => (
                          <button
                            key={size}
                            onClick={() => setSelectedSize(size)}
                            className={`py-3 border-2 rounded-[var(--radius-sm)] transition-colors ${
                              selectedSize === size
                                ? 'border-accent bg-accent/5'
                                : 'border-border hover:border-accent/50'
                            }`}
                            aria-pressed={selectedSize === size}
                          >
                            {size}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Quantity */}
                    <div className="mb-6">
                      <label className="block mb-3 font-medium">Quantity</label>
                      <div className="flex items-center border border-border rounded-[var(--radius-sm)] w-fit">
                        <button
                          onClick={() => setQuantity(Math.max(1, quantity - 1))}
                          className="px-4 py-3 hover:bg-secondary transition-colors"
                          aria-label="Decrease quantity"
                        >
                          -
                        </button>
                        <span className="px-6 py-3 min-w-[4rem] text-center">
                          {quantity}
                        </span>
                        <button
                          onClick={() => setQuantity(quantity + 1)}
                          className="px-4 py-3 hover:bg-secondary transition-colors"
                          aria-label="Increase quantity"
                        >
                          +
                        </button>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="space-y-3">
                      <button
                        onClick={handleAddToCart}
                        disabled={!product.inStock}
                        className="w-full bg-foreground text-white py-4 rounded-[var(--radius-sm)] hover:bg-accent transition-colors disabled:bg-muted disabled:cursor-not-allowed"
                      >
                        {product.inStock ? 'Add to Cart' : 'Out of Stock'}
                      </button>
                      <button className="w-full border-2 border-border py-4 rounded-[var(--radius-sm)] hover:border-accent transition-colors flex items-center justify-center gap-2">
                        <Heart className="w-5 h-5" />
                        Add to Wishlist
                      </button>
                    </div>

                    {/* Additional Info */}
                    <div className="mt-8 pt-8 border-t border-border space-y-4 text-small">
                      <p className="flex justify-between">
                        <span className="text-muted">SKU</span>
                        <span>{product.id.toUpperCase()}</span>
                      </p>
                      <p className="flex justify-between">
                        <span className="text-muted">Collection</span>
                        <span>{product.collection}</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
