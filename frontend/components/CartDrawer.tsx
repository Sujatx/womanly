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
            SHOPPING BAG / {cart?.count || 0}
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
          {lines.length === 0 ? (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              gap: '2rem',
              color: 'var(--muted)'
            }}>
              <ShoppingCart size={64} strokeWidth={1} />
              <p style={{ margin: 0, fontSize: '1rem', fontWeight: 800 }}>YOUR BAG IS EMPTY</p>
              <button 
                onClick={onClose}
                className="vexo-button"
              >
                START BROWSING
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              {lines.map((line) => (
                <div key={line.id} style={{ display: 'flex', gap: '1.5rem', position: 'relative' }}>
                  <div style={{ width: 110, height: 140, borderRadius: 'var(--radius-md)', overflow: 'hidden', background: 'var(--bg-subtle)', flexShrink: 0 }}>
                    {line.image?.url && (
                      <img src={line.image.url} alt={line.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    )}
                  </div>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <h3 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 900, textTransform: 'uppercase' }}>{line.title}</h3>
                      <button
                        onClick={() => { cart?.remove(line.id); toast.info('ITEM REMOVED'); }}
                        style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--muted)', padding: '2px' }}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                    
                    {/* Variant Details */}
                    <div style={{ marginTop: '0.5rem', display: 'flex', gap: '1rem' }}>
                      {line.selectedOptions?.map(opt => (
                        <span key={opt.name} style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--muted)', textTransform: 'uppercase' }}>
                          {opt.name}: {opt.value}
                        </span>
                      ))}
                    </div>

                    <p style={{ margin: '0.75rem 0', fontSize: '1rem', fontWeight: 900 }}>{formatPrice(line.price, currencyCode)}</p>
                    
                    <div style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        background: 'rgba(255,255,255,0.5)',
                        borderRadius: 'var(--radius-pill)',
                        border: '1px solid var(--border)',
                        padding: '4px'
                      }}>
                        <button 
                          onClick={() => cart?.setQty(line.id, Math.max(0, line.qty - 1))}
                          style={{ border: 'none', background: 'none', cursor: 'pointer', display: 'grid', placeItems: 'center', width: '32px', height: '32px' }}
                        >
                          <Minus size={14} />
                        </button>
                        <span style={{ minWidth: '30px', textAlign: 'center', fontSize: '0.85rem', fontWeight: 900 }}>{line.qty}</span>
                        <button 
                          onClick={() => cart?.setQty(line.id, line.qty + 1)}
                          style={{ border: 'none', background: 'none', cursor: 'pointer', display: 'grid', placeItems: 'center', width: '32px', height: '32px' }}
                        >
                          <Plus size={14} />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {lines.length > 0 && (
          <div style={{ padding: '2rem', borderTop: '1px solid var(--border)', background: 'rgba(255,255,255,0.2)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem' }}>
              <span style={{ fontSize: '0.9rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--muted)' }}>Subtotal</span>
              <span style={{ fontSize: '1.2rem', fontWeight: 900 }}>{formatPrice(subtotal, currencyCode)}</span>
            </div>
            <Link
              href="/checkout"
              onClick={onClose}
              className="vexo-button"
              style={{ width: '100%', height: '64px', justifyContent: 'center' }}
            >
              PROCEED TO CHECKOUT
              <ArrowRight size={20} />
            </Link>
            <p style={{ textAlign: 'center', fontSize: '0.7rem', fontWeight: 800, color: 'var(--muted)', marginTop: '1.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Shipping and taxes calculated at checkout
            </p>
          </div>
        )}
      </div>
    </>
  );
}

export default CartDrawer;