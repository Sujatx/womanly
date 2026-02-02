import { useState } from 'react';
import { Heart } from 'lucide-react';
import { motion } from 'motion/react';
import type { Product } from '@/app/data/products';

interface ProductCardProps {
  product: Product;
  onQuickView?: (product: Product) => void;
}

export function ProductCard({ product, onQuickView }: ProductCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [imageIndex, setImageIndex] = useState(0);

  const displayPrice = product.salePrice || product.price;
  const hasDiscount = product.salePrice && product.salePrice < product.price;

  return (
    <article
      className="group relative bg-white rounded-[var(--radius-md)] overflow-hidden"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setImageIndex(0);
      }}
    >
      {/* Badge */}
      {product.badge && (
        <div className="absolute top-3 left-3 z-10">
          <span className="inline-block bg-white px-3 py-1 rounded-[var(--radius-sm)] text-small font-medium uppercase tracking-wide shadow-[var(--shadow-soft)]">
            {product.badge}
          </span>
        </div>
      )}

      {/* Wishlist Button */}
      <button
        className="absolute top-3 right-3 z-10 p-2 bg-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-[var(--motion-micro)] hover:bg-accent hover:text-white"
        aria-label={`Add ${product.name} to wishlist`}
      >
        <Heart className="w-4 h-4" />
      </button>

      {/* Image */}
      <a
        href={`#product/${product.id}`}
        onClick={(e) => {
          if (onQuickView) {
            e.preventDefault();
            onQuickView(product);
          }
        }}
        className="block"
      >
        <div className="relative aspect-[4/5] bg-secondary overflow-hidden">
          {product.images.map((img, idx) => (
            <motion.img
              key={idx}
              src={img}
              alt={idx === 0 ? product.name : `${product.name} alternate view ${idx + 1}`}
              className="absolute inset-0 w-full h-full object-cover"
              initial={{ opacity: idx === 0 ? 1 : 0 }}
              animate={{
                opacity: imageIndex === idx ? 1 : 0,
                scale: isHovered ? 1.03 : 1
              }}
              transition={{
                opacity: { duration: 0.3 },
                scale: { duration: 0.35, ease: [0.2, 0.8, 0.2, 1] }
              }}
              onMouseEnter={() => {
                if (idx > 0 && isHovered) setImageIndex(idx);
              }}
            />
          ))}

          {/* Out of stock overlay */}
          {!product.inStock && (
            <div className="absolute inset-0 bg-white/80 flex items-center justify-center">
              <span className="text-nav text-muted">Out of Stock</span>
            </div>
          )}
        </div>
      </a>

      {/* Metadata */}
      <div className="p-4">
        <p className="text-small text-muted mb-1 uppercase tracking-wide">
          {product.collection}
        </p>
        <h3 className="font-medium mb-2">
          <a
            href={`#product/${product.id}`}
            className="hover:text-accent transition-colors"
            onClick={(e) => {
              if (onQuickView) {
                e.preventDefault();
                onQuickView(product);
              }
            }}
          >
            {product.name}
          </a>
        </h3>
        <div className="flex items-center gap-2">
          <span className={hasDiscount ? 'text-accent font-medium' : ''}>
            ${displayPrice}
          </span>
          {hasDiscount && (
            <span className="text-small text-muted line-through">
              ${product.price}
            </span>
          )}
        </div>

        {/* Color swatches (shown on hover) */}
        {product.colors.length > 1 && (
          <div className="flex gap-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity duration-[var(--motion-micro)]">
            {product.colors.slice(0, 4).map((color) => (
              <button
                key={color}
                className="w-6 h-6 rounded-full border-2 border-border hover:border-accent transition-colors"
                style={{
                  backgroundColor:
                    color.toLowerCase() === 'white' ? '#fff' :
                    color.toLowerCase() === 'black' ? '#000' :
                    color.toLowerCase() === 'ivory' ? '#FFFFF0' :
                    color.toLowerCase() === 'camel' ? '#C19A6B' :
                    color.toLowerCase() === 'champagne' ? '#F7E7CE' :
                    color.toLowerCase() === 'navy' ? '#000080' :
                    color.toLowerCase() === 'grey' || color.toLowerCase() === 'gray' ? '#808080' :
                    color.toLowerCase() === 'charcoal' ? '#36454F' :
                    color.toLowerCase() === 'cream' ? '#FFFDD0' :
                    color.toLowerCase() === 'sand' ? '#C2B280' :
                    color.toLowerCase() === 'olive' ? '#808000' :
                    color.toLowerCase() === 'indigo' ? '#4B0082' :
                    color.toLowerCase() === 'ecru' ? '#C2B280' :
                    color.toLowerCase() === 'chocolate' ? '#7B3F00' :
                    '#ccc'
                }}
                aria-label={color}
                title={color}
              />
            ))}
          </div>
        )}
      </div>
    </article>
  );
}
