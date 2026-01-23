// app/collections/[handle]/page.tsx
import { notFound } from 'next/navigation';
import { getProducts, toCard } from '@/lib/api-client';
import PLPFilters from '@/components/PLPFilters';
import ClientPLP from './plp-client';

interface CollectionPageParams {
  handle: string;
}

interface CollectionPageSearchParams {
  q?: string;
}

interface CollectionPageProps {
  params: Promise<CollectionPageParams>;
  searchParams?: Promise<CollectionPageSearchParams>;
}

export default async function CollectionPage({
  params,
  searchParams,
}: CollectionPageProps) {
  // Await the params and searchParams
  const { handle } = await params;
  const resolvedSearchParams = await searchParams;
  const q = (resolvedSearchParams?.q || '').trim();

  // In the real backend, 'handle' corresponds to 'category_slug'
  // But our API expects 'category' param.
  // We need to pass 'handle' as category.
  
  // Also, the backend handles 'q' natively.
  const productData = await getProducts(1, 24, handle, q);
  const products = productData.items;

  // We don't throw 404 if empty list, just show empty state usually.
  // But if that's the desired behavior:
  if (!products.length && !q) {
     // Only 404 if category truly empty? 
     // For now, let's allow empty categories or handle in UI.
     // But to keep parity:
     // notFound(); 
  }

  const cards = products.map(toCard);

  return (
    <div>
      <h1
        className="text-xl"
        style={{ fontWeight: 600, marginBottom: '0.5rem' }}
      >
        {handle.replaceAll('-', ' ').toUpperCase()}
      </h1>

      <PLPFilters />

      <ClientPLP cards={cards} />
    </div>
  );
}