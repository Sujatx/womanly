import { useMemo, useState } from 'react';
import type { CartItem } from '@/app/data/products';
import { fetchShippingEstimate, fetchTaxEstimate, validateCoupon } from '@/lib/api-client';

interface CheckoutPageProps {
  items: CartItem[];
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

  const shippingItems = items.map((item) => ({
    product_id: Number(item.id),
    quantity: item.quantity,
    category_slug: item.collection.toLowerCase().replace(/\s+/g, '-'),
  }));

  const finalTotal = Math.max(0, subtotal + (shippingCost || 0) + (taxAmount || 0) - couponDiscount);

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

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 rounded-[var(--radius-lg)] border border-border bg-white p-6 space-y-5">
          <h2 className="text-2xl font-headline">Shipping Details</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <input
              value={country}
              onChange={(e) => setCountry(e.target.value.toUpperCase())}
              className="px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background"
              placeholder="Country code (IN)"
            />
            <input
              value={state}
              onChange={(e) => setState(e.target.value)}
              className="px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background"
              placeholder="State"
            />
            <input
              value={postalCode}
              onChange={(e) => setPostalCode(e.target.value)}
              className="px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background"
              placeholder="Postal code"
            />
          </div>

          <div className="flex flex-col md:flex-row gap-3">
            <button
              onClick={handleEstimateShippingAndTax}
              className="px-6 py-3 rounded-[var(--radius-sm)] bg-foreground text-white hover:bg-accent transition-colors"
            >
              Estimate Shipping & Tax
            </button>
            <div className="flex-1 flex gap-3">
              <input
                value={couponCode}
                onChange={(e) => setCouponCode(e.target.value)}
                className="flex-1 px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background"
                placeholder="Coupon code"
              />
              <button
                onClick={handleApplyCoupon}
                className="px-6 py-3 rounded-[var(--radius-sm)] border border-border hover:border-accent transition-colors"
              >
                Apply
              </button>
            </div>
          </div>

          {statusText ? <p className="text-small text-muted">{statusText}</p> : null}
        </div>

        <aside className="rounded-[var(--radius-lg)] border border-border bg-white p-6 h-fit">
          <h3 className="text-xl font-medium mb-4">Order Total</h3>
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
        </aside>
      </div>
    </section>
  );
}
