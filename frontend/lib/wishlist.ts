// lib/wishlist.ts
'use client';

import { useEffect, useRef, useState } from 'react';

export type WishlistItem = {
  id: string; // product id or handle
  title: string;
  image?: { url: string; altText?: string };
  price?: number;
  currencyCode?: string;
};

const KEY = 'wishlist_v1';
const EVT = 'wishlist:update';

function read(): WishlistItem[] {
  try { const raw = localStorage.getItem(KEY); return raw ? JSON.parse(raw) : []; } catch { return []; }
}
function write(items: WishlistItem[]) {
  try { localStorage.setItem(KEY, JSON.stringify(items)); } catch {}
  setTimeout(() => { try { window.dispatchEvent(new CustomEvent(EVT)); } catch {} }, 0);
}

export function useWishlist() {
  const [items, setItems] = useState<WishlistItem[]>([]);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    setItems(read());
    function onStorage(e: StorageEvent) { if (e.key === KEY) setTimeout(() => mounted.current && setItems(read()), 0); }
    function onLocal() { setTimeout(() => mounted.current && setItems(read()), 0); }
    window.addEventListener('storage', onStorage);
    window.addEventListener(EVT, onLocal as EventListener);
    return () => {
      mounted.current = false;
      window.removeEventListener('storage', onStorage);
      window.removeEventListener(EVT, onLocal as EventListener);
    };
  }, []);

  function add(item: WishlistItem) {
    setItems(prev => {
      if (prev.some(i => i.id === item.id)) return prev;
      const next = [item, ...prev];
      write(next);
      return next;
    });
  }
  function remove(id: string) {
    setItems(prev => {
      const next = prev.filter(i => i.id !== id);
      write(next);
      return next;
    });
  }
  function toggle(item: WishlistItem) {
    setItems(prev => {
      const exists = prev.some(i => i.id === item.id);
      const next = exists ? prev.filter(i => i.id !== item.id) : [item, ...prev];
      write(next);
      return next;
    });
  }
  function clear() { setItems(() => { write([]); return []; }); }
  function has(id: string) { return items.some(i => i.id === id); }

  const count = items.length;
  return { items, add, remove, toggle, clear, has, count };
}
