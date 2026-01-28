// components/PDPClient.tsx
// Two-column PDP: LEFT = gallery (with vertical thumbnails), RIGHT = details/options/buy/add-to-cart.

'use client';

import { useEffect, useMemo, useState } from 'react';
import { PDPGallery } from '@/components/PDPGallery';
import { VariantSelector } from '@/components/VariantSelector';
import { SizeGuideModal } from '@/components/SizeGuideModal';
import { DeliveryReturns } from '@/components/DeliveryReturns';
import { CheckoutButtons } from '@/components/CheckoutButtons';
import { useCart } from '@/lib/cart';
import { toast } from 'sonner';
import { ShoppingBag, Ruler, Check } from 'lucide-react';

type Money = { amount: string; currencyCode: string };
type Variant = {
  id: string;
  title: string;
  availableForSale: boolean;
  price: Money;
  selectedOptions: { name: string; value: string }[];
};

export default function PDPClient({
  id,
  title,
  description,
  images,
  options,
  variants,
  tags,
}: {
  id: number;
  title: string;
  description: string;
  images: { url: string; altText?: string }[];
  options: { name: string; values: string[] }[];
  variants: Variant[];
  tags?: string[];
}) {
  const [selected, setSelected] = useState<Record<string, string>>({});
  const [sizeGuideOpen, setSizeGuideOpen] = useState(false);
  const [justAdded, setJustAdded] = useState(false);
  const { add } = useCart();

  // Defaults: first value per option (covers size/color, etc.)
  useEffect(() => {
    const init: Record<string, string> = {};
    for (const o of options) init[o.name] = o.values[0];
    setSelected(init);
  }, [options]);

  // Active variant from selections
  const activeVariant = useMemo(() => {
    return (
      variants.find((v) =>
        v.selectedOptions.every((so) => selected[so.name] === so.value)
      ) || variants[0]
    );
  }, [variants, selected]);

  // Disable unavailable values
  const disabledValues = useMemo(() => {
    const map: Record<string, string[]> = {};
    for (const opt of options) {
      const others = options.filter((o) => o.name !== opt.name);
      const dis: string[] = [];
      for (const value of opt.values) {
        const matches = variants.some((v) => {
          if (!v.availableForSale) return false;
          for (const o of others) {
            const want = selected[o.name];
            const has = v.selectedOptions.find((so) => so.name === o.name)?.value;
            if (want && has && want !== has) return false;
          }
          return v.selectedOptions.find((so) => so.name === opt.name)?.value === value;
        });
        if (!matches) dis.push(value);
      }
      map[opt.name] = dis;
    }
    return map;
  }, [options, variants, selected]);

  const priceText = `${activeVariant.price.amount} ${activeVariant.price.currencyCode}`;

  function onAdd() {
    add({
      id: String(id), // Use actual product ID
      productId: String(id), // Ensure productId is set for local/sync logic
      title,
      price: Number(activeVariant.price.amount),
      currencyCode: activeVariant.price.currencyCode || 'USD',
      qty: 1,
      image: images?.[0],
      selectedOptions: activeVariant.selectedOptions,
    });
    toast.success('Added to cart', {
      description: `${title} - ${activeVariant.title}`,
      action: {
        label: 'View Cart',
        onClick: () => window.dispatchEvent(new CustomEvent('cart:open'))
      }
    });
    setJustAdded(true);
    setTimeout(() => setJustAdded(false), 2000);
  }

  return (
    <div style={{ display: 'grid', gap: '2rem', gridTemplateColumns: '1fr' }}>
      <style jsx>{`
        @media (min-width: 768px) {
          .pdp-grid {
            grid-template-columns: minmax(0, 680px) 1fr; /* LEFT gallery, RIGHT details */
            align-items: start;
          }
        }
      `}</style>

      <div className="pdp-grid" style={{ display: 'grid', gap: '2rem', gridTemplateColumns: '1fr' }}>
        {/* LEFT: Gallery group; tweak maxWidth to control desktop image size */}
        <section style={{ maxWidth: 680, width: '100%', justifySelf: 'start' }}>
          <PDPGallery images={images} />
        </section>

        {/* RIGHT: Details + options + actions (beside the main image) */}
        <section style={{ minWidth: 0 }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '0.25rem' }}>{title}</h1>
          <p style={{ marginTop: '.25rem', fontSize: '1.25rem', fontWeight: 600 }}>{priceText}</p>

          {/* Size/Color/etc. options */}
          <div style={{ marginTop: '2rem' }}>
            <VariantSelector
              options={options}
              selected={selected}
              disabledValues={disabledValues}
              onChange={(name, value) => setSelected((prev) => ({ ...prev, [name]: value }))}
            />
          </div>

          {/* Size guide */}
          <div style={{ marginTop: '1rem' }}>
            <button
              type="button"
              onClick={() => setSizeGuideOpen(true)}
              style={{ 
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                background: 'none',
                padding: '0',
                border: 'none',
                textDecoration: 'underline',
                fontSize: '0.875rem',
                fontWeight: 500,
                cursor: 'pointer',
                color: '#666'
              }}
            >
              <Ruler size={16} />
              Size Guide
            </button>
          </div>

          {/* Buy/Add to cart */}
          <div style={{ marginTop: '2rem', display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={onAdd}
              disabled={justAdded}
              style={{ 
                flex: 1,
                minWidth: '200px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.75rem',
                borderRadius: '12px', 
                padding: '1rem', 
                background: justAdded ? '#f0f0f0' : '#fff', 
                border: '1px solid #111',
                color: '#111',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => !justAdded && (e.currentTarget.style.background = '#f9f9f9')}
              onMouseLeave={(e) => !justAdded && (e.currentTarget.style.background = '#fff')}
            >
              {justAdded ? (
                <>
                  <Check size={18} />
                  Added to bag
                </>
              ) : (
                <>
                  <ShoppingBag size={18} />
                  Add to bag
                </>
              )}
            </button>

            <div style={{ flex: 1, minWidth: '200px' }}>
              <CheckoutButtons merchandiseId={activeVariant?.id} />
            </div>
          </div>

          {/* Delivery & Returns */}
          <div style={{ marginTop: '2rem' }}>
            <DeliveryReturns />
          </div>

          {/* Details */}
          <div style={{ marginTop: '2.5rem', borderTop: '1px solid #f0f0f0', paddingTop: '1.5rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Description</h3>
            <p style={{ fontSize: '0.95rem', color: '#444', lineHeight: 1.6 }}>{description}</p>
          </div>
        </section>
      </div>

      {/* Size Guide modal */}
      <SizeGuideModal open={sizeGuideOpen} onClose={() => setSizeGuideOpen(false)} category={tags?.[0]} />
    </div>
  );
}