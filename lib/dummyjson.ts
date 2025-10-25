// lib/dummyjson.ts
// Minimal client for DummyJSON products with mappers for your UI.
// Endpoints covered: products by category, product by id, products search, pagination via limit/skip.

const BASE = 'https://dummyjson.com';

// Types
export type DummyProduct = {
  id: number;
  title: string;
  description: string;
  category: string;
  price: number;
  brand?: string;
  images: string[];
  thumbnail?: string;
  tags?: string[];
};

export type SearchResult = {
  products: DummyProduct[];
  total: number;
  skip: number;
  limit: number;
};

// Internal fetcher
async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`DummyJSON error ${res.status}`);
  return res.json() as Promise<T>;
}

// Map app collection handles -> DummyJSON categories
export const categoryMap: Record<string, string> = {
  'new-in': 'womens-dresses',   // demo “new in” using a rich category
  'dresses': 'womens-dresses',
  'tops': 'tops',
  'bottoms': 'womens-shoes',    // reuse as “bottoms” placeholder
  'sale': 'womens-bags',        // reuse as “sale” placeholder
};

// Category products (PLP)
// limit: page size, page: 1-based page index
export async function getCategoryProducts(appHandle: string, limit = 24, page = 1): Promise<DummyProduct[]> {
  const cat = categoryMap[appHandle] || appHandle;
  const skip = Math.max(0, (page - 1) * limit);
  const data = await fetchJSON<{ products: DummyProduct[] }>(
    `/products/category/${encodeURIComponent(cat)}?limit=${limit}&skip=${skip}`
  );
  return data.products;
}

// Single product (PDP)
export async function getProductById(id: string | number): Promise<DummyProduct> {
  return fetchJSON<DummyProduct>(`/products/${id}`);
}

// Search with pagination (global search)
export async function searchProducts(q: string, limit = 24, page = 1): Promise<SearchResult> {
  const safeQ = (q || '').trim();
  const skip = Math.max(0, (page - 1) * limit);
  return fetchJSON<SearchResult>(`/products/search?q=${encodeURIComponent(safeQ)}&limit=${limit}&skip=${skip}`);
}

// Mapper: DummyProduct -> ProductCard props
export function toCard(p: DummyProduct) {
  const image = p.images?.[0] ? { url: p.images[0], altText: p.title } : undefined;
  return {
    handle: String(p.id), // links to /products/{id}
    title: p.title,
    image,
    hoverImage: p.images?.[1] ? { url: p.images[1], altText: p.title } : undefined,
    price: { amount: String(p.price), currencyCode: 'USD' },
  };
}

// Mapper: DummyProduct -> PDPClient props (simulated options/variants)
export function toPDP(p: DummyProduct) {
  const images = (p.images || []).map((url) => ({ url, altText: p.title }));
  // DummyJSON lacks variants; simulate a couple for demo UX
  const options = [
    { name: 'Size', values: ['S', 'M', 'L'] },
    { name: 'Color', values: ['Black', 'Ivory'] },
  ];
  const variants = [
    {
      id: `var_${p.id}_S_Black`,
      title: 'S / Black',
      availableForSale: true,
      price: { amount: String(p.price), currencyCode: 'USD' },
      selectedOptions: [
        { name: 'Size', value: 'S' },
        { name: 'Color', value: 'Black' },
      ],
    },
    {
      id: `var_${p.id}_M_Ivory`,
      title: 'M / Ivory',
      availableForSale: true,
      price: { amount: String(p.price), currencyCode: 'USD' },
      selectedOptions: [
        { name: 'Size', value: 'M' },
        { name: 'Color', value: 'Ivory' },
      ],
    },
  ];

  return {
    title: p.title,
    description: p.description,
    images,
    options,
    variants,
    tags: p.tags || [],
  };
}
