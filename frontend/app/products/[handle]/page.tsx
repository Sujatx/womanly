// app/products/[handle]/page.tsx
// DummyJSON-powered PDP: maps /products/[id] -> DummyJSON /products/:id
// Uses toPDP() to shape data for your existing PDPClient.

import { notFound } from 'next/navigation';
import PDPClient from '@/components/PDPClient';
import { getProduct, toPDP } from '@/lib/api-client';

export default async function ProductPage({ 
  params 
}: { 
  params: Promise<{ handle: string }> 
}) {
  // Await params before using
  const { handle } = await params;
  const id = Number(handle);

  // If the URL segment isn't a finite number, trigger the 404 UI
  if (!Number.isFinite(id)) {
    notFound();
  }

  try {
    const product = await getProduct(id);
    const mapped = toPDP(product);

    return (
      <PDPClient
        id={mapped.id}
        title={mapped.title}
        description={mapped.description}
        images={mapped.images}
        options={mapped.options}
        variants={mapped.variants}
        tags={mapped.tags}
      />
    );
  } catch {
    // If the product lookup fails, render the route's not-found UI
    notFound();
  }
}
