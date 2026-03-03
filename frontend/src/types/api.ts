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
  is_available: boolean;
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
  items: T[];
  total: number;
  page: number;
  size: number;
}
