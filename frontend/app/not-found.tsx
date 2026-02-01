import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function NotFound() {
  return (
    <div style={{ minHeight: '70vh', display: 'grid', placeItems: 'center', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
      <div className="bg-text">404</div>
      
      <div style={{ position: 'relative', zIndex: 1 }}>
        <h1 style={{ fontSize: '4rem', fontWeight: 900, marginBottom: '1rem' }}>LOST IN FASHION?</h1>
        <p style={{ fontWeight: 800, color: 'var(--muted)', fontSize: '1rem', letterSpacing: '0.05em', marginBottom: '3rem' }}>
          THE PAGE YOU ARE LOOKING FOR DOES NOT EXIST OR HAS BEEN MOVED.
        </p>
        
        <Link href="/" className="vexo-button">
          BACK TO HOME <ArrowLeft size={20} />
        </Link>
      </div>
    </div>
  );
}
