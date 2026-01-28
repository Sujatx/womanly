'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth-context';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const { login, signup } = useAuth();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await signup(email, password, fullName);
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
