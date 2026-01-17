'use client';

import { createClient } from '@/lib/supabase/client';

export default function Login() {
  const supabase = createClient();

  async function loginWithGoogle() {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`
      }
    });
  }

  return (
    <div>
      <button onClick={loginWithGoogle}>
        Continue with Google
      </button>
    </div>
  );
}
