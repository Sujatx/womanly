// app/collections/[handle]/page.tsx
import { notFound } from 'next/navigation';
import { getCategoryProducts, toCard } from '@/lib/dummyjson';
import PLPFilters from '@/components/PLPFilters';
import ClientPLP from './plp-client';

export default async function CollectionPage(props: any) {
  // Accept whatever Next gives (Promise or plain object) and await to normalize.
  const { params, searchParams } = props;
  const { handle } = await params;    // covers Promise<{handle}> and {handle}
  const sp = await searchParams;      // handles undefined, object, or Promise<object>

  const baseProducts = await getCategoryProducts(handle, 24);

  if (!baseProducts.length) notFound();

  const q = (sp?.q || '').toString().trim().toLowerCase();
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
      <h1 className="text-xl" style={{ fontWeight: 600, marginBottom: '0.5rem' }}>
        {handle.replace('-', ' ').toUpperCase()}
      </h1>

      <PLPFilters />

      <ClientPLP cards={cards} />
    </div>
  );
}
