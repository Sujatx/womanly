// app/collections/[handle]/page.tsx
import { notFound } from 'next/navigation';
import { getCategoryProducts, toCard } from '@/lib/dummyjson';
import PLPFilters from '@/components/PLPFilters';
import ClientPLP from './plp-client';

interface CollectionPageParams {
  handle: string;
}

interface CollectionPageSearchParams {
  q?: string;
}

interface CollectionPageProps {
  params: Promise<CollectionPageParams>;      // ← Added Promise
  searchParams?: Promise<CollectionPageSearchParams>;  // ← Added Promise
}

export default async function CollectionPage({
  params,
  searchParams,
}: CollectionPageProps) {
  // Await the params and searchParams
  const { handle } = await params;
  const resolvedSearchParams = await searchParams;

  const baseProducts = await getCategoryProducts(handle, 24);

  if (!baseProducts.length) {
    notFound();
  }

  const q = (resolvedSearchParams?.q || '').trim().toLowerCase();
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
