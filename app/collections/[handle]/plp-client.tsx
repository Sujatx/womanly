// app/collections/[handle]/plp-client.tsx
'use client';

import { useSearchParams } from 'next/navigation';
import { filterByPrice, sortCards } from '@/lib/plp-transform';
import { ProductCard } from '@/components/ProductCard';

type Card = {
  handle: string;
  title: string;
  image?: { url: string; altText?: string };
  hoverImage?: { url: string; altText?: string };
  price: { amount: string; currencyCode: string };
};

export default function ClientPLP({ cards }: { cards: Card[] }) {
  const search = useSearchParams();
  const sort = search.get('sort') || 'relevance';
  const min = search.get('min'); const max = search.get('max');

  const minN = min ? Number(min) : undefined;
  const maxN = max ? Number(max) : undefined;

  const priced = filterByPrice(cards, minN, maxN);
  const final = sortCards(priced, sort);

  if (!final.length) {
    return <p className="muted">No products match your filters.</p>;
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4">
      {final.map((p) => (
        <ProductCard key={p.handle} product={p} />
      ))}
    </div>
  );
}
