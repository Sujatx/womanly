// app/account/layout.tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Package, MapPin, User, LogOut } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function AccountLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { logout } = useAuth();

  const navItems = [
    { label: 'ORDERS', href: '/account/orders', icon: Package },
    { label: 'ADDRESSES', href: '/account/addresses', icon: MapPin },
    { label: 'PROFILE', href: '/account/profile', icon: User },
  ];

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '4rem 1.5rem' }}>
      <div className="bg-text">ACCOUNT</div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '5rem', position: 'relative', zIndex: 1 }}>
        <aside style={{ position: 'sticky', top: '8rem', height: 'fit-content' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 900, marginBottom: '3rem' }}>YOUR ACCOUNT</h1>
          
          <nav style={{ display: 'grid', gap: '1rem' }}>
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    padding: '1rem 1.5rem',
                    borderRadius: 'var(--radius-md)',
                    background: isActive ? 'var(--fg)' : 'rgba(255,255,255,0.3)',
                    color: isActive ? 'white' : 'var(--fg)',
                    fontWeight: 800,
                    fontSize: '0.8rem',
                    letterSpacing: '0.05em',
                    transition: 'all 0.2s',
                    border: '1px solid var(--border)'
                  }}
                >
                  <item.icon size={18} />
                  {item.label}
                </Link>
              );
            })}
            
            <button
              onClick={logout}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                padding: '1rem 1.5rem',
                borderRadius: 'var(--radius-md)',
                background: 'transparent',
                color: 'var(--fg)',
                fontWeight: 800,
                fontSize: '0.8rem',
                letterSpacing: '0.05em',
                cursor: 'pointer',
                border: '1px solid var(--border)',
                marginTop: '2rem'
              }}
            >
              <LogOut size={18} />
              SIGN OUT
            </button>
          </nav>
        </aside>

        <main>
          {children}
        </main>
      </div>
    </div>
  );
}
