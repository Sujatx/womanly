// components/SizeGuideModal.tsx
// Accessible modal dialog for Size Guide using WAI-ARIA practices.
// - role="dialog" aria-modal="true" with labelled title for screen readers.
// - Focus trap and Escape key to close.
// - Click on backdrop closes the modal.

'use client';

import { useEffect, useRef } from 'react';

type Props = {
  open: boolean;
  onClose: () => void;
  title?: string;
  category?: string; // e.g., "Dresses" to show tailored size info
  children?: React.ReactNode; // optional custom content
};

export function SizeGuideModal({ open, onClose, title = 'Size Guide', category, children }: Props) {
  const dialogRef = useRef<HTMLDivElement>(null);

  // Focus the dialog when opened and trap focus within
  useEffect(() => {
    if (!open) return;
    const dialog = dialogRef.current;
    if (!dialog) return;

    // Save previously focused element
    const prev = document.activeElement as HTMLElement | null;

    // Focus first focusable element inside
    const focusables = dialog.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    (focusables[0] || dialog).focus();

    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
      if (e.key === 'Tab') {
        // Trap focus
        const list = Array.from(focusables).filter(el => !el.hasAttribute('disabled'));
        if (!list.length) return;
        const first = list[0];
        const last = list[list.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }

    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('keydown', onKey);
      // Restore focus
      prev?.focus();
    };
  }, [open, onClose]);

  if (!open) return null;

  function onBackdrop(e: React.MouseEvent<HTMLDivElement>) {
    if (e.target === e.currentTarget) onClose();
  }

  return (
    <div
      onClick={onBackdrop}
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
        display: 'grid', placeItems: 'center', zIndex: 50,
      }}
      aria-hidden={false}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="size-guide-title"
        className="rounded"
        style={{
          background: '#fff', color: '#111',
          width: 'min(680px, 92vw)',
          maxHeight: '80vh', overflow: 'auto',
          padding: '1rem', boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '.5rem' }}>
          <h2 id="size-guide-title" style={{ fontSize: '1.1rem', fontWeight: 600 }}>
            {title}{category ? ` — ${category}` : ''}
          </h2>
          <button
            onClick={onClose}
            aria-label="Close size guide"
            className="rounded"
            style={{ border: '1px solid #ddd', padding: '.25rem .5rem', background: '#fff' }}
          >
            ✕
          </button>
        </div>

        {/* Example content: replace with real charts later */}
        {children ?? (
          <div style={{ fontSize: '.95rem' }}>
            <p className="muted" style={{ marginBottom: '.75rem' }}>
              Measure bust, waist, and hips; compare to the chart below for a confident fit. Units in inches and centimeters.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '.5rem' }}>
              <div style={{ fontWeight: 600 }}>Size</div>
              <div style={{ fontWeight: 600 }}>Bust</div>
              <div style={{ fontWeight: 600 }}>Waist</div>
              <div style={{ fontWeight: 600 }}>Hips</div>

              <div>XS</div><div>31–32 in / 79–81 cm</div><div>24–25 in / 61–63 cm</div><div>34–35 in / 86–89 cm</div>
              <div>S</div><div>33–34 in / 84–86 cm</div><div>26–27 in / 66–69 cm</div><div>36–37 in / 91–94 cm</div>
              <div>M</div><div>35–36 in / 89–91 cm</div><div>28–29 in / 71–74 cm</div><div>38–39 in / 97–99 cm</div>
              <div>L</div><div>37–39 in / 94–99 cm</div><div>30–32 in / 76–81 cm</div><div>40–42 in / 102–107 cm</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
