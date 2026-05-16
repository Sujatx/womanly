import type { APIProduct } from '../types/api';
import type { Product } from '../app/data/products';

export function transformProduct(apiProduct: APIProduct): Product {
  // Extract unique sizes and colors from variants
  const sizes = Array.from(new Set(
    apiProduct.variants
      .map(v => v.size)
      .filter((s): s is string => s !== null)
  )).sort();

  const colors = Array.from(new Set(
    apiProduct.variants
      .map(v => v.color)
      .filter((c): c is string => c !== null)
  )).sort();

  // Determine stock status
  const totalStock = apiProduct.variants.reduce((sum, v) => sum + v.stock_quantity, 0);
  const inStock = totalStock > 0;

  const variantOptions = apiProduct.variants.map((variant) => ({
    id: variant.id,
    size: variant.size || '',
    color: variant.color || '',
    priceAdjustment: variant.price_adjustment,
    stockQuantity: variant.stock_quantity,
    availableStock: variant.available_stock ?? variant.stock_quantity,
    isAvailable: variant.is_available,
  }));

  // Process images: sort by display_order, prioritize primary
  const sortedImages = [...apiProduct.product_images].sort((a, b) => {
    if (a.is_primary && !b.is_primary) return -1;
    if (!a.is_primary && b.is_primary) return 1;
    return a.display_order - b.display_order;
  });

  const images = sortedImages.map(img => img.image_url);
  // Add thumbnail if available and not already in images
  if (apiProduct.thumbnail && !images.includes(apiProduct.thumbnail)) {
    images.unshift(apiProduct.thumbnail);
  }

  // Determine badge based on simple heuristics (can be enhanced later)
  let badge: Product['badge'] = undefined;
  if (apiProduct.category_slug === 'new-arrivals') {
    badge = 'new';
  } else if (apiProduct.price < 100) { // Example logic
    badge = 'sale';
  }

  return {
    id: apiProduct.id.toString(),
    name: apiProduct.title,
    collection: apiProduct.category_slug // Fallback, ideally fetch category name
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' '), 
    price: apiProduct.price,
    description: apiProduct.description,
    images: images.length > 0 ? images : ['https://via.placeholder.com/800x1000?text=No+Image'],
    sizes,
    colors,
    inStock,
    badge,
    variants: variantOptions,
  };
}
