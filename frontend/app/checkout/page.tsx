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
      toast.error('PLEASE SIGN IN TO COMPLETE PURCHASE');
      router.push('/auth');
      return;
    }

    setIsAuthProcessing(true);
    try {
      const scriptLoaded = await loadRazorpayScript();
      if (!scriptLoaded) {
        toast.error('RAZORPAY SDK FAILED TO LOAD');
        return;
      }

      const order = await createPaymentOrder();

      const options = {
        key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
        amount: Math.round(total * 100),
        currency: 'INR',
        name: 'WOMANLY',
        description: `ORDER FOR ${user.full_name || user.email}`,
        order_id: order.id,
        handler: async function (response: any) {
          toast.loading('VERIFYING PAYMENT...');
          try {
            const verifyRes = await verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });

            if (verifyRes.status === 'success') {
              toast.success('ORDER PLACED SUCCESSFULLY!');
              clear();
              router.push('/'); 
            } else {
              toast.error('PAYMENT VERIFICATION FAILED');
            }
          } catch (err: any) {
            toast.error('VERIFICATION ERROR: ' + err.message);
          }
        },
        prefill: {
          name: user.full_name || '',
          email: user.email,
        },
        theme: {
          color: '#0f172a',
        },
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.open();
    } catch (err: any) {
      toast.error('PAYMENT INITIALIZATION FAILED');
    } finally {
      setIsAuthProcessing(false);
    }
  }

  if (lines.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '150px 1.5rem' }}>
        <div className="bg-text">EMPTY</div>
        <ShoppingBag size={80} style={{ margin: '0 auto 2rem', opacity: 0.1 }} />
        <h1 style={{ fontSize: '2rem', fontWeight: 900 }}>YOUR BAG IS EMPTY</h1>
        <Link href="/" className="vexo-button" style={{ marginTop: '2rem' }}>
          BACK TO SHOP <ArrowLeft size={20} />
        </Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '4rem 1.5rem 10rem' }}>
      <div className="bg-text">CHECKOUT</div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '4rem' }}>
        <style jsx>{`
          @media (min-width: 1024px) {
            .checkout-grid {
              display: grid;
              grid-template-columns: 1fr 450px;
              gap: 6rem;
              align-items: start;
            }
          }
        `}</style>

        <div className="checkout-grid" style={{ position: 'relative', zIndex: 1 }}>
          {/* LEFT: Items & Details */}
          <div>
            <h1 style={{ fontSize: '3.5rem', fontWeight: 900, marginBottom: '3rem' }}>CHECKOUT</h1>
            
            <section style={{ marginBottom: '4rem' }}>
              <h2 style={{ fontSize: '0.8rem', fontWeight: 900, marginBottom: '2rem', letterSpacing: '0.1em', color: 'var(--muted)' }}>
                REVIEW BAG ({count})
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                {lines.map(line => (
                  <div key={line.id} style={{ display: 'flex', gap: '2rem', borderBottom: '1px solid var(--border)', paddingBottom: '2rem' }}>
                    <div style={{ width: '120px', height: '160px', borderRadius: 'var(--radius-md)', background: 'var(--bg-subtle)', overflow: 'hidden' }}>
                      <img src={line.image?.url} alt={line.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    </div>
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <h3 style={{ fontSize: '1rem', fontWeight: 900, textTransform: 'uppercase' }}>{line.title}</h3>
                        <p style={{ fontWeight: 900, fontSize: '1.1rem' }}>${(line.price * line.qty).toFixed(2)}</p>
                      </div>
                      <div style={{ marginTop: '0.5rem', display: 'flex', gap: '1rem' }}>
                        {line.selectedOptions?.map(opt => (
                          <span key={opt.name} style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--muted)', textTransform: 'uppercase' }}>
                            {opt.name}: {opt.value}
                          </span>
                        ))}
                      </div>
                      <p style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--muted)', marginTop: 'auto' }}>QTY: {line.qty}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
              <div style={{ padding: '2rem', background: 'rgba(255,255,255,0.3)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)' }}>
                <Truck size={32} style={{ marginBottom: '1.5rem' }} />
                <h3 style={{ fontSize: '0.9rem', fontWeight: 900, marginBottom: '0.5rem' }}>EXPRESS DELIVERY</h3>
                <p style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--muted)' }}>2-4 BUSINESS DAYS</p>
              </div>
              <div style={{ padding: '2rem', background: 'rgba(255,255,255,0.3)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)' }}>
                <ShieldCheck size={32} style={{ marginBottom: '1.5rem' }} />
                <h3 style={{ fontSize: '0.9rem', fontWeight: 900, marginBottom: '0.5rem' }}>SECURE PAYMENT</h3>
                <p style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--muted)' }}>RAZORPAY ENCRYPTED</p>
              </div>
            </section>
          </div>

          {/* RIGHT: Summary */}
          <aside style={{ 
            background: 'rgba(255,255,255,0.2)', 
            padding: '3rem', 
            borderRadius: 'var(--radius-lg)', 
            position: 'sticky', 
            top: '8rem',
            border: '1px solid var(--border)',
            backdropFilter: 'blur(10px)'
          }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 900, marginBottom: '2.5rem' }}>SUMMARY</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '2.5rem', paddingBottom: '2.5rem', borderBottom: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 800, color: 'var(--muted)', fontSize: '0.9rem' }}>
                <span>SUBTOTAL</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 800, color: 'var(--muted)', fontSize: '0.9rem' }}>
                <span>SHIPPING</span>
                <span>{shipping === 0 ? 'FREE' : `$${shipping.toFixed(2)}`}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 800, color: 'var(--muted)', fontSize: '0.9rem' }}>
                <span>ESTIMATED TAX</span>
                <span>${tax.toFixed(2)}</span>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '3rem' }}>
              <span style={{ fontSize: '1.1rem', fontWeight: 900 }}>TOTAL</span>
              <span style={{ fontSize: '2.5rem', fontWeight: 900 }}>${total.toFixed(2)}</span>
            </div>

            <button
              onClick={handlePayment}
              disabled={isProcessing}
              className="vexo-button"
              style={{ width: '100%', height: '72px', fontSize: '1.1rem' }}
            >
              <CreditCard size={24} />
              {isProcessing ? 'PROCESSING...' : 'PAY WITH RAZORPAY'}
            </button>

            <p style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--muted)', textAlign: 'center', marginTop: '2rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              By completing your purchase you agree to our Terms of Service and Privacy Policy.
            </p>
          </aside>
        </div>
      </div>
    </div>
  );
}
