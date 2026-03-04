import { APIProduct, PaginatedResponse } from '../types/api';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchProducts(page = 1, limit = 20): Promise<APIProduct[]> {
  try {
    const skip = (page - 1) * limit;
    const response = await fetch(`${API_URL}/products?skip=${skip}&limit=${limit}`);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    const data = await response.json();
    // Support both paginated and direct list responses for flexibility
    return Array.isArray(data) ? data : data.items || [];
  } catch (error) {
    console.error('Failed to fetch products:', error);
    return [];
  }
}

export async function fetchProduct(id: string): Promise<APIProduct | null> {
  try {
    const response = await fetch(`${API_URL}/products/${id}`);
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch product ${id}:`, error);
    return null;
  }
}
