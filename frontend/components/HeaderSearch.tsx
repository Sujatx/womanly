// components/HeaderSearch.tsx
'use client';

import { useEffect, useId, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';

type Suggestion = { id: number; title: string; thumbnail?: string };

export default function HeaderSearch() {
  const router = useRouter();
  const [q, setQ] = useState('');
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<Suggestion[]>([]);
  const [active, setActive] = useState<number>(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const rootRef = useRef<HTMLDivElement>(null); // NEW: stable root instead of currentTarget
  const listId = useId();

  // Debounced search
  useEffect(() => {
    const handle = setTimeout(async () => {
      const term = q.trim();
      if (!term) {
        setItems([]);
        setOpen(false);
        setActive(-1);
        return;
      }
      try {
        const res = await fetch(
          `https://dummyjson.com/products/search?q=${encodeURIComponent(term)}&limit=6`,
          { cache: 'no-store' }
        );
        const data = await res.json();
        const next: Suggestion[] = (data.products || []).map((p: any) => ({
          id: p.id,
          title: p.title,
          thumbnail: p.thumbnail || p.images?.[0],
        }));
        setItems(next);
        setOpen(next.length > 0);
        setActive(next.length ? 0 : -1);
      } catch {
        setItems([]);
        setOpen(false);
        setActive(-1);
      }
    }, 200);
    return () => clearTimeout(handle);
  }, [q]);

  function onKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!open || !items.length) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActive((i) => (i + 1) % items.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActive((i) => (i - 1 + items.length) % items.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const pick = items[active >= 0 ? active : 0];
      if (pick) {
        setOpen(false);
        router.push(`/products/${pick.id}`);
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setOpen(false);
    }
  }

  // Close popup if focus leaves the root; use rAF and a root ref (avoid currentTarget in async)
  function onBlur() {
    requestAnimationFrame(() => {
      const root = rootRef.current;
      if (!root) return;
      if (!root.contains(document.activeElement)) setOpen(false);
    });
  }

  return (
    <div ref={rootRef} data-search-root style={{ position: 'relative', width: 'min(420px, 58vw)' }}>
      <input
        ref={inputRef}
        type="search"
        placeholder="Search products…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        onKeyDown={onKeyDown}
        onFocus={() => { if (items.length) setOpen(true); }}
        onBlur={onBlur}
        role="combobox"
        aria-expanded={open}
        aria-haspopup="listbox"
        aria-controls={listId}
        aria-activedescendant={active >= 0 && open ? `${listId}-opt-${active}` : undefined}
        aria-autocomplete="list"
        style={{ border: '1px solid #ddd', padding: '.45rem .6rem', borderRadius: 8, width: '100%' }}
      />
      {open && items.length > 0 && (
        <ul
          id={listId}
          role="listbox"
          style={{
            position: 'absolute',
            zIndex: 70,
            top: '110%',
            left: 0,
            right: 0,
            background: '#fff',
            border: '1px solid #eee',
            borderRadius: 10,
            padding: '.35rem',
            boxShadow: '0 10px 24px rgba(0,0,0,0.08)',
            maxHeight: 360,
            overflow: 'auto',
          }}
        >
          {items.map((it, i) => {
            const activeStyle = i === active ? { background: '#f6f6f6' } : {};
            return (
              <li
                id={`${listId}-opt-${i}`}
                key={it.id}
                role="option"
                aria-selected={i === active}
                tabIndex={-1}
                onMouseEnter={() => setActive(i)}
                onMouseDown={(e) => e.preventDefault()} // keep focus on input
                onClick={() => {
                  setOpen(false);
                  router.push(`/products/${it.id}`);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '.5rem',
                  padding: '.4rem .5rem',
                  borderRadius: 8,
                  cursor: 'pointer',
                  ...activeStyle,
                }}
              >
                <div style={{ width: 40, height: 40, background: '#f2f2f2', borderRadius: 6, overflow: 'hidden', flex: '0 0 auto' }}>
                  {it.thumbnail ? (
                    <img src={it.thumbnail} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : null}
                </div>
                <span style={{ fontSize: 14, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{it.title}</span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
