'use client';

import { useEffect, useRef, useState } from 'react';
import { getCart, addToCart, removeFromCart as apiRemoveFromCart, Cart, CartItem } from './api-client';
import { useAuth } from './auth-context';

export type CartLine = {
  id: string; 
  productId: string;
  title: string;
  price: number;
  currencyCode: string;
  qty: number;
  image?: { url: string; altText?: string };
  selectedOptions?: { name: string; value: string }[];
};

const KEY = 'cart_v1';
const EVT = 'cart:update';

function readLocalCart(): CartLine[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function writeLocalCart(lines: CartLine[]) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(KEY, JSON.stringify(lines));
  } catch {}
  setTimeout(() => {
    try { window.dispatchEvent(new CustomEvent(EVT)); } catch {}
  }, 0);
}

function mapApiCartToLines(apiCart: Cart): CartLine[] {
    return apiCart.items.map(item => ({
        id: String(item.id),
        productId: String(item.product_id),
        title: item.product?.title || 'Product',
        price: item.product?.price || 0,
        currencyCode: 'USD',
        qty: item.quantity,
        image: item.product?.images?.[0] ? { url: item.product.images[0] } : undefined,
    }));
}

export function formatMoney(amount: number, currencyCode: string, locale = 'en-US') {
  return new Intl.NumberFormat(locale, { style: 'currency', currency: currencyCode }).format(amount);
}

export function useCart() {
  const [lines, setLines] = useState<CartLine[]>([]);
  const { token } = useAuth();
  const mounted = useRef(true);
  const isAuth = !!token;

  useEffect(() => {
    mounted.current = true;
    
    if (isAuth) {
        getCart()
            .then(c => {
                if(mounted.current) setLines(mapApiCartToLines(c));
            })
            .catch(() => {});
    } else {
        setLines(readLocalCart());
    }

    function onStorage(e: StorageEvent) {
      if (e.key === KEY && !isAuth) {
        setTimeout(() => { if (mounted.current) setLines(readLocalCart()); }, 0);
      }
    }

    function onLocal() {
      if (!isAuth) {
         setTimeout(() => { if (mounted.current) setLines(readLocalCart()); }, 0);
      }
    }

    window.addEventListener('storage', onStorage);
    window.addEventListener(EVT, onLocal as EventListener);

    return () => {
      mounted.current = false;
      window.removeEventListener('storage', onStorage);
      window.removeEventListener(EVT, onLocal as EventListener);
    };
  }, [isAuth, token]);

  async function add(line: CartLine) {
    if (isAuth) {
        try {
            const newCart = await addToCart(Number(line.id), line.qty); 
            setLines(mapApiCartToLines(newCart));
        } catch (e) {
            console.error(e);
        }
    } else {
        setLines(prev => {
            const next = [...prev];
            const i = next.findIndex(l => l.productId === line.id);
            if (i >= 0) next[i] = { ...next[i], qty: next[i].qty + line.qty };
            else next.push({ ...line, productId: line.id });
            writeLocalCart(next);
            return next;
        });
    }
  }

  async function remove(id: string) {
    if (isAuth) {
        try {
            const newCart = await apiRemoveFromCart(Number(id));
            setLines(mapApiCartToLines(newCart));
        } catch (e) {
            console.error(e);
        }
    } else {
        setLines(prev => {
            const next = prev.filter(l => l.id !== id && l.productId !== id); 
            writeLocalCart(next);
            return next;
        });
    }
  }

  function setQty(id: string, qty: number) {
      if (!isAuth) {
        setLines(prev => {
            const next = prev.map(l => (l.id === id ? { ...l, qty } : l)).filter(l => l.qty > 0);
            writeLocalCart(next);
            return next;
        });
      }
  }

  function clear() {
    if (isAuth) {
        // API clear not yet implemented, usually happens on checkout
    } else {
        setLines(() => {
            writeLocalCart([]);
            return [];
        });
    }
  }

  const count = lines.reduce((n, l) => n + l.qty, 0);
  const subtotal = lines.reduce((s, l) => s + l.qty * l.price, 0);
  const currencyCode = lines[0]?.currencyCode || 'USD';

  return { lines, add, remove, setQty, clear, count, subtotal, currencyCode };
}
