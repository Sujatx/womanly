// components/ProductCard.tsx
'use client';

import Link from 'next/link';
import { useWishlist } from '@/lib/wishlist';
import * as React from 'react';

type Img = { url: string; altText?: string };
type Money = { amount: string; currencyCode: string };

type Product = {
  handle: string;
  title: string;
  image?: Img;
  hoverImage?: Img;
  price: Money;
  rating?: number; // 0-5
  reviewCount?: number;
};

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

function StarRating({ rating, reviewCount }: { rating: number; reviewCount?: number }) {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <div
        role="img"
        aria-label={`${rating} out of 5 stars`}
        style={{ display: 'flex', alignItems: 'center', gap: '2px' }}
      >
        {/* Full stars */}
        {Array.from({ length: fullStars }).map((_, i) => (
          <svg
            key={`full-${i}`}
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="currentColor"
            style={{ color: '#fbbf24' }}
            aria-hidden="true"
          >
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        ))}

        {/* Half star */}
        {hasHalfStar && (
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            style={{ color: '#fbbf24' }}
            aria-hidden="true"
          >
            <defs>
              <linearGradient id={`half-${rating}`}>
                <stop offset="50%" stopColor="currentColor" />
                <stop offset="50%" stopColor="transparent" />
              </linearGradient>
            </defs>
            <path
              d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
              fill={`url(#half-${rating})`}
              stroke="currentColor"
              strokeWidth="1"
            />
          </svg>
        )}

        {/* Empty stars */}
        {Array.from({ length: emptyStars }).map((_, i) => (
          <svg
            key={`empty-${i}`}
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            style={{ color: '#d1d5db' }}
            aria-hidden="true"
          >
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        ))}
      </div>

      {/* Review count */}
      {reviewCount !== undefined && (
        <span className="text-xs muted" style={{ fontWeight: 500 }}>
          ({reviewCount})
        </span>
      )}
    </div>
  );
}

export function ProductCard({ product }: { product: Product }) {
  const { has, toggle } = useWishlist();
  const inWL = has(product.handle);

  return (
    <div className="card" style={{ position: 'relative' }}>
      <Link href={`/products/${product.handle}`} aria-label={product.title}>
        <div className="hover-zoom" style={{ borderRadius: 12, border: '1px solid var(--border)' }}>
          <div
            className="aspect-4-5 product-image-wrapper"
            style={{ position: 'relative', overflow: 'hidden' }}
            aria-hidden="true"
          >
            {/* Base image */}
            {product.image?.url ? (
              <img
                src={product.image.url}
                alt={product.image.altText || product.title}
                className="media-cover product-image-base"
              />
            ) : (
              <div className="skeleton aspect-4-5" />
            )}

            {/* Hover image swap */}
            {product.hoverImage?.url && (
              <img
                src={product.hoverImage.url}
                alt=""
                aria-hidden="true"
                className="media-cover product-image-hover"
              />
            )}
          </div>
        </div>

        <div style={{ marginTop: '.5rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <p style={{ fontWeight: 600, lineHeight: 1.3, margin: 0 }}>{product.title}</p>
          
          {/* Rating */}
          {product.rating !== undefined && (
            <StarRating rating={product.rating} reviewCount={product.reviewCount} />
          )}

          {/* Price */}
          <p className="text-sm muted" style={{ margin: 0, fontWeight: 600 }}>
            {formatPrice(product.price)}
          </p>
        </div>
      </Link>

      {/* Toggle button with aria-pressed and accessible name */}
      <button
        type="button"
        aria-label={inWL ? 'Remove from wishlist' : 'Add to wishlist'}
        aria-pressed={inWL}
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
          try {
            window.dispatchEvent(new CustomEvent('wishlist:update'));
            window.dispatchEvent(new CustomEvent('wishlist:open'));
          } catch {}
        }}
        className="wishlist-btn"
        style={{
          position: 'absolute',
          top: 10,
          right: 10,
          width: 40,
          height: 40,
          borderRadius: 999,
          background: 'rgba(255,255,255,0.9)',
          border: '1px solid var(--border)',
          display: 'grid',
          placeItems: 'center',
          boxShadow: 'var(--shadow-sm)',
          transition: 'transform var(--dur-1) var(--ease-out), background var(--dur-1) var(--ease-out)',
        }}
      >
        <span aria-hidden="true" style={{ fontSize: 18, lineHeight: 1 }}>
          {inWL ? '❤' : '♡'}
        </span>
      </button>
    </div>
  );
}
