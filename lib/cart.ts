// lib/cart.ts
'use client';

import { useEffect, useRef, useState } from 'react';

export type CartLine = {
  id: string;
  title: string;
  price: number;
  currencyCode: string;
  qty: number;
  image?: { url: string; altText?: string };
  selectedOptions?: { name: string; value: string }[];
};

const KEY = 'cart_v1';
const EVT = 'cart:update';

function readCart(): CartLine[] {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function writeCart(lines: CartLine[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(lines));
  } catch {}
  // Defer same‑tab signal to avoid setState during another component's render
  setTimeout(() => {
    try { window.dispatchEvent(new CustomEvent(EVT)); } catch {}
  }, 0);
}

export function formatMoney(amount: number, currencyCode: string, locale = 'en-US') {
  return new Intl.NumberFormat(locale, { style: 'currency', currency: currencyCode }).format(amount);
}

export function useCart() {
  const [lines, setLines] = useState<CartLine[]>([]);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    setLines(readCart());

    function onStorage(e: StorageEvent) {
      if (e.key === KEY) {
        // Defer to avoid setState during render
        setTimeout(() => { if (mounted.current) setLines(readCart()); }, 0);
      }
    }

    function onLocal() {
      // Defer to avoid setState during render
      setTimeout(() => { if (mounted.current) setLines(readCart()); }, 0);
    }

    window.addEventListener('storage', onStorage);
    window.addEventListener(EVT, onLocal as EventListener);

    return () => {
      mounted.current = false;
      window.removeEventListener('storage', onStorage);
      window.removeEventListener(EVT, onLocal as EventListener);
    };
  }, []);

  function add(line: CartLine) {
    setLines(prev => {
      const next = [...prev];
      const i = next.findIndex(l => l.id === line.id);
      if (i >= 0) next[i] = { ...next[i], qty: next[i].qty + line.qty };
      else next.push(line);
      writeCart(next);
      return next;
    });
  }

  function remove(id: string) {
    setLines(prev => {
      const next = prev.filter(l => l.id !== id);
      writeCart(next);
      return next;
    });
  }

  function setQty(id: string, qty: number) {
    setLines(prev => {
      const next = prev.map(l => (l.id === id ? { ...l, qty } : l)).filter(l => l.qty > 0);
      writeCart(next);
      return next;
    });
  }

  function clear() {
    setLines(() => {
      writeCart([]);
      return [];
    });
  }

  const count = lines.reduce((n, l) => n + l.qty, 0);
  const subtotal = lines.reduce((s, l) => s + l.qty * l.price, 0);
  const currencyCode = lines[0]?.currencyCode || 'USD';

  return { lines, add, remove, setQty, clear, count, subtotal, currencyCode };
}
