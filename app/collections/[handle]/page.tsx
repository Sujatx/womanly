// app/collections/[handle]/page.tsx
import { notFound } from 'next/navigation';
import { getCategoryProducts, toCard } from '@/lib/dummyjson';
import PLPFilters from '@/components/PLPFilters';
import ClientPLP from './plp-client';

export default async function CollectionPage({
  params,
  searchParams,
}: {
  // NOTICE: params is typed as a Promise — Next 15 expects this in some builds.
  params: Promise<{ handle: string }>;
  searchParams?: { q?: string };
}) {
  // unwrap the async params
  const { handle } = await params;

  const baseProducts = await getCategoryProducts(handle, 24);

  if (!baseProducts.length) {
    notFound();
  }

  const q = (searchParams?.q || '').trim().toLowerCase();
  const filtered = q
    ? baseProducts.filter(
        (p) =>
          p.title.toLowerCase().includes(q) ||
          p.description.toLowerCase().includes(q)
      )
    : baseProducts;

  const cards = filtered.map(toCard);

  return (
    <div>
      <h1
        className="text-xl"
        style={{ fontWeight: 600, marginBottom: '0.5rem' }}
      >
        {handle.replace('-', ' ').toUpperCase()}
      </h1>

      <PLPFilters />

      <ClientPLP cards={cards} />
    </div>
  );
}
