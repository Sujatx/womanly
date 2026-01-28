// app/layout.tsx
import './globals.css';
import type { ReactNode } from 'react';
import Link from 'next/link';
import HeaderCart from '@/components/HeaderCart';
import HeaderSearch from '@/components/HeaderSearch';
import HeaderWishlist from '@/components/HeaderWishlist';
import { Inter } from 'next/font/google';
import HeaderNavLinks from '@/components/HeaderNavLinks'; // new
import UserMenu from '@/components/UserMenu';
import { AuthProvider } from '@/lib/auth-context';
import { Toaster } from 'sonner';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-sans',
});

export const metadata = {
  title: 'Womanly — Women’s Fashion',
  description:
    'Discover new-in dresses, tops, bottoms, and edits with fast delivery and easy returns.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.variable} style={{ display: 'flex', minHeight: '100vh', flexDirection: 'column', fontFamily: 'var(--font-sans)' }}>
        <AuthProvider>
          <Toaster position="top-center" richColors />
          <a href="#main" className="sr-only">Skip to content</a>

          <header role="banner" /* glass is handled in CSS */>
            <div className="container header">
              <Link href="/" className="brand" aria-label="Go to homepage" style={{ fontWeight: 700, letterSpacing: '.2px' }}>
                Womanly
              </Link>

              <nav aria-label="Primary" className="nav" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1 }}>
                <div style={{ flex: 1, maxWidth: 520 }}>
                  <HeaderSearch />
                </div>

                {/* moved into a client component that sets aria-current */}
                <HeaderNavLinks />

                <UserMenu />
                <HeaderWishlist />
                <div style={{ marginLeft: '0.5rem' }}>
                  <HeaderCart />
                </div>
              </nav>
            </div>
          </header>

          <main id="main" style={{ flex: 1 }}>
            <div className="container" /* relies on CSS for max-width + centering */ style={{ padding: '1rem' }}>
              {children}
            </div>
          </main>

          <footer>
            <div className="container footer" style={{ padding: '1rem' }}>
              <small>© {new Date().getFullYear()} Made by Sujat</small>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
