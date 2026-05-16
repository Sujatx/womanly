import { useMemo, useState, useEffect } from 'react';
import type { CartItem } from '@/app/data/products';
import { fetchShippingEstimate, fetchTaxEstimate, validateCoupon } from '@/lib/api-client';
import type { CheckoutItemInput } from '@/types/api';

interface CheckoutPageProps {
  items: CartItem[];
}

interface RazorpayWindow extends Window {
  Razorpay?: any;
}

export function CheckoutPage({ items }: CheckoutPageProps) {
  const subtotal = useMemo(
    () => items.reduce((sum, item) => sum + (item.salePrice || item.price) * item.quantity, 0),
    [items],
  );

  const [country, setCountry] = useState('IN');
  const [state, setState] = useState('');
  const [postalCode, setPostalCode] = useState('');
  const [couponCode, setCouponCode] = useState('');
  const [shippingCost, setShippingCost] = useState<number | null>(null);
  const [taxAmount, setTaxAmount] = useState<number | null>(null);
  const [couponDiscount, setCouponDiscount] = useState<number>(0);
  const [statusText, setStatusText] = useState('');
  
  // Payment flow state
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  // Load Razorpay script on mount
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const shippingItems = items.map((item) => ({
    product_id: Number(item.id),
    quantity: item.quantity,
    category_slug: item.collection.toLowerCase().replace(/\s+/g, '-'),
  }));

  const finalTotal = Math.max(0, subtotal + (shippingCost || 0) + (taxAmount || 0) - couponDiscount);

  const checkoutItems: CheckoutItemInput[] = useMemo(() => {
    return items
      .filter((item) => typeof item.variantId === 'number')
      .map((item) => ({ variant_id: item.variantId as number, quantity: item.quantity }));
  }, [items]);

  async function handlePlaceOrder() {
    if (items.length === 0) {
      setStatusText('Add items to cart to proceed with payment.');
      return;
    }

    if (!fullName.trim() || !email.trim() || !phone.trim() || !address.trim() || !city.trim()) {
      setStatusText('Please fill in all billing and shipping details.');
      return;
    }

    setIsProcessing(true);
    setStatusText('Creating order...');

    try {
      // Step 1: Create order on backend
      const idempotencyKey = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const createOrderResponse = await fetch(`http://localhost:8000/api/v1/payments/create-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Idempotency-Key': idempotencyKey,
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
        body: JSON.stringify({
          items: checkoutItems,
        }),
      });

      if (!createOrderResponse.ok) {
        throw new Error(`Order creation failed: ${createOrderResponse.statusText}`);
      }

      const orderData = await createOrderResponse.json();
      setStatusText('Opening payment gateway...');

      // Step 2: Show Razorpay payment modal
      const RazorpayWindow = window as RazorpayWindow;
      if (!RazorpayWindow.Razorpay) {
        throw new Error('Razorpay SDK not loaded');
      }

      const options = {
        key: 'rzp_test_S8YIGFotNHvcxH', // From your .env file
        amount: orderData.amount ?? Math.round(finalTotal * 100), // Amount in paise
        currency: 'INR',
        name: 'Womanly',
        description: `Order for ${fullName}`,
        order_id: orderData.id,
        prefill: {
          name: fullName,
          email: email,
          contact: phone,
        },
        notes: {
          address: address,
          city: city,
          state: state,
          postal_code: postalCode,
          country: country,
        },
        handler: async function (response: any) {
          setStatusText('Verifying payment...');
          
          // Step 3: Verify payment on backend
          const verifyResponse = await fetch(`http://localhost:8000/api/v1/payments/verify`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
            },
            body: JSON.stringify({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            }),
          });

          if (!verifyResponse.ok) {
            throw new Error('Payment verification failed');
          }

          setStatusText('✓ Payment successful! Order placed.');
          setTimeout(() => {
            window.location.hash = '#/orders';
          }, 2000);
        },
        modal: {
          ondismiss: () => {
            setIsProcessing(false);
            setStatusText('Payment cancelled. Please try again.');
          }
        },
      };

      const razorpayInstance = new RazorpayWindow.Razorpay(options);
      razorpayInstance.open();
    } catch (error) {
      setIsProcessing(false);
      setStatusText(`Error: ${error instanceof Error ? error.message : 'An error occurred'}`);
    }
  }

  async function handleEstimateShippingAndTax() {
    if (items.length === 0) {
      setStatusText('Add items to cart before estimating shipping and tax.');
      return;
    }

    setStatusText('Retrying requests if needed...');
    const address = {
      country,
      state: state || undefined,
      postal_code: postalCode || undefined,
    };

    const [shipping, tax] = await Promise.all([
      fetchShippingEstimate(address, shippingItems),
      fetchTaxEstimate(address, shippingItems, subtotal),
    ]);

    setShippingCost(shipping?.cost ?? 0);
    setTaxAmount(tax?.tax_amount ?? 0);
    setStatusText('Shipping and tax updated.');
  }

  async function handleApplyCoupon() {
    if (!couponCode.trim()) {
      setStatusText('Enter a coupon code first.');
      return;
    }

    const result = await validateCoupon(couponCode.trim(), subtotal);
    if (!result || !result.valid) {
      setCouponDiscount(0);
      setStatusText(result?.message || 'Coupon is invalid or unavailable.');
      return;
    }

    setCouponDiscount(result.discount_amount || 0);
    setStatusText(result.message);
  }

  return (
    <section className="container mx-auto px-6 py-16 md:py-24">
      <div className="mb-10">
        <p className="text-small text-muted uppercase tracking-wide">Checkout</p>
        <h1 className="font-headline">Shipping & Payment Summary</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
        <div className="lg:col-span-2 rounded-[var(--radius-lg)] border border-border bg-white p-4 sm:p-6 space-y-5 overflow-hidden">
          <h2 className="font-headline">Billing & Shipping Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full min-w-0 px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background"
              placeholder="Full name"
            />
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              className="w-full min-w-0 px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background"
              placeholder="Email address"
            />
            <input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full min-w-0 px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background md:col-span-2"
              placeholder="Phone number"
            />
            <input
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className="w-full min-w-0 px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background md:col-span-2"
              placeholder="Street address"
            />
            <input
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full min-w-0 px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background"
              placeholder="City"
            />
          </div>

          <h2 className="font-headline pt-4">Shipping Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              value={country}
              onChange={(e) => setCountry(e.target.value.toUpperCase())}
              className="w-full min-w-0 px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background"
              placeholder="Country code (IN)"
            />
            <input
              value={state}
              onChange={(e) => setState(e.target.value)}
              className="w-full min-w-0 px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background"
              placeholder="State"
            />
            <input
              value={postalCode}
              onChange={(e) => setPostalCode(e.target.value)}
              className="w-full min-w-0 px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background"
              placeholder="Postal code"
            />
          </div>

          <div className="flex flex-col gap-3 md:flex-row">
            <button
              onClick={handleEstimateShippingAndTax}
              className="w-full md:w-auto px-6 py-3 rounded-[var(--radius-sm)] bg-foreground text-white hover:bg-accent transition-colors"
            >
              Estimate Shipping & Tax
            </button>
            <div className="flex flex-col sm:flex-row flex-1 gap-3 min-w-0">
              <input
                value={couponCode}
                onChange={(e) => setCouponCode(e.target.value)}
                className="flex-1 min-w-0 px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background"
                placeholder="Coupon code"
              />
              <button
                onClick={handleApplyCoupon}
                className="w-full sm:w-auto px-6 py-3 rounded-[var(--radius-sm)] border border-border hover:border-accent transition-colors"
              >
                Apply
              </button>
            </div>
          </div>

          {statusText ? <p className="text-small text-muted">{statusText}</p> : null}
        </div>

        <aside className="rounded-[var(--radius-lg)] border border-border bg-white p-4 sm:p-6 h-fit">
          <h3 className="font-medium mb-4">Order Total</h3>
          <div className="space-y-2 text-small">
            <p className="flex justify-between"><span className="text-muted">Subtotal</span><span>${subtotal.toFixed(2)}</span></p>
            <p className="flex justify-between"><span className="text-muted">Shipping</span><span>${(shippingCost || 0).toFixed(2)}</span></p>
            <p className="flex justify-between"><span className="text-muted">Tax</span><span>${(taxAmount || 0).toFixed(2)}</span></p>
            <p className="flex justify-between"><span className="text-muted">Discount</span><span>- ${(couponDiscount || 0).toFixed(2)}</span></p>
          </div>
          <div className="mt-4 pt-4 border-t border-border flex justify-between font-medium">
            <span>Total</span>
            <span>${finalTotal.toFixed(2)}</span>
          </div>
          <button
            onClick={handlePlaceOrder}
            disabled={isProcessing || items.length === 0}
            className="w-full mt-6 bg-black text-white py-3 rounded-[var(--radius-sm)] font-medium hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            {isProcessing ? 'Processing...' : 'Complete Payment'}
          </button>
          {statusText && statusText.includes('Payment') && (
            <p className={`mt-2 text-sm text-center ${statusText.includes('Error') || statusText.includes('cancelled') ? 'text-red-600' : 'text-green-600'}`}>
              {statusText}
            </p>
          )}
        </aside>
      </div>
    </section>
  );
}
