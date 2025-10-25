// components/HeaderNavLinks.tsx
'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const items = [
  { href: '/collections/new-in', label: 'New In' },
  { href: '/collections/dresses', label: 'Dresses' },
  { href: '/collections/tops', label: 'Tops' },
  { href: '/collections/bottoms', label: 'Bottoms' },
  { href: '/collections/sale', label: 'Sale' },
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
