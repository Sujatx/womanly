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
    addToCart({
      id: item.id,
      productId: item.id,
      title: item.title,
      price: item.price || 0,
      currencyCode: item.currencyCode || 'USD',
      qty: 1,
      image: item.image
    });
    remove(item.id);
    toast.success('Moved to cart');
  }

  return (
    <>
      <div
        onClick={onClose}
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.2)',
          backdropFilter: 'blur(4px)',
          zIndex: 9998,
        }}
      />
      
      <div
        role="dialog"
        aria-modal="true"
        style={{
          position: 'fixed',
          top: 0,
          right: 0,
          width: '100%',
          maxWidth: '480px',
          height: '100vh',
          background: 'white',
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '-10px 0 40px rgba(0,0,0,0.1)',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div style={{ 
          padding: '1.5rem', 
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Heart size={20} fill="#111" />
            <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600, letterSpacing: '-0.01em' }}>
              Wishlist ({items.length})
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{ border: 'none', background: 'none', cursor: 'pointer', padding: '0.5rem', color: '#666' }}
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem' }}>
          {items.length === 0 ? (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              gap: '1rem',
              color: '#999'
            }}>
              <Heart size={48} strokeWidth={1} />
              <p style={{ margin: 0, fontSize: '0.95rem' }}>Your wishlist is empty</p>
              <button 
                onClick={onClose}
                style={{ 
                  marginTop: '0.5rem',
                  padding: '0.6rem 1.2rem',
                  background: '#111',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '20px',
                  fontSize: '0.875rem',
                  cursor: 'pointer'
                }}
              >
                Explore Products
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {items.map((item) => (
                <div key={item.id} style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                  <div style={{ width: 80, height: 100, borderRadius: '8px', overflow: 'hidden', background: '#f9f9f9', flexShrink: 0 }}>
                    {item.image?.url && (
                      <img src={item.image.url} alt={item.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    )}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h3 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 600, color: '#111', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {item.title}
                    </h3>
                    <p style={{ margin: '0.25rem 0 0.75rem', fontSize: '0.875rem', color: '#666' }}>
                      ${item.price}
                    </p>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        onClick={() => handleMoveToCart(item)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.4rem',
                          padding: '0.4rem 0.8rem',
                          background: '#f5f5f5',
                          border: 'none',
                          borderRadius: '6px',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.background = '#eeeeee'}
                        onMouseLeave={(e) => e.currentTarget.style.background = '#f5f5f5'}
                      >
                        <ShoppingBag size={14} />
                        Add to Cart
                      </button>
                      <button
                        onClick={() => remove(item.id)}
                        style={{
                          padding: '0.4rem',
                          background: 'none',
                          border: 'none',
                          color: '#999',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {items.length > 0 && (
          <div style={{ padding: '1.5rem', borderTop: '1px solid #f0f0f0' }}>
            <button
              onClick={() => { clear(); toast.info('Wishlist cleared'); }}
              style={{
                width: '100%',
                padding: '0.75rem',
                background: 'none',
                border: '1px solid #e5e5e5',
                borderRadius: '8px',
                fontSize: '0.875rem',
                fontWeight: 500,
                cursor: 'pointer'
              }}
            >
              Clear All Items
            </button>
          </div>
        )}
      </div>
    </>
  );
}
