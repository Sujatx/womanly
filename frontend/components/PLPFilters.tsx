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
  const [sort, setSort] = useURLState('sort', 'relevance'); // relevance | price-asc | price-desc | title-asc
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
    <div className="text-sm" style={{ display:'flex', gap:'0.5rem', flexWrap:'wrap', marginBottom:'0.75rem' }}>
      <input
        aria-label="Search"
        value={q}
        onChange={(e)=>setQ(e.target.value)}
        placeholder="Search"
        style={{ border:'1px solid #ddd', padding:'.35rem .5rem', borderRadius:6 }}
      />
      <select aria-label="Sort" value={sort} onChange={(e)=>setSort(e.target.value)} style={{ border:'1px solid #ddd', padding:'.35rem .5rem', borderRadius:6 }}>
        <option value="relevance">Relevance</option>
        <option value="price-asc">Price ↑</option>
        <option value="price-desc">Price ↓</option>
        <option value="title-asc">Title A–Z</option>
      </select>
      <input aria-label="Min price" value={min} onChange={(e)=>setMin(e.target.value)} placeholder="Min" inputMode="numeric"
             style={{ width:70, border:'1px solid #ddd', padding:'.35rem .5rem', borderRadius:6 }} />
      <input aria-label="Max price" value={max} onChange={(e)=>setMax(e.target.value)} placeholder="Max" inputMode="numeric"
             style={{ width:70, border:'1px solid #ddd', padding:'.35rem .5rem', borderRadius:6 }} />
      <button onClick={apply} style={{ border:'1px solid #ddd', padding:'.35rem .6rem', borderRadius:6, background:'#f5f5f5' }}>Apply</button>
      <button onClick={reset} style={{ border:'1px solid #ddd', padding:'.35rem .6rem', borderRadius:6, background:'#fff' }}>Reset</button>
    </div>
  );
}
