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

  const { handle } = await params;

  const resolvedSearchParams = await searchParams;

  const q = (resolvedSearchParams?.q || '').trim();



  const productData = await getProducts(1, 24, handle, q);

  const products = productData.items;

  const cards = products.map(toCard);



  return (

    <div style={{ paddingBottom: '10rem' }}>

      <div className="bg-text" style={{ top: '10%' }}>{handle.toUpperCase()}</div>

      

      <header style={{ textAlign: 'center', marginBottom: '6rem', position: 'relative', zIndex: 1 }}>

        <span className="collection-tag" style={{ color: 'var(--muted)' }}>CURATED SELECTION</span>

        <h1 style={{ fontSize: '4rem', fontWeight: 900, margin: '1rem 0' }}>{handle.replaceAll('-', ' ')}</h1>

        <p style={{ fontWeight: 800, color: 'var(--muted)', fontSize: '0.9rem' }}>DISCOVER THE LATEST PIECES FROM OUR {handle.toUpperCase()} CATEGORY</p>

      </header>



      <div className="container" style={{ position: 'relative', zIndex: 1 }}>

        <div style={{ marginBottom: '3rem', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)', padding: '1rem 0' }}>

          <PLPFilters />

        </div>



        <ClientPLP cards={cards} />

      </div>

    </div>

  );

}
