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
    <div style={{ minHeight: '80vh', display: 'grid', placeItems: 'center', position: 'relative', overflow: 'hidden', padding: '2rem' }}>
      <div className="bg-text" style={{ fontSize: '20vw' }}>{isLogin ? 'LOGIN' : 'JOIN'}</div>
      
      <div className="card" style={{ 
        width: '100%', 
        maxWidth: '450px', 
        padding: '3.5rem', 
        borderRadius: 'var(--radius-lg)', 
        position: 'relative', 
        zIndex: 1,
        background: 'rgba(255,255,255,0.4)',
        backdropFilter: 'blur(10px)',
        border: '1px solid var(--border)'
      }}>
        <header style={{ marginBottom: '3rem', textAlign: 'center' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 900, marginBottom: '0.5rem' }}>
            {isLogin ? 'WELCOME BACK' : 'BECOME A MEMBER'}
          </h1>
          <p style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--muted)', letterSpacing: '0.05em' }}>
            {isLogin ? 'ENTER YOUR DETAILS TO ACCESS YOUR BAG' : 'CREATE YOUR ACCOUNT FOR A PREMIUM EXPERIENCE'}
          </p>
        </header>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {!isLogin && (
             <div>
               <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)', marginBottom: '0.5rem' }}>FULL NAME</label>
               <input
                 type="text"
                 required
                 value={fullName}
                 onChange={(e) => setFullName(e.target.value)}
                 className="card"
                 style={{ width: '100%', padding: '1.25rem', background: 'white', borderRadius: 'var(--radius-sm)' }}
               />
             </div>
          )}

          <div>
            <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)', marginBottom: '0.5rem' }}>EMAIL ADDRESS</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="card"
              style={{ width: '100%', padding: '1.25rem', background: 'white', borderRadius: 'var(--radius-sm)' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)', marginBottom: '0.5rem' }}>PASSWORD</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="card"
              style={{ width: '100%', padding: '1.25rem', background: 'white', borderRadius: 'var(--radius-sm)' }}
            />
          </div>

          {error && (
            <div style={{ background: '#fef2f2', color: '#ef4444', padding: '1rem', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', fontWeight: 800, border: '1px solid #fee2e2' }}>
              {error.toUpperCase()}
            </div>
          )}

          <button
            type="submit"
            className="vexo-button"
            style={{ width: '100%', height: '64px', marginTop: '1rem' }}
          >
            {isLogin ? 'LOG IN' : 'SIGN UP'}
          </button>
        </form>

        <div style={{ marginTop: '2.5rem', textAlign: 'center' }}>
          <button
            onClick={() => { setIsLogin(!isLogin); setError(''); }}
            style={{ 
              background: 'none', 
              border: 'none', 
              fontSize: '0.75rem', 
              fontWeight: 900, 
              color: 'var(--fg)', 
              textDecoration: 'underline', 
              cursor: 'pointer', 
              letterSpacing: '0.05em' 
            }}
          >
            {isLogin ? 'DON’T HAVE AN ACCOUNT? JOIN US' : 'ALREADY A MEMBER? LOG IN'}
          </button>
        </div>
      </div>
    </div>
  );
}
