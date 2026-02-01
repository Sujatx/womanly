// app/account/profile/page.tsx
'use client';

import { useAuth } from '@/lib/auth-context';
import { User, Mail, Shield } from 'lucide-react';

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <div>
      <header style={{ marginBottom: '3rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>PERSONAL PROFILE</h2>
        <p style={{ color: 'var(--muted)', fontWeight: 700, fontSize: '0.9rem' }}>MANAGE YOUR PERSONAL INFORMATION AND SECURITY</p>
      </header>

      <div style={{ display: 'grid', gap: '2rem', maxWidth: '600px' }}>
        <div style={{ 
          background: 'rgba(255,255,255,0.3)', 
          padding: '2.5rem', 
          borderRadius: 'var(--radius-lg)', 
          border: '1px solid var(--border)',
          display: 'grid',
          gap: '2rem'
        }}>
          <div>
            <label style={{ fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <User size={14} /> FULL NAME
            </label>
            <p style={{ fontSize: '1.2rem', fontWeight: 900, textTransform: 'uppercase' }}>{user?.full_name || 'NOT PROVIDED'}</p>
          </div>

          <div>
            <label style={{ fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <Mail size={14} /> EMAIL ADDRESS
            </label>
            <p style={{ fontSize: '1.2rem', fontWeight: 900 }}>{user?.email}</p>
          </div>

          <div style={{ borderTop: '1px solid var(--border)', paddingTop: '2rem' }}>
            <label style={{ fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <Shield size={14} /> ACCOUNT STATUS
            </label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ 
                width: '10px', 
                height: '100px', 
                background: '#22c55e', 
                borderRadius: 'var(--radius-pill)',
                display: 'inline-block',
                height: '10px'
              }} />
              <p style={{ fontSize: '0.9rem', fontWeight: 800 }}>VERIFIED CUSTOMER</p>
            </div>
          </div>
        </div>

        <button className="vexo-button" style={{ height: '64px' }}>EDIT PROFILE INFORMATION</button>
      </div>
    </div>
  );
}
