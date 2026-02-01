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



  useEffect(() => {

    const init: Record<string, string> = {};

    for (const o of options) init[o.name] = o.values[0];

    setSelected(init);

  }, [options]);



    const activeVariant = useMemo(() => {



      return (



        variants.find((v) =>



          v.selectedOptions.every((so) => selected[so.name] === so.value)



        ) || variants[0]



      );



    }, [variants, selected]);



  



    const inventoryStatus = useMemo(() => {



      if (!activeVariant || !activeVariant.availableForSale) return 'OUT OF STOCK';



      if (activeVariant.stockQuantity < 5) return `ONLY ${activeVariant.stockQuantity} LEFT`;



      return 'IN STOCK';



    }, [activeVariant]);



  



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



  const priceText = `${activeVariant?.price.amount || '0'}`;



  function onAdd() {

    if (!activeVariant) return;

    add({

      id: String(activeVariant.id),

      productId: String(id),

      title,

      price: Number(activeVariant.price.amount),

      currencyCode: activeVariant.price.currencyCode || 'USD',

      qty: 1,

      image: images?.[0],

      selectedOptions: activeVariant.selectedOptions,

    });

    toast.success('ITEM ADDED TO BAG');

    setJustAdded(true);

    setTimeout(() => setJustAdded(false), 2000);

  }



  return (

    <div style={{ paddingBottom: '10rem' }}>

      <div className="bg-text" style={{ top: '15%' }}>{title.split(' ')[0]}</div>

      

      <div className="container" style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '5rem', alignItems: 'start', position: 'relative', zIndex: 1 }}>

        {/* LEFT: Gallery */}

        <section>

          <PDPGallery images={images} />

        </section>



        {/* RIGHT: Details */}

        <section style={{ paddingTop: '2rem' }}>

                    <span className="collection-tag" style={{ color: 'var(--muted)' }}>WINTER 2025 EDITION</span>

                    <h1 style={{ fontSize: '3rem', margin: '1rem 0', lineHeight: 1 }}>{title}</h1>

                    

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>

                      <p style={{ fontSize: '2rem', fontWeight: 900, margin: 0 }}>{priceText}</p>

                      <span style={{ 

                        fontSize: '0.7rem', 

                        fontWeight: 900, 

                        padding: '0.4rem 0.8rem', 

                        borderRadius: 'var(--radius-pill)',

                        background: inventoryStatus === 'OUT OF STOCK' ? '#ef4444' : 'var(--fg)',

                        color: 'white',

                        letterSpacing: '0.05em'

                      }}>

                        {inventoryStatus}

                      </span>

                    </div>

          

                    <div style={{ marginBottom: '3rem' }}>

                      <VariantSelector

                        options={options}

                        selected={selected}

                        disabledValues={disabledValues}

                        onChange={(name, value) => setSelected((prev) => ({ ...prev, [name]: value }))}

                      />

                    </div>

          

                    <div style={{ display: 'flex', gap: '1rem', marginBottom: '4rem' }}>

                      <button

                        type="button"

                        onClick={onAdd}

                        disabled={justAdded || !activeVariant?.availableForSale}

                        className="vexo-button"

                        style={{ flex: 1, height: '64px', fontSize: '1rem', opacity: activeVariant?.availableForSale ? 1 : 0.5 }}

                      >

                        {!activeVariant?.availableForSale ? 'SOLD OUT' : justAdded ? 'ADDED TO BAG' : 'ADD TO BAG'}

                      </button>

          

            <button 

              className="vexo-button vexo-button-outline"

              style={{ width: '64px', height: '64px', padding: 0, display: 'grid', placeItems: 'center' }}

            >

              <Heart />

            </button>

          </div>



          <div style={{ display: 'grid', gap: '2rem' }}>

            <div style={{ borderTop: '1px solid var(--border)', paddingTop: '1.5rem' }}>

              <h3 style={{ fontSize: '0.8rem', fontWeight: 900, marginBottom: '1rem' }}>PRODUCT DESCRIPTION</h3>

              <p style={{ lineHeight: 1.7 }}>{description}</p>

            </div>

            

            <div style={{ borderTop: '1px solid var(--border)', paddingTop: '1.5rem' }}>

              <button 

                onClick={() => setSizeGuideOpen(true)}

                style={{ background: 'none', border: 'none', fontWeight: 900, fontSize: '0.8rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '1rem' }}

              >

                <Ruler size={18} /> SIZE GUIDE & MEASUREMENTS

              </button>

            </div>



            <DeliveryReturns />

          </div>

        </section>

      </div>



      <SizeGuideModal open={sizeGuideOpen} onClose={() => setSizeGuideOpen(false)} />

    </div>

  );

}
