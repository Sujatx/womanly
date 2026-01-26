// components/CheckoutButtons.tsx
// Demo-only checkout: no network calls, just a quick loading state and success message.

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from './Button';
import { loadRazorpayScript } from '@/lib/razorpay';
import { createPaymentOrder, verifyPayment } from '@/lib/api-client';

export function CheckoutButtons({
  merchandiseId,
  quantity = 1,
  disabled = false,
}: {
  merchandiseId?: string;
  quantity?: number;
  disabled?: boolean;
}) {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function onBuy() {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth');
      return;
    }

    setLoading(true);
    try {
      // 1. Load Razorpay script
      const res = await loadRazorpayScript();
      if (!res) {
        alert('Razorpay SDK failed to load. Are you online?');
        setLoading(false);
        return;
      }

      // 2. Create Order on Backend
      const order = await createPaymentOrder();

      // 3. Open Razorpay Checkout
      const options = {
        key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
        amount: order.amount,
        currency: order.currency,
        name: 'Womanly',
        description: 'Purchase Payment',
        order_id: order.id,
        handler: async function (response: any) {
          // 4. Verify Payment on Backend
          try {
            const verifyRes = await verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });

            if (verifyRes.status === 'success') {
              alert('Payment Successful!');
              router.push('/'); // Or orders page
            } else {
              alert('Payment Verification Failed');
            }
          } catch (err: any) {
            alert('Error verifying payment: ' + err.message);
          }
        },
        prefill: {
          name: '', // Can be filled if we have user info
          email: '',
          contact: '',
        },
        theme: {
          color: '#111111',
        },
      };

      const paymentObject = new (window as any).Razorpay(options);
      paymentObject.open();
    } catch (err: any) {
      alert('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  }

  const isDisabled = disabled || loading || !merchandiseId;

  return (
    <Button onClick={onBuy} loading={loading} disabled={isDisabled} aria-busy={loading}>
      Buy Now
    </Button>
  );
}
