// app/auth/verify/page.tsx
'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

function VerifyContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('VERIFYING YOUR ACCOUNT...');
  const router = useRouter();

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('MISSING VERIFICATION TOKEN');
      return;
    }

    async function verify() {
      try {
        const res = await fetch(`${API_URL}/auth/verify-email?token=${token}`, {
          method: 'POST'
        });
        const data = await res.json();
        if (res.ok) {
          setStatus('success');
          setMessage('ACCOUNT VERIFIED SUCCESSFULLY');
        } else {
          setStatus('error');
          setMessage(data.detail || 'VERIFICATION FAILED');
        }
      } catch (err) {
        setStatus('error');
        setMessage('NETWORK ERROR');
      }
    }

    verify();
  }, [token]);

  return (
    <div style={{ minHeight: '80vh', display: 'grid', placeItems: 'center', textAlign: 'center', padding: '2rem' }}>
      <div className="bg-text">VERIFY</div>
      
      <div className="card" style={{ 
        padding: '4rem', 
        borderRadius: 'var(--radius-lg)', 
        background: 'rgba(255,255,255,0.4)', 
        border: '1px solid var(--border)',
        maxWidth: '500px',
        width: '100%',
        position: 'relative',
        zIndex: 1,
        backdropFilter: 'blur(10px)'
      }}>
        {status === 'loading' && <Loader2 size={64} className="animate-spin" style={{ margin: '0 auto 2rem', opacity: 0.2 }} />}
        {status === 'success' && <CheckCircle size={64} style={{ color: '#22c55e', margin: '0 auto 2rem' }} />}
        {status === 'error' && <XCircle size={64} style={{ color: '#ef4444', margin: '0 auto 2rem' }} />}

        <h1 style={{ fontSize: '2rem', fontWeight: 900, marginBottom: '1rem' }}>{message}</h1>
        
        {status === 'success' && (
          <p style={{ fontWeight: 800, color: 'var(--muted)', marginBottom: '2.5rem' }}>
            YOUR ACCOUNT HAS BEEN ACTIVATED. YOU CAN NOW ACCESS ALL PREMIUM FEATURES.
          </p>
        )}

        <Link href={status === 'success' ? '/auth' : '/'} className="vexo-button" style={{ width: '100%', height: '64px' }}>
          {status === 'success' ? 'CONTINUE TO LOGIN' : 'BACK TO HOME'}
        </Link>
      </div>
    </div>
  );
}

export default function VerifyPage() {
  return (
    <Suspense fallback={<div>LOADING...</div>}>
      <VerifyContent />
    </Suspense>
  );
}
