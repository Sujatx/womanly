// components/PDPGallery.tsx
// Left rail: vertical thumbnails; Right: main image in a fixed 4:5 box with next/image fill.
// Hover/focus a thumbnail to swap the main image instantly.

'use client';

import { useState } from 'react';
import Image from 'next/image';

type Img = { url: string; altText?: string };

export function PDPGallery({ images }: { images: Img[] }) {
  const safe = images?.length ? images : [];
  const [active, setActive] = useState(0);
  if (!safe.length) return null;
  const current = safe[active];

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '100px 1fr',
        gap: '1.5rem',
        alignItems: 'start',
      }}
    >
      {/* Vertical thumbnail rail */}
      <div
        style={{
          display: 'grid',
          gap: '1rem',
          gridAutoRows: 'min-content',
          maxHeight: 600,
          overflow: 'auto',
          paddingRight: 4,
        }}
        aria-label="Image thumbnails"
      >
        {safe.map((img, i) => {
          const isActive = i === active;
          return (
            <button
              key={i}
              onClick={() => setActive(i)}
              onMouseEnter={() => setActive(i)}
              aria-current={isActive ? 'true' : undefined}
              style={{
                width: 100,
                height: 125,
                borderRadius: 'var(--radius-sm)',
                overflow: 'hidden',
                border: isActive ? '3px solid var(--fg)' : '1px solid var(--border)',
                background: 'var(--bg-subtle)',
                cursor: 'pointer',
                transition: 'all 0.2s',
                opacity: isActive ? 1 : 0.7,
              }}
            >
              <Image
                src={img.url}
                alt={img.altText || `Thumbnail ${i + 1}`}
                width={300}
                height={400}
                sizes="100px"
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                loading="lazy"
              />
            </button>
          );
        })}
      </div>

      {/* Main image */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          aspectRatio: '4 / 5',
          borderRadius: 'var(--radius-lg)',
          overflow: 'hidden',
          background: 'var(--bg-subtle)',
          boxShadow: 'var(--shadow-md)',
        }}
      >
        <Image
          src={current.url}
          alt={current.altText || 'Product image'}
          fill
          sizes="(max-width: 768px) 90vw, 800px"
          style={{ objectFit: 'cover' }}
          priority
        />
      </div>
    </div>
  );
}
