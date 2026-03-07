import { useEffect, useState } from 'react';
import { apiRequest } from '@/lib/api-client';
import { useToast } from '@/contexts/ToastContext';

export function VerifyEmailPage() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const { showToast } = useToast();

  useEffect(() => {
    // Extract token from URL hash (since we use hash-based routing)
    // Hash format: #/auth/verify?token=abc
    const hash = window.location.hash;
    const queryStart = hash.indexOf('?');
    const queryString = queryStart !== -1 ? hash.substring(queryStart + 1) : '';
    const params = new URLSearchParams(queryString);
    const token = params.get('token');

    console.log('[VerifyEmail] Hash:', hash);
    console.log('[VerifyEmail] Query string:', queryString);
    console.log('[VerifyEmail] Token:', token);

    if (!token) {
      setStatus('error');
      setMessage('Verification token is missing');
      return;
    }

    // Call backend to verify email
    async function verifyEmail() {
      try {
        console.log('[VerifyEmail] Calling API with token:', token);
        const response = await apiRequest<{ status: string; message: string }>(
          `/auth/verify-email?token=${token}`,
          { method: 'POST' }
        );
        
        console.log('[VerifyEmail] Success response:', response);
        setStatus('success');
        setMessage(response.message || 'Email verified successfully!');

        // Keep frontend auth state in sync if user is already logged in.
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          try {
            const parsedUser = JSON.parse(storedUser);
            if (parsedUser && !parsedUser.is_verified) {
              localStorage.setItem('user', JSON.stringify({ ...parsedUser, is_verified: true }));
            }
          } catch {
            // Ignore user parse issues and continue verification UX.
          }
        }

        showToast('Email verified! You can now log in.', 'success');
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          window.location.hash = '#/auth';
        }, 3000);
      } catch (error: any) {
        console.error('[VerifyEmail] Error:', error);
        setStatus('error');
        setMessage(error.message || 'Verification failed. Token may be expired or invalid.');
        showToast('Verification failed', 'error');
      }
    }

    verifyEmail();
  }, [showToast]);

  return (
    <section className="container mx-auto px-6 py-16 md:py-24 flex items-center justify-center min-h-[60vh]">
      <div className="max-w-md w-full text-center">
        {status === 'loading' && (
          <>
            <div className="mb-6 flex justify-center">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-foreground"></div>
            </div>
            <h1 className="font-headline text-2xl md:text-3xl mb-4">Verifying Your Email</h1>
            <p className="text-muted">Please wait while we verify your email address...</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="mb-6 flex justify-center">
              <svg 
                className="w-16 h-16 text-green-500" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" 
                />
              </svg>
            </div>
            <h1 className="font-headline text-2xl md:text-3xl mb-4 text-green-700">Email Verified!</h1>
            <p className="text-muted mb-6">{message}</p>
            <p className="text-sm text-muted">Redirecting you to login...</p>
            <a 
              href="#/auth" 
              className="mt-4 inline-block bg-foreground text-white px-8 py-3 rounded-[var(--radius-sm)] font-bold hover:bg-accent transition-colors"
            >
              Go to Login
            </a>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="mb-6 flex justify-center">
              <svg 
                className="w-16 h-16 text-red-500" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" 
                />
              </svg>
            </div>
            <h1 className="font-headline text-2xl md:text-3xl mb-4 text-red-700">Verification Failed</h1>
            <p className="text-muted mb-6">{message}</p>
            <div className="space-y-3">
              <a 
                href="#/auth" 
                className="block bg-foreground text-white px-8 py-3 rounded-[var(--radius-sm)] font-bold hover:bg-accent transition-colors"
              >
                Back to Login
              </a>
              <p className="text-sm text-muted">
                Need a new verification link? Log in and request a new one from your profile.
              </p>
            </div>
          </>
        )}
      </div>
    </section>
  );
}

export default VerifyEmailPage;
