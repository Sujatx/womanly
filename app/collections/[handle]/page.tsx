// app/collections/[handle]/page.tsx
import { notFound } from 'next/navigation';
import { getCategoryProducts, toCard } from '@/lib/dummyjson';
import PLPFilters from '@/components/PLPFilters';
import ClientPLP from './plp-client';

interface PageProps {
  params: { handle: string };
  searchParams?: { q?: string };
}

export default async function CollectionPage({ params, searchParams }: PageProps) {
  const baseProducts = await getCategoryProducts(params.handle, 24);

  if (!baseProducts.length) {
    notFound();
  }

  const q = (searchParams?.q || '').trim().toLowerCase();
  const filtered = q
    ? baseProducts.filter(p =>
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
        {params.handle.replace('-', ' ').toUpperCase()}
      </h1>

      <PLPFilters />

      <ClientPLP cards={cards} />
    </div>
  );
}
