// components/PLPFilters.tsx
'use client';

import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';

function useURLState(key: string, initial = '') {
  const search = useSearchParams();
  const [value, setValue] = useState(search.get(key) ?? initial);
  useEffect(() => { setValue(search.get(key) ?? initial); }, [search, key, initial]);
  return [value, setValue] as const;
}

export default function PLPFilters() {
  const router = useRouter();
  const pathname = usePathname();
  const search = useSearchParams();

  const [q, setQ] = useURLState('q', '');
  const [sort, setSort] = useURLState('sort', 'relevance');
  const [min, setMin] = useURLState('min', '');
  const [max, setMax] = useURLState('max', '');

  function apply() {
    const params = new URLSearchParams(search.toString());
    q ? params.set('q', q) : params.delete('q');
    sort ? params.set('sort', sort) : params.delete('sort');
    min ? params.set('min', min) : params.delete('min');
    max ? params.set('max', max) : params.delete('max');
    router.push(`${pathname}?${params.toString()}`);
  }

  function reset() {
    router.push(pathname);
  }

  return (
    <div style={{ display:'flex', gap:'1.5rem', flexWrap:'wrap', alignItems: 'center' }}>
      <input
        aria-label="Search"
        value={q}
        onChange={(e)=>setQ(e.target.value)}
        placeholder="SEARCH COLLECTION..."
        style={{ 
          background: 'transparent',
          border:'1px solid var(--border)', 
          padding:'0.75rem 1.5rem', 
          borderRadius:'var(--radius-pill)',
          fontSize: '0.75rem',
          fontWeight: 800,
          width: '250px'
        }}
      />
      
      <select 
        aria-label="Sort" 
        value={sort} 
        onChange={(e)=>setSort(e.target.value)} 
        style={{ 
          background: 'transparent',
          border:'1px solid var(--border)', 
          padding:'0.75rem 1.5rem', 
          borderRadius:'var(--radius-pill)',
          fontSize: '0.75rem',
          fontWeight: 800,
          cursor: 'pointer'
        }}
      >
        <option value="relevance">SORT: RELEVANCE</option>
        <option value="price-asc">PRICE: LOW TO HIGH</option>
        <option value="price-desc">PRICE: HIGH TO LOW</option>
        <option value="title-asc">TITLE: A–Z</option>
      </select>

      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <input aria-label="Min price" value={min} onChange={(e)=>setMin(e.target.value)} placeholder="MIN $" inputMode="numeric"
               style={{ width:100, background: 'transparent', border:'1px solid var(--border)', padding:'0.75rem 1rem', borderRadius:'var(--radius-pill)', fontSize: '0.75rem', fontWeight: 800 }} />
        <input aria-label="Max price" value={max} onChange={(e)=>setMax(e.target.value)} placeholder="MAX $" inputMode="numeric"
               style={{ width:100, background: 'transparent', border:'1px solid var(--border)', padding:'0.75rem 1rem', borderRadius:'var(--radius-pill)', fontSize: '0.75rem', fontWeight: 800 }} />
      </div>

      <button onClick={apply} className="vexo-button" style={{ padding: '0.75rem 2rem', fontSize: '0.75rem' }}>APPLY</button>
      <button onClick={reset} className="vexo-button vexo-button-outline" style={{ padding: '0.75rem 2rem', fontSize: '0.75rem' }}>RESET</button>
    </div>
  );
}
