'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { Package, Calendar, Tag, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export default function OrdersPage() {
  const { user, token } = useAuth();
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    if (!token) {
      router.push('/auth');
      return;
    }

    async function fetchOrders() {
      try {
        const res = await fetch(`${API_URL}/payments/orders/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Failed to fetch orders');
        const data = await res.json();
        setOrders(data);
      } catch (err: any) {
        toast.error(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchOrders();
  }, [token, router]);

  if (loading) {
    return (
      <div style={{ display: 'grid', placeItems: 'center', height: '400px' }}>
        <div className="skeleton" style={{ width: '100%', height: '400px' }} />
      </div>
    );
  }

  return (
    <div>
      <header style={{ marginBottom: '3rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>ORDER HISTORY</h2>
        <p style={{ color: 'var(--muted)', fontWeight: 700, fontSize: '0.9rem' }}>VIEW AND TRACK YOUR RECENT PURCHASES</p>
      </header>

      {orders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '6rem', background: 'rgba(255,255,255,0.2)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)' }}>
          <Package size={64} style={{ margin: '0 auto 1.5rem', opacity: 0.1 }} />
          <p style={{ fontWeight: 900, color: 'var(--muted)' }}>NO ORDERS FOUND</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '2rem' }}>
          {orders.map((order) => (
            <div key={order.id} style={{ 
              background: 'rgba(255,255,255,0.3)', 
              borderRadius: 'var(--radius-lg)', 
              padding: '2rem', 
              border: '1px solid var(--border)',
              display: 'grid',
              gap: '1.5rem'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border)', paddingBottom: '1.5rem' }}>
                <div>
                  <div style={{ fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)', marginBottom: '0.5rem' }}>ORDER ID: #{order.id}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontWeight: 800 }}>
                    <Calendar size={16} /> {new Date(order.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ 
                    display: 'inline-block',
                    padding: '0.4rem 1rem',
                    borderRadius: 'var(--radius-pill)',
                    fontSize: '0.7rem',
                    fontWeight: 900,
                    textTransform: 'uppercase',
                    background: order.status === 'paid' ? 'var(--fg)' : 'var(--bg-subtle)',
                    color: order.status === 'paid' ? 'white' : 'var(--fg)',
                    border: '1px solid var(--border)'
                  }}>
                    {order.status}
                  </span>
                  <div style={{ marginTop: '0.75rem', fontSize: '1.5rem', fontWeight: 900 }}>
                    ${order.total_amount.toFixed(2)}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 900, color: 'var(--muted)' }}>
                  {order.items?.length || 0} ITEMS IN THIS ORDER
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
