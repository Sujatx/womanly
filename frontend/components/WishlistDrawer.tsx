'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useWishlist } from '@/lib/wishlist';
import { X, Heart, ShoppingBag, Trash2 } from 'lucide-react';
import { useCart } from '@/lib/cart';
import { toast } from 'sonner';

type Props = {
  open: boolean;
  onClose: () => void;
};

export default function WishlistDrawer({ open, onClose }: Props) {
  const { items, remove, clear } = useWishlist();
  const { add: addToCart } = useCart();

  useEffect(() => {
    if (!open) return;
    const onEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onEscape);
    return () => window.removeEventListener('keydown', onEscape);
  }, [open, onClose]);

  if (!open) return null;

  function handleMoveToCart(item: any) {
    // For wishlist items, we might not have a variantId saved if it was a generic "add to wishlist"
    // But since our ProductCard now saves the full item, let's assume it has it or use productId as fallback
    addToCart({
      id: item.id, // This is handle/id
      variantId: item.variantId || item.id,
      productId: item.productId || item.id,
      title: item.title,
      price: item.price || 0,
      currencyCode: item.currencyCode || 'USD',
      qty: 1,
      image: item.image
    });
    remove(item.id);
    toast.success('ITEM MOVED TO BAG');
  }

  return (
    <>
      <div
        onClick={onClose}
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.3)',
          backdropFilter: 'blur(12px)',
          zIndex: 9998,
        }}
      />
      
      <div
        role="dialog"
        aria-modal="true"
        style={{
          position: 'fixed',
          top: '1rem',
          right: '1rem',
          bottom: '1rem',
          width: 'calc(100% - 2rem)',
          maxWidth: '500px',
          background: 'var(--bg)',
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: 'var(--shadow-md)',
          borderRadius: 'var(--radius-lg)',
          overflow: 'hidden',
          border: '1px solid var(--border)'
        }}
      >
        {/* Header */}
        <div style={{ 
          padding: '2rem', 
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(255,255,255,0.2)'
        }}>
          <h2 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 900, letterSpacing: '0.05em' }}>
            WISHLIST / {items.length}
          </h2>
          <button
            onClick={onClose}
            className="vexo-button vexo-button-outline"
            style={{ width: '40px', height: '40px', padding: 0, borderRadius: '50%', display: 'grid', placeItems: 'center' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '2rem' }}>
          {items.length === 0 ? (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              gap: '2rem',
              color: 'var(--muted)'
            }}>
              <Heart size={64} strokeWidth={1} />
              <p style={{ margin: 0, fontSize: '1rem', fontWeight: 800 }}>YOUR WISHLIST IS EMPTY</p>
              <button 
                onClick={onClose}
                className="vexo-button"
              >
                BROWSE COLLECTIONS
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              {items.map((item) => (
                <div key={item.id} style={{ display: 'flex', gap: '1.5rem' }}>
                  <div style={{ width: 110, height: 140, borderRadius: 'var(--radius-md)', overflow: 'hidden', background: 'var(--bg-subtle)', flexShrink: 0 }}>
                    {item.image?.url && (
                      <img src={item.image.url} alt={item.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    )}
                  </div>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <h3 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 900, textTransform: 'uppercase' }}>{item.title}</h3>
                      <button
                        onClick={() => { remove(item.id); toast.info('ITEM REMOVED'); }}
                        style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--muted)', padding: '2px' }}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                    <p style={{ margin: '0.5rem 0', fontSize: '1rem', fontWeight: 900 }}>${item.price}</p>
                    
                    <button
                      onClick={() => handleMoveToCart(item)}
                      className="vexo-button"
                      style={{ marginTop: 'auto', padding: '0.6rem 1.2rem', fontSize: '0.75rem', width: 'fit-content' }}
                    >
                      <ShoppingBag size={14} />
                      ADD TO BAG
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {items.length > 0 && (
          <div style={{ padding: '2rem', borderTop: '1px solid var(--border)', background: 'rgba(255,255,255,0.2)' }}>
            <button
              onClick={() => { clear(); toast.info('WISHLIST CLEARED'); }}
              className="vexo-button vexo-button-outline"
              style={{ width: '100%', height: '56px', justifyContent: 'center' }}
            >
              CLEAR ALL ITEMS
            </button>
          </div>
        )}
      </div>
    </>
  );
}
