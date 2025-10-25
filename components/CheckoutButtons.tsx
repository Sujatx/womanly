// components/CheckoutButtons.tsx
// Demo-only checkout: no network calls, just a quick loading state and success message.

'use client';

import { useState } from 'react';
import { Button } from './Button';

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

  async function onBuy() {
    setLoading(true);
    await new Promise((r) => setTimeout(r, 700)); // simulate work
    alert('Demo checkout complete — connect a backend later.');
    setLoading(false);
  }

  const isDisabled = disabled || loading || !merchandiseId;

  return (
    <Button onClick={onBuy} loading={loading} disabled={isDisabled} aria-busy={loading}>
      Buy Now
    </Button>
  );
}
