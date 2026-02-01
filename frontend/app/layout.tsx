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
      <body className={inter.variable} style={{ display: 'flex', minHeight: '100vh', flexDirection: 'column', background: 'var(--bg)' }}>
        <AuthProvider>
          <Toaster position="top-center" richColors />
          <a href="#main" className="sr-only">Skip to content</a>

          <header role="banner">
            <div className="container header-inner">
              {/* Left Pill: Nav Links */}
              <nav aria-label="Primary Left" className="nav-pill">
                <HeaderNavLinks />
              </nav>

              {/* Center: Brand Notch */}
              <div className="notch-container">
                <Link href="/" className="brand" aria-label="Go to homepage">
                  Womanly
                </Link>
              </div>

              {/* Right Pill: Actions */}
              <div className="nav-pill">
                <div style={{ width: 180 }}>
                  <HeaderSearch />
                </div>
                <UserMenu />
                <HeaderWishlist />
                <HeaderCart />
              </div>
            </div>
          </header>

          <main id="main" style={{ flex: 1, paddingTop: '7rem' }}>
            <div className="container">
              {children}
            </div>
          </main>

          <footer>
            <div className="container footer">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <small>© {new Date().getFullYear()} WOMANLY. PREMISES OF HIGH FASHION.</small>
                <div style={{ display: 'flex', gap: '2rem', fontSize: '0.8rem', fontWeight: 600 }}>
                  <Link href="/privacy">PRIVACY</Link>
                  <Link href="/terms">TERMS</Link>
                  <Link href="/shipping">SHIPPING</Link>
                </div>
              </div>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
