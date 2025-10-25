// app/products/[handle]/page.tsx
// DummyJSON-powered PDP: maps /products/[id] -> DummyJSON /products/:id
// Uses toPDP() to shape data for your existing PDPClient.

import { notFound } from 'next/navigation';
import PDPClient from '@/components/PDPClient';
import { getProductById, toPDP } from '@/lib/dummyjson';

export default async function ProductPage({ params }: { params: { handle: string } }) {
  const id = Number(params.handle);

  // If the URL segment isn't a finite number, trigger the 404 UI
  if (!Number.isFinite(id)) {
    notFound();
  }

  try {
    const product = await getProductById(id);
    const mapped = toPDP(product);

    return (
      <PDPClient
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
