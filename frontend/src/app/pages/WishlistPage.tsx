import { useEffect, useState } from 'react';
import { Heart } from 'lucide-react';
import { fetchWishlist } from '@/lib/api-client';
import type { APIWishlist } from '@/types/api';
import { useAuth } from '@/contexts/AuthContext';

export function WishlistPage() {
  const [wishlist, setWishlist] = useState<APIWishlist | null>(null);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    async function loadWishlist() {
      if (!isAuthenticated) {
        setLoading(false);
        return;
      }
      
      try {
        const result = await fetchWishlist();
        setWishlist(result);
      } finally {
        setLoading(false);
      }
    }

    loadWishlist();
  }, [isAuthenticated]);

  return (
    <section className="container mx-auto px-6 py-16 md:py-24">
      <div className="mb-10">
        <p className="text-small text-muted uppercase tracking-wide">Account</p>
        <h1 className="font-headline">Wishlist</h1>
      </div>

      {loading ? (
        <p className="text-muted">Loading wishlist...</p>
      ) : !isAuthenticated ? (
        <div className="rounded-[var(--radius-lg)] border border-border bg-white p-10 text-center">
          <Heart className="mx-auto mb-4 h-10 w-10 text-muted" />
          <p className="text-muted mb-3">Sign in to view your wishlist</p>
          <a 
            href="#/auth"
            className="inline-block bg-foreground text-white px-6 py-3 rounded-[var(--radius-sm)] hover:bg-accent transition-colors"
          >
            Sign In
          </a>
        </div>
      ) : !wishlist || wishlist.items.length === 0 ? (
        <div className="rounded-[var(--radius-lg)] border border-border bg-white p-10 text-center">
          <Heart className="mx-auto mb-4 h-10 w-10 text-muted" />
          <p className="text-muted mb-3">No wishlist items found.</p>
          <a 
            href="#/shop"
            className="inline-block bg-foreground text-white px-6 py-3 rounded-[var(--radius-sm)] hover:bg-accent transition-colors"
          >
            Start Shopping
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {wishlist.items.map((item) => (
            <article key={item.id} className="rounded-[var(--radius-md)] border border-border bg-white overflow-hidden">
              <div className="aspect-[4/3] bg-secondary">
                {item.thumbnail ? (
                  <img
                    src={item.thumbnail}
                    alt={item.title ?? 'Wishlist item'}
                    loading="lazy"
                    decoding="async"
                    className="w-full h-full object-cover"
                  />
                ) : null}
              </div>
              <div className="p-4">
                <h3 className="font-medium mb-1">{item.title ?? 'Untitled product'}</h3>
                <p className="text-muted text-small">{item.price ? `$${item.price}` : 'Price unavailable'}</p>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
