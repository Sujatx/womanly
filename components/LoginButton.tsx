'use client';

import { createClient } from '@/lib/supabase/client';

export function LoginButton() {
  const supabase = createClient();

  async function login() {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: 'http://localhost:3000/auth/callback'
      }
    });
  }

  return (
    <button
      onClick={login}
      style={{
        background: '#111',
        color: '#fff',
        padding: '0.6rem 1rem',
        borderRadius: 8,
        fontWeight: 600,
      }}
    >
      Login with Google
    </button>
  );
}
