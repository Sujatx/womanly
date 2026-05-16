export interface APIProductImage {
  id: number;
  product_id: number;
  image_url: string;
  alt_text: string | null;
  display_order: number;
  is_primary: boolean;
}

export interface APIProductVariant {
  id: number;
  product_id: number;
  sku: string;
  size: string | null;
  color: string | null;
  material: string | null;
  price_adjustment: number;
  stock_quantity: number;
  available_stock?: number;
  is_available: boolean;
  estimated_total?: number;
}

export interface APIProduct {
  id: number;
  title: string;
  description: string;
  price: number;
  brand: string | null;
  thumbnail: string | null;
  category_slug: string;
  category_id: number | null;
  variants: APIProductVariant[];
  product_images: APIProductImage[];
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    total: number;
    skip: number;
    limit: number;
    has_more: boolean;
  };
}

export interface APIPagedResult<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  hasMore: boolean;
}

export interface APIWishlistItem {
  id: number;
  product_id: number;
  title: string | null;
  thumbnail: string | null;
  price: number | null;
}

export interface APIWishlist {
  id: number;
  items: APIWishlistItem[];
  count: number;
}

export interface CheckoutItemInput {
  variant_id: number;
  quantity: number;
}

export interface APIOrder {
  id: number;
  status: string;
  total_amount: number;
  created_at: string;
  tracking_number?: string | null;
  shipping_provider?: string | null;
}

export interface ShippingAddressInput {
  country: string;
  state?: string;
  postal_code?: string;
}

export interface ShippingCartItemInput {
  product_id: number;
  quantity: number;
  category_slug?: string;
}

export interface APIShippingEstimate {
  cost: number;
  delivery_days: number;
  provider: string;
}

export interface APITaxBreakdownItem {
  category?: string;
  rate: number;
  amount: number;
  description?: string;
}

export interface APITaxEstimate {
  tax_amount: number;
  effective_rate: number;
  breakdown: APITaxBreakdownItem[];
}

export interface APICouponValidation {
  valid: boolean;
  discount_type?: string;
  discount_amount?: number;
  discount_value?: number;
  message: string;
}
