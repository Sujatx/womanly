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
  return method.toUpperCase() === 'GET' ? 3 : 0;
}

function isRetryableStatus(status: number): boolean {
  return [408, 429, 500, 502, 503, 504].includes(status);
}

function calculateBackoff(attempt: number, baseMs = 1000, maxMs = 8000): number {
  const exponential = Math.min(baseMs * Math.pow(2, attempt), maxMs);
  const jitter = exponential * 0.1 * Math.random();
  return exponential + jitter;
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
      console.log(`[API] ${method} ${API_URL}${path} (attempt ${attempt + 1}/${retries + 1})`, options.body ? JSON.parse(options.body as string) : '');
      
      const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers,
      });

      console.log(`[API] Response ${response.status}`, response.statusText);

      if (!response.ok) {
        // Retry on retryable server errors
        if (isRetryableStatus(response.status) && attempt < retries) {
          const backoffMs = calculateBackoff(attempt);
          console.warn(`[API] Retryable error ${response.status}, retrying in ${backoffMs}ms`);
          await sleep(backoffMs);
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
      
      // Network errors - retry with backoff
      if (attempt < retries && error instanceof Error && !error.message.includes('Unauthorized')) {
        const backoffMs = calculateBackoff(attempt);
        console.warn(`[API] Network error, retrying in ${backoffMs}ms`);
        await sleep(backoffMs);
        continue;
      }
      
      // Don't retry on other errors
      throw error;
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

export async function batchFetchProducts(
  productIds: number[],
  options: { includeVariants?: boolean; includeImages?: boolean } = {}
): Promise<APIProduct[]> {
  if (productIds.length === 0) return [];
  
  try {
    const response = await apiRequest<{ products: APIProduct[]; not_found: number[] }>(
      '/batch/products',
      {
        method: 'POST',
        body: JSON.stringify({
          product_ids: productIds,
          include_variants: options.includeVariants ?? true,
          include_images: options.includeImages ?? true,
        }),
      }
    );
    return response.products;
  } catch {
    return [];
  }
}

export interface BatchAddressValidationResult {
  index: number;
  is_valid: boolean;
  errors: string[];
}

export async function batchValidateAddresses(
  addresses: Array<{
    full_name: string;
    phone: string;
    address_line1: string;
    address_line2?: string;
    city: string;
    state: string;
    postal_code: string;
    country: string;
  }>,
): Promise<BatchAddressValidationResult[]> {
  if (addresses.length === 0) return [];

  const response = await apiRequest<{ results: BatchAddressValidationResult[] }>(
    '/batch/addresses',
    {
      method: 'POST',
      body: JSON.stringify({ addresses }),
    },
  );
  return response.results;
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
