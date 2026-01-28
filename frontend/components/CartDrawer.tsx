'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useCart } from '@/lib/cart';
import { X, ShoppingCart, Trash2, Plus, Minus, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';

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
            <ShoppingCart size={20} />
            <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600, letterSpacing: '-0.01em' }}>
              Your Cart ({cart?.count || 0})
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
          {lines.length === 0 ? (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              gap: '1rem',
              color: '#999'
            }}>
              <ShoppingCart size={48} strokeWidth={1} />
              <p style={{ margin: 0, fontSize: '0.95rem' }}>Your cart is empty</p>
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
                Start Shopping
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {lines.map((line) => (
                <div key={line.id} style={{ display: 'flex', gap: '1rem' }}>
                  <div style={{ width: 90, height: 110, borderRadius: '8px', overflow: 'hidden', background: '#f9f9f9', flexShrink: 0 }}>
                    {line.image?.url && (
                      <img src={line.image.url} alt={line.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    )}
                  </div>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, color: '#111' }}>{line.title}</h3>
                        <button
                          onClick={() => { cart?.remove(line.id); toast.info('Removed from cart'); }}
                          style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#999', padding: '2px' }}
                        >
                          <X size={16} />
                        </button>
                      </div>
                      <p style={{ margin: '0.25rem 0 0', fontSize: '0.875rem', color: '#666' }}>{formatPrice(line.price, currencyCode)}</p>
                    </div>
                    
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        border: '1px solid #e5e5e5', 
                        borderRadius: '6px',
                        padding: '2px'
                      }}>
                        <button 
                          onClick={() => cart?.setQty(line.id, Math.max(0, line.qty - 1))}
                          style={{ border: 'none', background: 'none', cursor: 'pointer', display: 'flex', padding: '4px' }}
                        >
                          <Minus size={14} />
                        </button>
                        <span style={{ minWidth: '30px', textAlign: 'center', fontSize: '0.875rem', fontWeight: 600 }}>{line.qty}</span>
                        <button 
                          onClick={() => cart?.setQty(line.id, line.qty + 1)}
                          style={{ border: 'none', background: 'none', cursor: 'pointer', display: 'flex', padding: '4px' }}
                        >
                          <Plus size={14} />
                        </button>
                      </div>
                      <p style={{ margin: 0, fontWeight: 700, fontSize: '0.95rem' }}>{formatPrice(line.price * line.qty, currencyCode)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {lines.length > 0 && (
          <div style={{ padding: '1.5rem', borderTop: '1px solid #f0f0f0', background: '#fff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
              <span style={{ fontSize: '0.95rem', color: '#666' }}>Subtotal</span>
              <span style={{ fontSize: '1.1rem', fontWeight: 700 }}>{formatPrice(subtotal, currencyCode)}</span>
            </div>
            <Link
              href="/checkout"
              onClick={onClose}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                width: '100%',
                padding: '1rem',
                background: '#111',
                color: '#fff',
                borderRadius: '12px',
                textDecoration: 'none',
                fontWeight: 600,
                fontSize: '1rem',
                transition: 'transform 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
              onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
            >
              Checkout
              <ArrowRight size={18} />
            </Link>
            <p style={{ textAlign: 'center', fontSize: '0.75rem', color: '#999', marginTop: '1rem' }}>
              Shipping and taxes calculated at checkout
            </p>
          </div>
        )}
      </div>
    </>
  );
}

export default CartDrawer;