import { useEffect, useState } from 'react';
import { Package } from 'lucide-react';
import { fetchMyOrders } from '@/lib/api-client';
import type { APIOrder } from '@/types/api';
import { useAuth } from '@/contexts/AuthContext';

export function OrdersPage() {
  const [orders, setOrders] = useState<APIOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    async function loadOrders() {
      if (!isAuthenticated) {
        setLoading(false);
        return;
      }
      
      try {
        const data = await fetchMyOrders();
        setOrders(data);
      } finally {
        setLoading(false);
      }
    }

    loadOrders();
  }, [isAuthenticated]);

  return (
    <section className="container mx-auto px-6 py-16 md:py-24">
      <div className="mb-10">
        <p className="text-small text-muted uppercase tracking-wide">Account</p>
        <h1 className="font-headline">Orders</h1>
      </div>

      {loading ? (
        <p className="text-muted">Loading orders...</p>
      ) : !isAuthenticated ? (
        <div className="rounded-[var(--radius-lg)] border border-border bg-white p-10 text-center">
          <Package className="mx-auto mb-4 h-10 w-10 text-muted" />
          <p className="text-muted mb-3">Sign in to view your orders</p>
          <a 
            href="#/auth"
            className="inline-block bg-foreground text-white px-6 py-3 rounded-[var(--radius-sm)] hover:bg-accent transition-colors"
          >
            Sign In
          </a>
        </div>
      ) : orders.length === 0 ? (
        <div className="rounded-[var(--radius-lg)] border border-border bg-white p-10 text-center">
          <Package className="mx-auto mb-4 h-10 w-10 text-muted" />
          <p className="text-muted mb-3">No orders found.</p>
          <a 
            href="#/shop"
            className="inline-block bg-foreground text-white px-6 py-3 rounded-[var(--radius-sm)] hover:bg-accent transition-colors"
          >
            Start Shopping
          </a>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <article
              key={order.id}
              className="rounded-[var(--radius-md)] border border-border bg-white p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-3"
            >
              <div>
                <p className="text-small text-muted">Order #{order.id}</p>
                <h3 className="font-medium">Status: {order.status}</h3>
                <p className="text-small text-muted">Placed: {new Date(order.created_at).toLocaleDateString()}</p>
              </div>
              <div className="text-left md:text-right">
                <p className="font-medium">${order.total_amount.toFixed(2)}</p>
                <p className="text-small text-muted">{order.shipping_provider || 'Standard shipping'}</p>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
