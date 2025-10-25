// app/collections/[handle]/page.tsx
import { notFound } from 'next/navigation';
import { getCategoryProducts, toCard } from '@/lib/dummyjson';
import PLPFilters from '@/components/PLPFilters';
import ClientPLP from './plp-client';

export default async function CollectionPage(props: any) {
  // props.params or props.params is sometimes a Promise in Next 15 builds.
  // Awaiting covers both Promise<object> and plain object.
  const { params, searchParams } = props;
  const { handle } = await params;
  const sp = await searchParams; // may be undefined, object, or Promise<object>

  const baseProducts = await getCategoryProducts(handle, 24);

  if (!baseProducts.length) {
    notFound();
  }

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
