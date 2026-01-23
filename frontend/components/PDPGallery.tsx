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
        gridTemplateColumns: '84px 1fr',
        gap: '0.75rem',
        alignItems: 'start',
      }}
    >
      {/* Vertical thumbnail rail */}
      <div
        style={{
          display: 'grid',
          gap: '0.5rem',
          gridAutoRows: 'min-content',
          maxHeight: 520,
          overflow: 'auto',
          paddingRight: 2,
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
              onFocus={() => setActive(i)}
              aria-current={isActive ? 'true' : undefined}
              aria-label={img.altText ? `Thumbnail: ${img.altText}` : `Thumbnail ${i + 1}`}
              style={{
                width: 80,
                height: 100,
                borderRadius: 8,
                overflow: 'hidden',
                border: isActive ? '2px solid #111' : '1px solid #ddd',
                background: '#f3f3f3',
                cursor: 'pointer',
              }}
            >
              <Image
                src={img.url}
                alt={img.altText || `Thumbnail ${i + 1}`}
                width={300}
                height={400}
                sizes="80px"
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                loading="lazy"
              />
            </button>
          );
        })}
      </div>

      {/* Main image: fixed 4:5 aspect box + fill = no extra bottom space */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          aspectRatio: '4 / 5',
          borderRadius: 12,
          overflow: 'hidden',
          background: '#f6f6f6',
        }}
      >
        <Image
          src={current.url}
          alt={current.altText || 'Product image'}
          fill
          sizes="(max-width: 768px) 90vw, 640px"
          style={{ objectFit: 'cover' }}
          priority
        />
      </div>
    </div>
  );
}
