// components/DeliveryReturns.tsx
// PDP reassurance: delivery window and return policy near the primary CTA.
// Keep concise to reduce risk perception and avoid pushing the CTA below the fold.

export function DeliveryReturns({
  shippingText = 'Delivery in 3–5 days',
  returnsText = 'Easy returns within 14 days',
}: { shippingText?: string; returnsText?: string }) {
  return (
    <div className="text-sm" style={{ color: '#555' }}>
      <p>🚚 {shippingText}</p>
      <p>↩️ {returnsText}</p>
    </div>
  );
}
