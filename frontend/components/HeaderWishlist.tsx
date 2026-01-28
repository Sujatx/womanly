'use client';

import { useState } from 'react';
import { useWishlist } from '@/lib/wishlist';
import { Heart } from 'lucide-react';
import WishlistDrawer from './WishlistDrawer';

export default function HeaderWishlist() {
  const [open, setOpen] = useState(false);
  const { count } = useWishlist();

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        aria-label="Open wishlist"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.4rem',
          padding: '0.5rem 0.75rem',
          borderRadius: '20px',
          border: '1px solid #e5e5e5',
          background: '#fff',
          cursor: 'pointer',
          transition: 'all 0.2s',
          color: '#111'
        }}
        onMouseEnter={(e) => e.currentTarget.style.borderColor = '#111'}
        onMouseLeave={(e) => e.currentTarget.style.borderColor = '#e5e5e5'}
      >
        <Heart size={18} fill={count > 0 ? "#111" : "none"} strokeWidth={count > 0 ? 0 : 2} />
        <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>
          {count}
        </span>
      </button>

      <WishlistDrawer open={open} onClose={() => setOpen(false)} />
    </>
  );
}