// app/account/addresses/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { Plus, Trash2, MapPin, Check } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export default function AddressesPage() {
  const { token } = useAuth();
  const [addresses, setAddresses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'India',
    is_default: false,
    address_type: 'home'
  });

  useEffect(() => {
    if (token) fetchAddresses();
  }, [token]);

  async function fetchAddresses() {
    try {
      const res = await fetch(`${API_URL}/addresses/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to fetch addresses');
      const data = await res.json();
      setAddresses(data);
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const res = await fetch(`${API_URL}/addresses/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      if (!res.ok) throw new Error('Failed to save address');
      toast.success('ADDRESS SAVED');
      setShowForm(false);
      fetchAddresses();
    } catch (err: any) {
      toast.error(err.message);
    }
  }

  async function deleteAddress(id: number) {
    try {
      const res = await fetch(`${API_URL}/addresses/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to delete');
      toast.success('ADDRESS REMOVED');
      fetchAddresses();
    } catch (err: any) {
      toast.error(err.message);
    }
  }

  if (loading) return <div className="skeleton" style={{ width: '100%', height: '400px' }} />;

  return (
    <div>
      <header style={{ marginBottom: '3rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>ADDRESS BOOK</h2>
          <p style={{ color: 'var(--muted)', fontWeight: 700, fontSize: '0.9rem' }}>MANAGE YOUR SHIPPING AND BILLING LOCATIONS</p>
        </div>
        <button 
          onClick={() => setShowForm(!showForm)}
          className="vexo-button" 
          style={{ padding: '0.8rem 1.5rem', fontSize: '0.8rem' }}
        >
          {showForm ? 'CANCEL' : 'ADD NEW ADDRESS'}
        </button>
      </header>

      {showForm && (
        <form onSubmit={onSubmit} style={{ 
          background: 'rgba(255,255,255,0.4)', 
          padding: '3rem', 
          borderRadius: 'var(--radius-lg)', 
          border: '1px solid var(--border)',
          marginBottom: '4rem',
          display: 'grid',
          gap: '1.5rem',
          gridTemplateColumns: '1fr 1fr'
        }}>
          <div style={{ gridColumn: 'span 2' }}>
            <label style={{ fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)' }}>FULL NAME</label>
            <input 
              required
              className="card"
              style={{ width: '100%', padding: '1rem', marginTop: '0.5rem', background: 'white' }} 
              value={formData.full_name}
              onChange={e => setFormData({...formData, full_name: e.target.value})}
            />
          </div>
          <div>
            <label style={{ fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)' }}>PHONE NUMBER</label>
            <input 
              required
              className="card"
              style={{ width: '100%', padding: '1rem', marginTop: '0.5rem', background: 'white' }} 
              value={formData.phone}
              onChange={e => setFormData({...formData, phone: e.target.value})}
            />
          </div>
          <div>
            <label style={{ fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)' }}>POSTAL CODE</label>
            <input 
              required
              className="card"
              style={{ width: '100%', padding: '1rem', marginTop: '0.5rem', background: 'white' }} 
              value={formData.postal_code}
              onChange={e => setFormData({...formData, postal_code: e.target.value})}
            />
          </div>
          <div style={{ gridColumn: 'span 2' }}>
            <label style={{ fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)' }}>ADDRESS LINE 1</label>
            <input 
              required
              className="card"
              style={{ width: '100%', padding: '1rem', marginTop: '0.5rem', background: 'white' }} 
              value={formData.address_line1}
              onChange={e => setFormData({...formData, address_line1: e.target.value})}
            />
          </div>
          <div>
            <label style={{ fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)' }}>CITY</label>
            <input 
              required
              className="card"
              style={{ width: '100%', padding: '1rem', marginTop: '0.5rem', background: 'white' }} 
              value={formData.city}
              onChange={e => setFormData({...formData, city: e.target.value})}
            />
          </div>
          <div>
            <label style={{ fontSize: '0.7rem', fontWeight: 900, color: 'var(--muted)' }}>STATE</label>
            <input 
              required
              className="card"
              style={{ width: '100%', padding: '1rem', marginTop: '0.5rem', background: 'white' }} 
              value={formData.state}
              onChange={e => setFormData({...formData, state: e.target.value})}
            />
          </div>
          <div style={{ gridColumn: 'span 2', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <input 
              type="checkbox"
              id="is_default"
              checked={formData.is_default}
              onChange={e => setFormData({...formData, is_default: e.target.checked})}
            />
            <label htmlFor="is_default" style={{ fontSize: '0.8rem', fontWeight: 800 }}>SET AS DEFAULT ADDRESS</label>
          </div>
          <button type="submit" className="vexo-button" style={{ gridColumn: 'span 2', height: '64px' }}>SAVE ADDRESS</button>
        </form>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '2rem' }}>
        {addresses.map(addr => (
          <div key={addr.id} style={{ 
            background: 'rgba(255,255,255,0.3)', 
            padding: '2rem', 
            borderRadius: 'var(--radius-lg)', 
            border: '1px solid var(--border)',
            position: 'relative'
          }}>
            {addr.is_default && (
              <span style={{ 
                position: 'absolute', 
                top: '2rem', 
                right: '2rem', 
                fontSize: '0.6rem', 
                fontWeight: 900, 
                background: 'var(--fg)', 
                color: 'white', 
                padding: '0.4rem 0.8rem', 
                borderRadius: 'var(--radius-pill)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <Check size={12} /> DEFAULT
              </span>
            )}
            <MapPin size={24} style={{ marginBottom: '1.5rem', opacity: 0.5 }} />
            <h3 style={{ fontSize: '1rem', fontWeight: 900, marginBottom: '0.5rem', textTransform: 'uppercase' }}>{addr.full_name}</h3>
            <p style={{ fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--fg)', fontWeight: 600 }}>
              {addr.address_line1}<br />
              {addr.address_line2 && <>{addr.address_line2}<br /></>}
              {addr.city}, {addr.state} - {addr.postal_code}<br />
              {addr.country}
            </p>
            <p style={{ fontSize: '0.8rem', fontWeight: 700, marginTop: '1rem', color: 'var(--muted)' }}>PHONE: {addr.phone}</p>
            
            <button 
              onClick={() => deleteAddress(addr.id)}
              style={{ 
                marginTop: '2rem', 
                background: 'none', 
                border: 'none', 
                color: '#ef4444', 
                fontSize: '0.7rem', 
                fontWeight: 900, 
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              <Trash2 size={14} /> REMOVE ADDRESS
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
