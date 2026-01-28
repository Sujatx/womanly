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
    return <div style={{ padding: '4rem', textAlign: 'center' }}>Loading your orders...</div>;
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      <header style={{ marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, letterSpacing: '-0.04em', marginBottom: '0.5rem' }}>Your Orders</h1>
        <p style={{ color: '#666' }}>View and track your recent purchases</p>
      </header>

      {orders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem', border: '2px dashed #eee', borderRadius: '24px' }}>
          <Package size={48} style={{ margin: '0 auto 1rem', color: '#ccc' }} />
          <p style={{ fontWeight: 600, color: '#666' }}>You haven't placed any orders yet.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {orders.map((order) => (
            <div key={order.id} style={{ border: '1px solid #f0f0f0', borderRadius: '20px', padding: '1.5rem', background: '#fff', boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', borderBottom: '1px solid #f5f5f5', paddingBottom: '1rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#999', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 700, marginBottom: '0.25rem' }}>
                    <Tag size={12} /> Order ID: #{order.id}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: '#111', fontWeight: 600 }}>
                    <Calendar size={14} /> {new Date(order.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ 
                    display: 'inline-block',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '20px',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    background: order.status === 'paid' ? '#ecfdf5' : '#fef3c7',
                    color: order.status === 'paid' ? '#059669' : '#d97706'
                  }}>
                    {order.status}
                  </span>
                  <div style={{ marginTop: '0.5rem', fontSize: '1.25rem', fontWeight: 800 }}>
                    ${order.total_amount.toFixed(2)}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
                {/* Simplified items list as images if we had them, or just item count */}
                <div style={{ fontSize: '0.875rem', color: '#666' }}>
                  {order.items?.length || 0} items in this order
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
