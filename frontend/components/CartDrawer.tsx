// components/CartDrawer.tsx
'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useCart } from '@/lib/cart';

type Props = {
  open: boolean;
  onClose: () => void;
};

function formatPrice(price: number | undefined, currencyCode?: string) {
  if (price === undefined) return 'Price unavailable';
  try {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: currencyCode || 'USD',
      maximumFractionDigits: 0,
    }).format(price);
  } catch {
    return `${price} ${currencyCode || 'USD'}`;
  }
}

function CartDrawer({ open, onClose }: Props) {
  const cart = useCart();
  const lines = cart?.lines || [];
  const subtotal = cart?.subtotal || 0;
  const currencyCode = cart?.currencyCode || 'USD';

  useEffect(() => {
    if (!open) return;
    const onEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onEscape);
    return () => window.removeEventListener('keydown', onEscape);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <>
      <div
        onClick={onClose}
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.4)',
          zIndex: 9998,
        }}
      />
      
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="cart-title"
        style={{
          position: 'fixed',
          top: 0,
          right: 0,
          width: '100%',
          maxWidth: '540px',
          height: '100vh',
          background: 'white',
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '-4px 0 24px rgba(0,0,0,0.15)',
          borderTopLeftRadius: '12px',
          borderBottomLeftRadius: '12px',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div style={{ 
          padding: '1.2rem 1.4rem', 
          borderBottom: '1px solid #eaeaea',
          background: '#fafafa',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h2 id="cart-title" style={{ margin: 0, fontSize: '1.2rem', fontWeight: 700 }}>
            Cart
          </h2>
          <div style={{ display: 'flex', gap: '.5rem' }}>
            {lines.length > 0 && (
              <button
                onClick={() => cart?.clear()}
                style={{
                  padding: '.35rem .65rem',
                  fontSize: '.9rem',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  background: 'white',
                  cursor: 'pointer',
                }}
              >
                Clear all
              </button>
            )}
            <button
              onClick={onClose}
              aria-label="Close cart"
              style={{
                width: 38,
                height: 38,
                padding: 0,
                fontSize: '1.3rem',
                border: '1px solid #ddd',
                borderRadius: '6px',
                background: 'white',
                cursor: 'pointer',
              }}
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div style={{ 
          flex: 1, 
          overflowY: 'auto', 
          padding: '1.25rem 1.4rem',
          background: 'white'
        }}>
          {lines.length === 0 ? (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              gap: '1rem',
              textAlign: 'center',
            }}>
              <div style={{ fontSize: '3rem', opacity: 0.3 }}>🛒</div>
              <div>
                <p style={{ margin: 0, fontWeight: 600 }}>Your cart is empty</p>
                <p style={{ margin: '.5rem 0 0', fontSize: '.9rem', color: '#666' }}>
                  Add items to get started
                </p>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '.7rem' }}>
              {lines.map((line: any) => (
                <div
                  key={line.id}
                  style={{
                    display: 'flex',
                    gap: '.75rem',
                    padding: '.75rem',
                    border: '1px solid #eaeaea',
                    borderRadius: '10px',
                    background: 'white',
                    alignItems: 'center',
                  }}
                >
                  <Link href={`/products/${line.id}`} onClick={onClose}>
                    <div style={{
                      width: 72,
                      height: 72,
                      background: '#fafafa',
                      borderRadius: '6px',
                      overflow: 'hidden',
                    }}>
                      {line.image?.url && (
                        <img
                          src={line.image.url}
                          alt={line.image.altText || line.title}
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        />
                      )}
                    </div>
                  </Link>

                  <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: '.25rem' }}>
                    <Link
                      href={`/products/${line.id}`}
                      onClick={onClose}
                      style={{
                        fontWeight: 600,
                        fontSize: '.95rem',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        color: 'inherit',
                        textDecoration: 'none',
                      }}
                    >
                      {line.title}
                    </Link>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem' }}>
                      <p style={{ margin: 0, fontWeight: 600, fontSize: '.9rem', color: '#666' }}>
                        {formatPrice(line.price, currencyCode)}
                      </p>
                      <span style={{ fontSize: '.8rem', color: '#666' }}>× {line.qty}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => cart?.remove(line.id)}
                    aria-label={`Remove ${line.title} from cart`}
                    style={{
                      border: 'none',
                      background: 'transparent',
                      padding: '.25rem',
                      cursor: 'pointer',
                      color: '#666',
                      fontSize: '1.2rem',
                    }}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {lines.length > 0 && (
          <div style={{
            padding: '1.2rem 1.4rem',
            borderTop: '1px solid #eaeaea',
            background: '#fafafa',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <span style={{ fontSize: '1rem', fontWeight: 600 }}>Subtotal</span>
              <span style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                {formatPrice(subtotal, currencyCode)}
              </span>
            </div>
            <Link
              href="/checkout"
              onClick={onClose}
              style={{
                display: 'block',
                width: '100%',
                padding: '.55rem 1rem',
                background: '#111',
                color: 'white',
                textAlign: 'center',
                borderRadius: '8px',
                textDecoration: 'none',
                fontWeight: 500,
              }}
            >
              Checkout
            </Link>
          </div>
        )}
      </div>
    </>
  );
}

export default CartDrawer;
