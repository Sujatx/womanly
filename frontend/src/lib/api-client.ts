import {
  APICouponValidation,
  APIOrder,
  APIProduct,
  APIPagedResult,
  APIShippingEstimate,
  APITaxEstimate,
  APIWishlist,
  PaginatedResponse,
  ShippingAddressInput,
  ShippingCartItemInput,
} from '../types/api';

const RAW_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = RAW_API_URL.endsWith('/api/v1') ? RAW_API_URL : `${RAW_API_URL}/api/v1`;

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

function getRetryCount(method: string): number {
  return method.toUpperCase() === 'GET' ? 3 : 1;
}

export function getAuthToken(): string | null {
  const token = localStorage.getItem('auth_token');
  console.log('[Auth] Getting token from localStorage:', token ? `${token.substring(0, 20)}...` : 'null');
  return token;
}

async function toErrorMessage(response: Response): Promise<string> {
  let detail = response.statusText;
  try {
    const data = await response.json();
    if (data.detail) {
      detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
    }
  } catch {
    // Ignore JSON parse errors
  }
  return `${detail}`;
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const method = options.method || 'GET';
  const retries = getRetryCount(method);

  const headers = new Headers(options.headers);
  headers.set('Accept', 'application/json');

  const token = getAuthToken();
  if (token && !headers.has('Authorization')) {
    console.log('[API] Adding Authorization header');
    headers.set('Authorization', `Bearer ${token}`);
  } else if (!token) {
    console.log('[API] No token available');
  }

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  let lastError: unknown;

  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      console.log(`[API] ${method} ${API_URL}${path}`, options.body ? JSON.parse(options.body as string) : '');
      
      const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers,
      });

      console.log(`[API] Response ${response.status}`, response.statusText);

      if (!response.ok) {
        if (response.status >= 500 && attempt < retries) {
          await sleep(1000 * 2 ** attempt);
          continue;
        }
        
        // Handle 401 Unauthorized - invalid/expired token
        if (response.status === 401) {
          const errorMsg = await toErrorMessage(response);
          console.warn('[API] 401 Unauthorized:', errorMsg);
          
          // Check if this is a token issue
          if (errorMsg.includes('Could not validate credentials') || errorMsg.includes('token')) {
            console.warn('[API] Token expired/invalid - clearing auth');
            localStorage.removeItem('auth_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            
            // Only redirect if not already on auth page
            if (!window.location.hash.includes('#/auth')) {
              window.location.hash = '#/auth';
            }
          }
          throw new Error(errorMsg);
        }
        
        const errorMsg = await toErrorMessage(response);
        console.error(`[API] Error:`, errorMsg);
        throw new Error(errorMsg);
      }

      if (response.status === 204) {
        return null as T;
      }

      const data = await response.json();
      console.log(`[API] Success:`, data);
      return data as T;
    } catch (error) {
      console.error(`[API] Request failed:`, error);
      lastError = error;
      if (attempt < retries) {
        await sleep(1000 * 2 ** attempt);
      }
    }
  }

  throw lastError instanceof Error ? lastError : new Error('Request failed');
}

function normalizePagedProducts(payload: PaginatedResponse<APIProduct>): APIPagedResult<APIProduct> {
  return {
    items: payload.data,
    total: payload.pagination.total,
    skip: payload.pagination.skip,
    limit: payload.pagination.limit,
    hasMore: payload.pagination.has_more,
  };
}

export async function fetchProducts(page = 1, limit = 20): Promise<APIProduct[]> {
  const skip = (page - 1) * limit;
  const result = await fetchProductList({ skip, limit });
  return result.items;
}

export async function fetchProductList(params: {
  skip?: number;
  limit?: number;
  category?: string;
  q?: string;
  inStock?: boolean;
} = {}): Promise<APIPagedResult<APIProduct>> {
  const query = new URLSearchParams();
  query.set('skip', String(params.skip ?? 0));
  query.set('limit', String(params.limit ?? 20));
  if (params.category) query.set('category', params.category);
  if (params.q) query.set('q', params.q);
  if (params.inStock !== undefined) query.set('in_stock', String(params.inStock));

  const data = await apiRequest<PaginatedResponse<APIProduct>>(`/products?${query.toString()}`);
  return normalizePagedProducts(data);
}

export async function searchProducts(queryText: string, limit = 20): Promise<APIPagedResult<APIProduct>> {
  const query = new URLSearchParams({ q: queryText, skip: '0', limit: String(limit) });
  const data = await apiRequest<PaginatedResponse<APIProduct>>(`/products/search?${query.toString()}`);
  return normalizePagedProducts(data);
}

export async function fetchProduct(id: string): Promise<APIProduct | null> {
  try {
    return await apiRequest<APIProduct>(`/products/${id}`);
  } catch {
    return null;
  }
}

export async function fetchWishlist(): Promise<APIWishlist | null> {
  try {
    return await apiRequest<APIWishlist>('/wishlist/');
  } catch {
    return null;
  }
}

export async function addToWishlist(productId: number): Promise<APIWishlist> {
  return await apiRequest<APIWishlist>('/wishlist/', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId }),
  });
}

export async function removeFromWishlist(productId: number): Promise<APIWishlist> {
  return await apiRequest<APIWishlist>(`/wishlist/${productId}`, {
    method: 'DELETE',
  });
}

export async function fetchMyOrders(): Promise<APIOrder[]> {
  try {
    return await apiRequest<APIOrder[]>('/payments/orders/me');
  } catch {
    return [];
  }
}

export async function fetchShippingEstimate(address: ShippingAddressInput, items: ShippingCartItemInput[]): Promise<APIShippingEstimate | null> {
  try {
    return await apiRequest<APIShippingEstimate>('/shipping/calculate', {
      method: 'POST',
      body: JSON.stringify({ address, items }),
    });
  } catch {
    return null;
  }
}

export async function fetchTaxEstimate(
  address: ShippingAddressInput,
  items: ShippingCartItemInput[],
  subtotal: number,
): Promise<APITaxEstimate | null> {
  try {
    return await apiRequest<APITaxEstimate>('/tax/calculate', {
      method: 'POST',
      body: JSON.stringify({ address, items, subtotal }),
    });
  } catch {
    return null;
  }
}

export async function validateCoupon(code: string, orderTotal: number): Promise<APICouponValidation | null> {
  try {
    const query = new URLSearchParams({ order_total: String(orderTotal) });
    return await apiRequest<APICouponValidation>(`/discounts/coupons/validate/${encodeURIComponent(code)}?${query.toString()}`);
  } catch {
    return null;
  }
}
