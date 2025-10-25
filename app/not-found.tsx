// app/not-found.tsx
import Link from 'next/link';

export default function NotFound() {
  return (
    <div style={{ padding: '2rem 0' }}>
      <h2>Not Found</h2>
      <p className="muted">Could not find the requested page or item.</p>
      <p style={{ marginTop: '.75rem' }}><Link href="/">Go home</Link></p>
    </div>
  );
}
