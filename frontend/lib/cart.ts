'use client';

import { useEffect, useRef, useState } from 'react';
import { getCart, addToCart, removeFromCart as apiRemoveFromCart, Cart, CartItem } from './api-client';
import { useAuth } from './auth-context';

export type CartLine = {
  id: string; // This is the CartItem.id (backend) or unique key (local)
  variantId: string;
  productId: string;
  title: string;
  price: number;
  currencyCode: string;
  qty: number;
  image?: { url: string; altText?: string };
  selectedOptions?: { name: string; value: string }[];
};

const KEY = 'cart_v2'; // Bump version for variant support
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
    return apiCart.items.map(item => {
        const product = item.variant?.product;
        const variant = item.variant;
        const price = (product?.price || 0) + (variant?.price_adjustment || 0);
        
        const options = [];
        if (variant?.size) options.push({ name: 'Size', value: variant.size });
        if (variant?.color) options.push({ name: 'Color', value: variant.color });

        return {
            id: String(item.id),
            variantId: String(item.variant_id),
            productId: String(product?.id || ''),
            title: product?.title || 'Product',
            price: price,
            currencyCode: 'USD',
            qty: item.quantity,
            image: product?.thumbnail ? { url: product.thumbnail } : undefined,
            selectedOptions: options
        };
    });
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
            const newCart = await addToCart(Number(line.variantId), line.qty); 
            setLines(mapApiCartToLines(newCart));
        } catch (e) {
            console.error(e);
        }
    } else {
        setLines(prev => {
            const next = [...prev];
            const i = next.findIndex(l => l.variantId === line.variantId);
            if (i >= 0) next[i] = { ...next[i], qty: next[i].qty + line.qty };
            else next.push({ ...line });
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
            const next = prev.filter(l => l.id !== id && l.variantId !== id); 
            writeLocalCart(next);
            return next;
        });
    }
  }

  function setQty(id: string, qty: number) {
      if (!isAuth) {
        setLines(prev => {
            const next = prev.map(l => (l.variantId === id || l.id === id ? { ...l, qty } : l)).filter(l => l.qty > 0);
            writeLocalCart(next);
            return next;
        });
      }
  }

  function clear() {
    if (isAuth) {
        // API clear not yet implemented
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