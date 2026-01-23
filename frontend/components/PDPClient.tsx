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

type Money = { amount: string; currencyCode: string };
type Variant = {
  id: string;
  title: string;
  availableForSale: boolean;
  price: Money;
  selectedOptions: { name: string; value: string }[];
};

export default function PDPClient({
  title,
  description,
  images,
  options,
  variants,
  tags,
}: {
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
      id: activeVariant.id,
      title,
      price: Number(activeVariant.price.amount),
      currencyCode: activeVariant.price.currencyCode || 'USD',
      qty: 1,
      image: images?.[0],
      selectedOptions: activeVariant.selectedOptions,
    });
    setJustAdded(true);
    setTimeout(() => setJustAdded(false), 1200);
    try { window.dispatchEvent(new CustomEvent('cart:open')); } catch {}
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
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>{title}</h1>
          <p style={{ marginTop: '.25rem', fontSize: '1.1rem' }}>{priceText}</p>

          {/* Size/Color/etc. options */}
          <div style={{ marginTop: '1rem' }}>
            <VariantSelector
              options={options}
              selected={selected}
              disabledValues={disabledValues}
              onChange={(name, value) => setSelected((prev) => ({ ...prev, [name]: value }))}
            />
          </div>

          {/* Size guide */}
          <div style={{ marginTop: '.5rem' }}>
            <button
              type="button"
              onClick={() => setSizeGuideOpen(true)}
              className="rounded"
              style={{ background: '#f2f2f2', padding: '.4rem .75rem', border: '1px solid #ddd' }}
            >
              Size Guide
            </button>
          </div>

          {/* Buy/Add to cart */}
          <div style={{ marginTop: '1rem', display: 'flex', gap: '.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={onAdd}
              className="rounded"
              style={{ border: '1px solid #ddd', padding: '.5rem .75rem', background: '#fff', cursor: 'pointer' }}
            >
              Add to cart
            </button>

            <CheckoutButtons merchandiseId={activeVariant?.id} />

            {justAdded && (
              <span aria-live="polite" className="muted" style={{ marginLeft: '.25rem', fontSize: 12 }}>
                Added
              </span>
            )}
          </div>

          {/* Delivery & Returns */}
          <div style={{ marginTop: '.75rem' }}>
            <DeliveryReturns />
          </div>

          {/* Details */}
          <div style={{ marginTop: '1.25rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Details</h3>
            <p className="muted" style={{ marginTop: '.25rem' }}>{description}</p>
          </div>
        </section>
      </div>

      {/* Size Guide modal */}
      <SizeGuideModal open={sizeGuideOpen} onClose={() => setSizeGuideOpen(false)} category={tags?.[0]} />
    </div>
  );
}
