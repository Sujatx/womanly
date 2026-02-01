'use client';

import Link from 'next/link';
import { useWishlist } from '@/lib/wishlist';
import * as React from 'react';
import { Heart } from 'lucide-react';
import { toast } from 'sonner';

type Img = { url: string; altText?: string };
type Money = { amount: string; currencyCode: string };

function formatPrice(price: Money) {
  const n = Number(price.amount);
  try {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: price.currencyCode || 'USD',
      maximumFractionDigits: 0,
    }).format(n);
  } catch {
    return `${n} ${price.currencyCode}`;
  }
}

export function ProductCard({ product }: { product: any }) {
  const { has, toggle } = useWishlist();
  const inWL = has(product.handle);

  return (
    <div className="vexo-card" style={{ opacity: product.isOutOfStock ? 0.7 : 1 }}>
      <Link href={`/products/${product.handle}`} aria-label={product.title}>
        <div className="vexo-card-image hover-zoom">
          {product.image?.url ? (
            <img
              src={product.image.url}
              alt={product.image.altText || product.title}
              className="media-cover"
            />
          ) : (
            <div className="skeleton media-cover" />
          )}

          {/* Out of Stock Overlay */}
          {product.isOutOfStock && (
            <div style={{
              position: 'absolute',
              inset: 0,
              background: 'rgba(255,255,255,0.6)',
              display: 'grid',
              placeItems: 'center',
              zIndex: 5
            }}>
              <span style={{ 
                fontSize: '0.7rem', 
                fontWeight: 900, 
                background: 'var(--fg)', 
                color: 'white', 
                padding: '0.5rem 1rem', 
                borderRadius: 'var(--radius-pill)',
                letterSpacing: '0.05em'
              }}>OUT OF STOCK</span>
            </div>
          )}

          {/* Wishlist Icon Overlay */}
          <button
            type="button"
            aria-label={inWL ? 'Remove from wishlist' : 'Add to wishlist'}
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              toggle({
                id: product.handle,
                title: product.title,
                image: product.image,
                price: Number(product.price.amount),
                currencyCode: product.price.currencyCode,
              });
              if (inWL) toast.info('ITEM REMOVED');
              else toast.success('ADDED TO WISHLIST');
            }}
            style={{
              position: 'absolute',
              top: '1rem',
              right: '1rem',
              background: 'rgba(255,255,255,0.8)',
              border: 'none',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              display: 'grid',
              placeItems: 'center',
              cursor: 'pointer',
              zIndex: 10
            }}
          >
            <Heart size={16} fill={inWL ? "#000" : "none"} strokeWidth={inWL ? 0 : 2} />
          </button>
        </div>

        {/* Floating Info Badge */}
        <div className="vexo-card-info">
          <div>
            <p className="vexo-card-title">{product.title}</p>
            <p className="text-xs" style={{ margin: 0, opacity: 0.6 }}>WINTER COLLECTION</p>
          </div>
          <p className="vexo-card-price">{formatPrice(product.price)}</p>
        </div>
      </Link>
    </div>
  );
}