// components/HeaderWishlist.tsx
'use client';

import { useEffect, useState } from 'react';
import { useWishlist } from '@/lib/wishlist';
import Link from 'next/link';

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

export default function HeaderWishlist() {
  const [open, setOpen] = useState(false);
  const { items, remove, clear, count } = useWishlist();

  useEffect(() => {
    function onOpen() { setOpen(true); }
    window.addEventListener('wishlist:open', onOpen as EventListener);
    return () => window.removeEventListener('wishlist:open', onOpen as EventListener);
  }, []);

  // Close on Escape key
  useEffect(() => {
    if (!open) return;
    function onEscape(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false);
    }
    window.addEventListener('keydown', onEscape);
    return () => window.removeEventListener('keydown', onEscape);
  }, [open]);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        aria-label="Open wishlist"
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
        <span aria-hidden="true">♥</span>
        <span aria-live="polite" style={{ fontSize: '.85rem', fontWeight: 600 }}>
          {count}
        </span>
      </button>

      {open && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 9999,
            display: 'flex',
            flexDirection: 'column',
            pointerEvents: 'all',
            transition: 'background 0.2s ease',
            background: 'rgba(0,0,0,0.40)',
          }}
          onClick={e => e.target === e.currentTarget && setOpen(false)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="wl-title"
            style={{
              display: 'flex',
              flexDirection: 'column',
              width: '100vw',
              maxWidth: '540px',
              height: '100vh',
              background: 'var(--bg)',
              marginLeft: 'auto',
              boxShadow: '-4px 0 24px rgba(0,0,0,0.15)',
              animation: 'slideInRight 250ms cubic-bezier(.2,.8,.2,1)',

            }}
          >
            {/* Header */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '1.2rem 1.4rem',
                borderBottom: '1px solid var(--border)',
                background: 'var(--bg-subtle)',
                minHeight: 68,
              }}
            >
              <h2 id="wl-title" style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0 }}>
                Wishlist
              </h2>
              <div style={{ display: 'flex', gap: '.5rem' }}>
                {items.length > 0 && (
                  <button
                    onClick={clear}
                    className="button button-secondary"
                    style={{
                      padding: '.35rem .65rem',
                      fontSize: '.9rem',
                      height: 'auto',
                    }}
                  >
                    Clear all
                  </button>
                )}
                <button
                  onClick={() => setOpen(false)}
                  aria-label="Close wishlist"
                  className="button button-secondary"
                  style={{
                    width: 38,
                    height: 38,
                    padding: 0,
                    fontSize: '1.3rem',
                    lineHeight: 1,
                  }}
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Content */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '1.25rem 1.4rem' }}>
              {items.length === 0 ? (
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: '100%',
                    gap: '1rem',
                    textAlign: 'center',
                  }}
                >
                  <span style={{ fontSize: '3rem', opacity: 0.3 }} aria-hidden="true">
                    ♡
                  </span>
                  <div>
                    <p style={{ margin: 0, fontWeight: 600 }}>Your wishlist is empty</p>
                    <p className="text-sm muted" style={{ margin: '.5rem 0 0' }}>
                      Save items you love for later
                    </p>
                  </div>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '.7rem' }}>
                  {items.map((it) => (
                    <div
                      key={it.id}
                      className="card"
                      style={{
                        display: 'flex',
                        gap: '.75rem',
                        padding: '.75rem',
                        border: '1px solid var(--border)',
                        borderRadius: 'var(--radius-sm)',
                        background: 'var(--bg)',
                        alignItems: 'center',
                        transition: 'transform var(--dur-1) var(--ease-out), box-shadow var(--dur-1) var(--ease-out)',
                      }}
                    >
                      {/* Image */}
                      <Link
                        href={`/products/${it.id}`}
                        onClick={() => setOpen(false)}
                        style={{ flexShrink: 0 }}
                      >
                        <div
                          className="aspect-square"
                          style={{
                            width: 72,
                            background: 'var(--bg-subtle)',
                            borderRadius: 'var(--radius-xs)',
                            overflow: 'hidden',
                          }}
                        >
                          {it.image?.url ? (
                            <img
                              src={it.image.url}
                              alt={it.image.altText || it.title}
                              className="media-cover"
                            />
                          ) : null}
                        </div>
                      </Link>

                      {/* Details */}
                      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: '.25rem' }}>
                        <Link
                          href={`/products/${it.id}`}
                          onClick={() => setOpen(false)}
                          style={{
                            fontWeight: 600,
                            fontSize: '.95rem',
                            display: 'block',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            lineHeight: 1.3,
                          }}
                        >
                          {it.title}
                        </Link>
                        <p className="text-sm muted" style={{ margin: 0, fontWeight: 600 }}>
                          {formatPrice(it.price, it.currencyCode)}
                        </p>
                      </div>

                      {/* Remove button */}
                      <button
                        onClick={() => remove(it.id)}
                        aria-label={`Remove ${it.title} from wishlist`}
                        style={{
                          border: 'none',
                          background: 'transparent',
                          padding: '.25rem',
                          cursor: 'pointer',
                          color: 'var(--muted)',
                          fontSize: '1.2rem',
                          lineHeight: 1,
                          transition: 'color var(--dur-1) var(--ease-out)',
                          alignSelf: 'flex-start',
                        }}
                        onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--fg)')}
                        onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--muted)')}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer CTA (if has items) */}
            {items.length > 0 && (
              <div
                style={{
                  padding: '1.2rem 1.4rem',
                  borderTop: '1px solid var(--border)',
                  background: 'var(--bg-subtle)',
                }}
              >
                <Link
                  href="/collections/all"
                  onClick={() => setOpen(false)}
                  className="button button-primary"
                  style={{ width: '100%', justifyContent: 'center' }}
                >
                  Continue Shopping
                </Link>
              </div>
            )}
          </div>

          <style jsx>{`
            @keyframes slideInRight {
              from { transform: translateX(100%); }
              to { transform: translateX(0); }
            }
          `}</style>
        </div>
      )}
    </>
  );
}
