'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');

    const endpoint = isLogin ? '/api/auth/login' : '/api/auth/signup';
    // We'll proxy through Next.js API routes or hit backend directly?
    // Let's hit backend directly for now, but usually we want to store cookie.
    // For this MVP, let's store token in localStorage to match existing pattern.
    
    // Wait, CORS might be issue if hitting localhost:8000 directly from browser.
    // Backend CORS middleware is needed.
    // Assuming backend will have CORS allowed for frontend.
    
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    try {
      let res;
      if (isLogin) {
        // Login expects form data
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        
        res = await fetch(`${API_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: formData,
        });
      } else {
        // Signup expects JSON
        res = await fetch(`${API_URL}/auth/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, full_name: fullName }),
        });
      }

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Authentication failed');
      }

      if (isLogin) {
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        // Refresh page or push to home
        router.push('/');
      } else {
        // After signup, switch to login or auto-login
        setIsLogin(true);
        setError('Account created! Please log in.');
      }
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: '4rem auto', padding: '2rem', border: '1px solid #eee', borderRadius: 8 }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem', textAlign: 'center' }}>
        {isLogin ? 'Welcome Back' : 'Create Account'}
      </h1>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {!isLogin && (
           <label>
             <span style={{ display: 'block', marginBottom: '.5rem', fontSize: '0.875rem' }}>Full Name</span>
             <input
               type="text"
               required
               value={fullName}
               onChange={(e) => setFullName(e.target.value)}
               style={{ width: '100%', padding: '.75rem', border: '1px solid #ddd', borderRadius: 4 }}
             />
           </label>
        )}

        <label>
          <span style={{ display: 'block', marginBottom: '.5rem', fontSize: '0.875rem' }}>Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ width: '100%', padding: '.75rem', border: '1px solid #ddd', borderRadius: 4 }}
          />
        </label>

        <label>
          <span style={{ display: 'block', marginBottom: '.5rem', fontSize: '0.875rem' }}>Password</span>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: '100%', padding: '.75rem', border: '1px solid #ddd', borderRadius: 4 }}
          />
        </label>

        {error && <p style={{ color: 'red', fontSize: '0.875rem' }}>{error}</p>}

        <button
          type="submit"
          style={{
            marginTop: '1rem',
            padding: '.75rem',
            background: '#111',
            color: '#fff',
            borderRadius: 4,
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          {isLogin ? 'Log In' : 'Sign Up'}
        </button>
      </form>

      <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem' }}>
        {isLogin ? "Don't have an account? " : "Already have an account? "}
        <button
          onClick={() => { setIsLogin(!isLogin); setError(''); }}
          style={{ background: 'none', border: 'none', textDecoration: 'underline', cursor: 'pointer', padding: 0 }}
        >
          {isLogin ? 'Sign up' : 'Log in'}
        </button>
      </div>
    </div>
  );
}
