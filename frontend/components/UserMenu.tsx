'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { User, Package, Heart, LogOut, ChevronDown } from 'lucide-react';

export default function UserMenu() {
  const { user, logout, loading } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (loading) return <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#f5f5f5' }} />;

  if (!user) {
    return (
      <Link 
        href="/auth" 
        style={{ 
          fontSize: '0.875rem', 
          fontWeight: 500, 
          color: '#111', 
          textDecoration: 'none',
          padding: '0.5rem 1rem',
          borderRadius: '20px',
          border: '1px solid #e5e5e5',
          transition: 'all 0.2s'
        }}
      >
        Sign In
      </Link>
    );
  }

  return (
    <div style={{ position: 'relative' }} ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: '0.25rem',
          color: '#111'
        }}
      >
        <div style={{
          width: 32,
          height: 32,
          borderRadius: '50%',
          background: '#111',
          color: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '0.75rem',
          fontWeight: 600
        }}>
          {user.full_name?.charAt(0).toUpperCase() || user.email.charAt(0).toUpperCase()}
        </div>
        <ChevronDown size={14} style={{ transform: isOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
      </button>

      {isOpen && (
        <div style={{
          position: 'absolute',
          top: '100%',
          right: 0,
          marginTop: '0.75rem',
          width: '220px',
          background: '#fff',
          borderRadius: '12px',
          boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
          border: '1px solid #f0f0f0',
          padding: '0.5rem',
          zIndex: 1000,
          display: 'flex',
          flexDirection: 'column',
          gap: '2px'
        }}>
          <div style={{ padding: '0.75rem 0.75rem 0.5rem', borderBottom: '1px solid #f5f5f5', marginBottom: '0.5rem' }}>
            <p style={{ margin: 0, fontSize: '0.875rem', fontWeight: 600, color: '#111' }}>{user.full_name || 'Account'}</p>
            <p style={{ margin: 0, fontSize: '0.75rem', color: '#666', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user.email}</p>
          </div>

          <MenuLink href="/account/orders" icon={<Package size={16} />} label="My Orders" onClick={() => setIsOpen(false)} />
          <MenuLink href="/wishlist" icon={<Heart size={16} />} label="Wishlist" onClick={() => setIsOpen(false)} />
          <MenuLink href="/account/settings" icon={<User size={16} />} label="Account Settings" onClick={() => setIsOpen(false)} />
          
          <button
            onClick={() => { logout(); setIsOpen(false); }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem',
              width: '100%',
              border: 'none',
              background: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              color: '#dc2626',
              fontSize: '0.875rem',
              fontWeight: 500,
              textAlign: 'left',
              transition: 'background 0.2s'
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = '#fff1f1')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'none')}
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      )}
    </div>
  );
}

function MenuLink({ href, icon, label, onClick }: { href: string; icon: React.ReactNode; label: string; onClick: () => void }) {
  return (
    <Link
      href={href}
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        padding: '0.75rem',
        textDecoration: 'none',
        color: '#444',
        fontSize: '0.875rem',
        fontWeight: 500,
        borderRadius: '8px',
        transition: 'all 0.2s'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = '#f9f9f9';
        e.currentTarget.style.color = '#111';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'none';
        e.currentTarget.style.color = '#444';
      }}
    >
      {icon}
      {label}
    </Link>
  );
}