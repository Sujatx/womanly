// components/HeaderNavLinks.tsx
'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const items = [
  { href: '/collections/womens-dresses', label: 'Dresses' },
  { href: '/collections/tops', label: 'Tops' },
  { href: '/collections/womens-bags', label: 'Bags' },
  { href: '/collections/womens-shoes', label: 'Shoes' },
  { href: '/collections/womens-jewellery', label: 'Jewelry' },
];

export default function HeaderNavLinks() {
  const pathname = usePathname();
  return (
    <>
      {items.map(({ href, label }) => {
        const current = pathname?.startsWith(href);
        return (
          <Link key={href} href={href} aria-current={current ? 'page' : undefined}>
            {label}
          </Link>
        );
      })}
    </>
  );
}
