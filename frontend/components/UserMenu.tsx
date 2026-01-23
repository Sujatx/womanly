'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function UserMenu() {
  const [token, setToken] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    // Check for token on mount and on storage events
    const t = localStorage.getItem('token');
    setToken(t);

    function onStorage() {
        setToken(localStorage.getItem('token'));
    }
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  function handleLogout() {
    localStorage.removeItem('token');
    setToken(null);
    router.refresh();
  }

  if (token) {
     return (
        <button 
          onClick={handleLogout} 
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontWeight: 500, fontSize: '0.875rem' }}
        >
          Logout
        </button>
     );
  }

  return (
    <Link 
      href="/auth" 
      style={{ fontWeight: 500, fontSize: '0.875rem' }}
    >
      Log In
    </Link>
  );
}
