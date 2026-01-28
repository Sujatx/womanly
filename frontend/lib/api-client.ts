const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export type Product = {
  id: number;
  title: string;
  description: string;
  price: number;
  brand?: string;
  images: string[];
  thumbnail?: string;
  tags?: string[];
  category_slug?: string;
};

export type ProductList = {
  items: Product[];
  total: number;
  skip: number;
  limit: number;
};

async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Unknown error' }));
    const message = typeof error.detail === 'string' 
      ? error.detail 
      : JSON.stringify(error.detail) || `API error ${res.status}`;
    throw new Error(message);
  }

  return res.json() as Promise<T>;
}

// Products
export async function getProducts(
  page = 1, 
  limit = 24, 
  category?: string, 
  q?: string
): Promise<ProductList> {
  const skip = (page - 1) * limit;
  const params = new URLSearchParams({ 
    skip: skip.toString(), 
    limit: limit.toString() 
  });
  
  if (category) params.append('category', category);
  if (q) params.append('q', q);

  return fetchAPI<ProductList>(`/products?${params.toString()}`, { cache: 'no-store' });
}

export async function getProduct(id: string | number): Promise<Product> {
  return fetchAPI<Product>(`/products/${id}`, { cache: 'no-store' });
}

export async function getCategories(): Promise<{ id: number; name: string; slug: string }[]> {
  return fetchAPI<{ id: number; name: string; slug: string }[]>('/categories', { cache: 'force-cache' });
}

export async function searchProducts(q: string, limit = 24, page = 1): Promise<ProductList> {
  const skip = (page - 1) * limit;
  return fetchAPI<ProductList>(`/products?q=${encodeURIComponent(q)}&limit=${limit}&skip=${skip}`, { cache: 'no-store' });
}

export function toCard(p: Product) {
    const image = p.images?.[0] ? { url: p.images[0], altText: p.title } : undefined;
    return {
      handle: String(p.id),
      title: p.title,
      image,
      hoverImage: p.images?.[1] ? { url: p.images[1], altText: p.title } : undefined,
      price: { amount: String(p.price), currencyCode: 'USD' },
    };
}

// Cart Types
export type CartItem = {
    id: number;
    product_id: number;
    quantity: number;
    selected_options?: string;
    product?: Product;
};

export type Cart = {
    id: number;
    items: CartItem[];
    count: number;
    subtotal: number;
};

// Cart API
function getAuthHeaders() {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

export async function getCart(): Promise<Cart> {
    return fetchAPI<Cart>('/cart', { headers: getAuthHeaders(), cache: 'no-store' });
}

export async function addToCart(product_id: number, quantity: number, selected_options?: string): Promise<Cart> {
    return fetchAPI<Cart>('/cart/items', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ product_id, quantity, selected_options }),
    });
}

export async function removeFromCart(item_id: number): Promise<Cart> {
    return fetchAPI<Cart>(`/cart/items/${item_id}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
    });
}

// Payment API
export async function createPaymentOrder(): Promise<{ id: string; amount: number; currency: string; db_order_id: number }> {
    return fetchAPI<{ id: string; amount: number; currency: string; db_order_id: number }>('/payments/create-order', {
        method: 'POST',
        headers: getAuthHeaders(),
    });
}

export async function verifyPayment(data: {
    razorpay_order_id: string;
    razorpay_payment_id: string;
    razorpay_signature: string;
}): Promise<{ status: string; order_id: number }> {
    return fetchAPI<{ status: string; order_id: number }>('/payments/verify', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
    });
}

// Mapper: DummyProduct -> PDPClient props (simulated options/variants)
export function toPDP(p: Product) {
    const images = (p.images || []).map((url) => ({ url, altText: p.title }));
    // DummyJSON lacks variants; simulate a couple for demo UX
    // Backend V1 also doesn't fully support variant logic yet (just placeholders in Seed?)
    // But we need to match the UI expectation.
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
      id: p.id,
      title: p.title,
      description: p.description,
      images,
      options,
      variants,
      tags: p.tags || [],
    };
  }
