const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export type ProductVariant = {
  id: number;
  sku: string;
  size?: string;
  color?: string;
  material?: string;
  price_adjustment: number;
  stock_quantity: number;
  is_available: boolean;
};

export type ProductImage = {
  id: number;
  image_url: string;
  alt_text?: string;
  display_order: number;
  is_primary: boolean;
};

export type Product = {
  id: number;
  title: string;
  description: string;
  price: number;
  brand?: string;
  thumbnail?: string;
  category_slug?: string;
  variants: ProductVariant[];
  product_images: ProductImage[];
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
    const primaryImg = p.product_images?.find(img => img.is_primary) || p.product_images?.[0];
    const image = primaryImg ? { url: primaryImg.image_url, altText: p.title } : { url: p.thumbnail || '', altText: p.title };
    
    const secondaryImg = p.product_images?.find(img => !img.is_primary) || p.product_images?.[1];
    
    // Calculate total stock for inventory badges
    const totalStock = p.variants?.reduce((acc, v) => acc + v.stock_quantity, 0) || 0;
    const isAvailable = p.variants?.some(v => v.is_available && v.stock_quantity > 0) ?? true;

    return {
      handle: String(p.id),
      title: p.title,
      image,
      hoverImage: secondaryImg ? { url: secondaryImg.image_url, altText: p.title } : undefined,
      price: { amount: String(p.price), currencyCode: 'USD' },
      totalStock,
      isOutOfStock: !isAvailable || totalStock === 0
    };
}

// Cart Types
export type CartItem = {
    id: number;
    variant_id: number;
    quantity: number;
    selected_options?: string;
    variant?: ProductVariant & { product?: Product };
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

export async function addToCart(variant_id: number, quantity: number, selected_options?: string): Promise<Cart> {
    return fetchAPI<Cart>('/cart/items', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ variant_id, quantity, selected_options }),
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

export function toPDP(p: Product) {
    const images = (p.product_images || []).map((img) => ({ url: img.image_url, altText: img.alt_text || p.title }));
    if (images.length === 0 && p.thumbnail) {
        images.push({ url: p.thumbnail, altText: p.title });
    }

    const sizes = Array.from(new Set(p.variants?.map(v => v.size).filter(Boolean)));
    const colors = Array.from(new Set(p.variants?.map(v => v.color).filter(Boolean)));

    const options = [];
    if (sizes.length > 0) options.push({ name: 'Size', values: sizes });
    if (colors.length > 0) options.push({ name: 'Color', values: colors });

    const variants = (p.variants || []).map(v => ({
        id: String(v.id),
        title: `${v.size || ''} / ${v.color || ''}`,
        availableForSale: v.is_available && v.stock_quantity > 0,
        stockQuantity: v.stock_quantity,
        price: { amount: String(p.price + v.price_adjustment), currencyCode: 'USD' },
        selectedOptions: [
            ...(v.size ? [{ name: 'Size', value: v.size }] : []),
            ...(v.color ? [{ name: 'Color', value: v.color }] : []),
        ]
    }));
  
    return {
      id: p.id,
      title: p.title,
      description: p.description,
      images,
      options,
      variants,
      tags: [],
    };
}
