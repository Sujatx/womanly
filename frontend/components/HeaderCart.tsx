// components/HeaderCart.tsx
'use client';

import { useEffect, useState } from 'react';
import CartDrawer from '@/components/CartDrawer';
import { useCart } from '@/lib/cart';

function HeaderCart() {
  const [open, setOpen] = useState(false);
  const { count } = useCart();

  useEffect(() => {
    function onOpen() { setOpen(true); }
    window.addEventListener('cart:open', onOpen as EventListener);
    return () => window.removeEventListener('cart:open', onOpen as EventListener);
  }, []);

  useEffect(() => {
    function onUpdate() { setOpen((v) => v); }
    window.addEventListener('cart:update', onUpdate as EventListener);
    return () => window.removeEventListener('cart:update', onUpdate as EventListener);
  }, []);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        aria-label="Open cart"
        className="button-secondary"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '.45rem .7rem',
          borderRadius: 999,
          border: '1px solid var(--border)',
          background: 'var(--bg)',
          fontSize: '1rem',
          position: 'relative',
        }}
      >
        <span aria-hidden="true">🛒</span>
        <span aria-live="polite" style={{ fontSize: '.85rem', fontWeight: 600 }}>
          {count}
        </span>
      </button>
      <CartDrawer open={open} onClose={() => setOpen(false)} />
    </>
  );
}

export default HeaderCart;
