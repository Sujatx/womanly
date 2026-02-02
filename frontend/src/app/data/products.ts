export interface Product {
  id: string;
  name: string;
  collection: string;
  price: number;
  salePrice?: number;
  images: string[];
  description: string;
  sizes: string[];
  colors: string[];
  inStock: boolean;
  badge?: 'new' | 'sale' | 'bestseller';
}

export const products: Product[] = [
  {
    id: '1',
    name: 'Silk Slip Dress',
    collection: 'Evening',
    price: 385,
    images: [
      'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=800&q=90',
      'https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=800&q=90'
    ],
    description: 'Luxurious silk slip dress with delicate bias cut. Crafted from 100% mulberry silk with adjustable straps and a flowing silhouette. Perfect for evening occasions.',
    sizes: ['XS', 'S', 'M', 'L', 'XL'],
    colors: ['Ivory', 'Black', 'Champagne'],
    inStock: true,
    badge: 'bestseller'
  },
  {
    id: '2',
    name: 'Cashmere Wrap Coat',
    collection: 'Outerwear',
    price: 795,
    images: [
      'https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=800&q=90',
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&q=90'
    ],
    description: 'Double-faced cashmere coat with an elegant wrap silhouette. Features wide lapels, self-tie belt, and Italian-crafted construction.',
    sizes: ['XS', 'S', 'M', 'L', 'XL'],
    colors: ['Camel', 'Charcoal', 'Cream'],
    inStock: true
  },
  {
    id: '3',
    name: 'Linen Shirt Dress',
    collection: 'Summer',
    price: 245,
    salePrice: 185,
    images: [
      'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=90',
      'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=800&q=90'
    ],
    description: 'Relaxed linen shirt dress with mother-of-pearl buttons. Classic collar and bracelet-length sleeves. Pre-washed for softness.',
    sizes: ['XS', 'S', 'M', 'L', 'XL'],
    colors: ['White', 'Sand', 'Olive'],
    inStock: true,
    badge: 'sale'
  },
  {
    id: '4',
    name: 'Tailored Wool Trousers',
    collection: 'Essentials',
    price: 295,
    images: [
      'https://images.unsplash.com/photo-1594633313593-bab3825d0caf?w=800&q=90',
      'https://images.unsplash.com/photo-1624206112918-f140f087f9b5?w=800&q=90'
    ],
    description: 'High-waisted wool trousers with a tailored fit. Features pressed creases, side pockets, and a concealed zip closure.',
    sizes: ['24', '26', '28', '30', '32'],
    colors: ['Black', 'Navy', 'Grey'],
    inStock: true
  },
  {
    id: '5',
    name: 'Merino Knit Turtleneck',
    collection: 'Knitwear',
    price: 185,
    images: [
      'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=800&q=90',
      'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=800&q=90'
    ],
    description: 'Fine gauge merino wool turtleneck. Lightweight yet warm with a slim fit. Ideal for layering or wearing alone.',
    sizes: ['XS', 'S', 'M', 'L', 'XL'],
    colors: ['Black', 'Ivory', 'Camel', 'Navy'],
    inStock: true
  },
  {
    id: '6',
    name: 'Leather Midi Skirt',
    collection: 'Modern Classic',
    price: 495,
    images: [
      'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=800&q=90',
      'https://images.unsplash.com/photo-1581044777550-4cfa60707c03?w=800&q=90'
    ],
    description: 'Butter-soft lambskin leather skirt with an A-line silhouette. Features a concealed side zip and fully lined interior.',
    sizes: ['XS', 'S', 'M', 'L', 'XL'],
    colors: ['Black', 'Chocolate'],
    inStock: false
  },
  {
    id: '7',
    name: 'Cotton Poplin Blouse',
    collection: 'Essentials',
    price: 165,
    images: [
      'https://images.unsplash.com/photo-1564257577-49e8f72d7f0d?w=800&q=90',
      'https://images.unsplash.com/photo-1591369822096-ffd140ec948f?w=800&q=90'
    ],
    description: 'Classic white poplin blouse with French cuffs and a relaxed fit. Crafted from 100% Egyptian cotton.',
    sizes: ['XS', 'S', 'M', 'L', 'XL'],
    colors: ['White', 'Ivory'],
    inStock: true,
    badge: 'new'
  },
  {
    id: '8',
    name: 'Wide Leg Denim',
    collection: 'Denim',
    price: 225,
    images: [
      'https://images.unsplash.com/photo-1582418702059-97ebafb35d09?w=800&q=90',
      'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&q=90'
    ],
    description: 'High-rise wide leg jeans in Japanese selvedge denim. Classic five-pocket styling with a full-length inseam.',
    sizes: ['24', '26', '28', '30', '32'],
    colors: ['Indigo', 'Black', 'Ecru'],
    inStock: true
  }
];

export interface CartItem extends Product {
  quantity: number;
  selectedSize: string;
  selectedColor: string;
}
