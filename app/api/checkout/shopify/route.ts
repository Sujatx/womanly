// app/api/checkout/shopify/route.ts
// POST { lines: [{ merchandiseId, quantity }] } -> { url: checkoutUrl }
// Uses Next.js Route Handlers (App Router) with NextRequest/NextResponse.
// Calls lib/shopify.ts createCartAndGetCheckoutUrl to hand off to Shopify checkout.

import { NextRequest, NextResponse } from 'next/server';
import { createCartAndGetCheckoutUrl } from '@/lib/shopify';

export async function POST(req: NextRequest) {
  try {
    // 1) Parse and validate payload
    const body = await req.json().catch(() => null);
    const lines = body?.lines;
    const isValid =
      Array.isArray(lines) &&
      lines.length > 0 &&
      lines.every(
        (l: any) =>
          l &&
          typeof l.merchandiseId === 'string' &&
          l.merchandiseId.length > 0 &&
          Number.isInteger(l.quantity) &&
          l.quantity > 0
      );

    if (!isValid) {
      return NextResponse.json({ error: 'Invalid payload: expected lines[{ merchandiseId, quantity>0 }]' }, { status: 400 });
    }

    // 2) Create Cart via Storefront API and get checkoutUrl
    const url = await createCartAndGetCheckoutUrl(lines);

    // 3) Return JSON so client can redirect safely
    return NextResponse.json({ url }, { status: 200 });
  } catch (e: any) {
    // Avoid leaking internals; surface a clean error
    return NextResponse.json({ error: e?.message || 'Checkout failed' }, { status: 500 });
  }
}
