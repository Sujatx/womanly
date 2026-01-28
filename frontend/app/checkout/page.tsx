'use client';

import { useCart } from '@/lib/cart';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { ShoppingBag, ArrowLeft, ShieldCheck, Truck, CreditCard } from 'lucide-react';
import Link from 'next/link';
import { loadRazorpayScript } from '@/lib/razorpay';
import { createPaymentOrder, verifyPayment } from '@/lib/api-client';
import { toast } from 'sonner';
import { useState } from 'react';

export default function CheckoutPage() {
  const { lines, subtotal, count, clear } = useCart();
  const { user } = useAuth();
  const router = useRouter();
  const [isProcessing, setIsAuthProcessing] = useState(false);

  const shipping = subtotal > 100 ? 0 : 15;
  const tax = subtotal * 0.08;
  const total = subtotal + shipping + tax;

  async function handlePayment() {
    if (!user) {
      toast.error('Please sign in to complete purchase');
      router.push('/auth');
      return;
    }

    setIsAuthProcessing(true);
    try {
      const scriptLoaded = await loadRazorpayScript();
      if (!scriptLoaded) {
        toast.error('Razorpay SDK failed to load');
        return;
      }

      const order = await createPaymentOrder();

      const options = {
        key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
        amount: Math.round(total * 100), // Ensure we use the full calculated total
        currency: 'INR',
        name: 'Womanly',
        description: `Order for ${user.full_name || user.email}`,
        order_id: order.id,
        handler: async function (response: any) {
          toast.loading('Verifying payment...');
          try {
            const verifyRes = await verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });

            if (verifyRes.status === 'success') {
              toast.success('Order placed successfully!');
              clear();
              router.push('/'); 
            } else {
              toast.error('Payment verification failed');
            }
          } catch (err: any) {
            toast.error('Verification error: ' + err.message);
          }
        },
        prefill: {
          name: user.full_name || '',
          email: user.email,
        },
        theme: {
          color: '#111111',
        },
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.open();
    } catch (err: any) {
      toast.error('Payment initialization failed');
    } finally {
      setIsAuthProcessing(false);
    }
  }

  if (lines.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 1.5rem' }}>
        <ShoppingBag size={64} style={{ margin: '0 auto 1.5rem', color: '#eee' }} />
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Your bag is empty</h1>
        <p style={{ color: '#666', marginTop: '0.5rem' }}>Looks like you haven't added anything yet.</p>
        <Link href="/" style={{ display: 'inline-block', marginTop: '2rem', background: '#111', color: '#fff', padding: '0.75rem 2rem', borderRadius: '30px', textDecoration: 'none', fontWeight: 600 }}>
          Back to Shop
        </Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#666', textDecoration: 'none', marginBottom: '2rem', fontSize: '0.875rem' }}>
        <ArrowLeft size={16} />
        Back to shopping
      </Link>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '3rem' }}>
        <style jsx>{`
          @media (min-width: 900px) {
            .checkout-grid {
              display: grid;
              grid-template-columns: 1fr 400px;
              gap: 4rem;
              align-items: start;
            }
          }
        `}</style>

        <div className="checkout-grid">
          {/* LEFT: Items & Details */}
          <div>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: '2rem' }}>Checkout</h1>
            
            <section style={{ marginBottom: '3rem' }}>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <ShoppingBag size={20} />
                Review Bag ({count})
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {lines.map(line => (
                  <div key={line.id} style={{ display: 'flex', gap: '1.5rem', borderBottom: '1px solid #f0f0f0', paddingBottom: '1.5rem' }}>
                    <div style={{ width: '100px', height: '130px', borderRadius: '12px', background: '#f9f9f9', overflow: 'hidden' }}>
                      <img src={line.image?.url} alt={line.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>{line.title}</h3>
                        <p style={{ fontWeight: 700 }}>${line.price * line.qty}</p>
                      </div>
                      <p style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.5rem' }}>Qty: {line.qty}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
              <div style={{ padding: '1.5rem', border: '1px solid #f0f0f0', borderRadius: '16px' }}>
                <Truck size={24} style={{ marginBottom: '1rem' }} />
                <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.25rem' }}>Express Delivery</h3>
                <p style={{ fontSize: '0.8rem', color: '#666' }}>2-4 Business days</p>
              </div>
              <div style={{ padding: '1.5rem', border: '1px solid #f0f0f0', borderRadius: '16px' }}>
                <ShieldCheck size={24} style={{ marginBottom: '1rem' }} />
                <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.25rem' }}>Secure Payment</h3>
                <p style={{ fontSize: '0.8rem', color: '#666' }}>Verified encryption</p>
              </div>
            </section>
          </div>

          {/* RIGHT: Summary */}
          <aside style={{ background: '#f9f9f9', padding: '2rem', borderRadius: '24px', position: 'sticky', top: '2rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.5rem' }}>Summary</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem', paddingBottom: '2rem', borderBottom: '1px solid #eee' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#666' }}>
                <span>Subtotal</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#666' }}>
                <span>Shipping</span>
                <span>{shipping === 0 ? 'FREE' : `$${shipping.toFixed(2)}`}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#666' }}>
                <span>Estimated Tax</span>
                <span>${tax.toFixed(2)}</span>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem' }}>
              <span style={{ fontSize: '1rem', fontWeight: 600 }}>Total</span>
              <span style={{ fontSize: '1.75rem', fontWeight: 800 }}>${total.toFixed(2)}</span>
            </div>

            <button
              onClick={handlePayment}
              disabled={isProcessing}
              style={{
                width: '100%',
                padding: '1.25rem',
                background: '#111',
                color: '#fff',
                border: 'none',
                borderRadius: '16px',
                fontSize: '1.1rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.75rem',
                transition: 'transform 0.2s'
              }}
              onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.02)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
            >
              <CreditCard size={20} />
              {isProcessing ? 'Processing...' : 'Pay with Razorpay'}
            </button>

            <p style={{ fontSize: '0.75rem', color: '#999', textAlign: 'center', marginTop: '1.5rem' }}>
              By completing your purchase you agree to our Terms of Service and Privacy Policy.
            </p>
          </aside>
        </div>
      </div>
    </div>
  );
}
