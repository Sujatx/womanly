// lib/shopify.ts
// Minimal Storefront API client + common queries + cartCreate helper.
// Uses the public Storefront token and versioned endpoint.
// Docs: Storefront API, collections query, and Cart -> checkoutUrl pattern.

const domain = process.env.NEXT_PUBLIC_SHOPIFY_STORE_DOMAIN!;
const token = process.env.SHOPIFY_STOREFRONT_ACCESS_TOKEN!;
const apiVersion = process.env.SHOPIFY_STOREFRONT_API_VERSION || '2025-10';

type GQLArgs = { query: string; variables?: Record<string, any> };

// Server-friendly fetch wrapper for GraphQL queries (catalog reads, etc.)
export async function storefront<T>({ query, variables }: GQLArgs): Promise<T> {
  const res = await fetch(`https://${domain}/api/${apiVersion}/graphql.json`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Storefront-Access-Token': token,
    },
    body: JSON.stringify({ query, variables }),
    next: { revalidate: 60 },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Storefront API error: ${res.status} ${text}`);
  }
  const json = await res.json();
  if (json.errors) throw new Error(JSON.stringify(json.errors));
  return json.data as T;
}

/* =========================
   Queries
   ========================= */

// Collections list for homepage tiles (id, handle, title, image)
export const GET_COLLECTIONS = `
  query Collections($first:Int=8){
    collections(first:$first){
      edges{
        node{
          id
          handle
          title
          image{ url altText }
        }
      }
    }
  }
`;

// Collection page products (PLP)
export const GET_COLLECTION_PRODUCTS = `
  query CollectionProducts($handle:String!, $first:Int=24){
    collectionByHandle(handle:$handle){
      id
      title
      handle
      products(first:$first){
        edges{
          node{
            id
            handle
            title
            featuredImage{ url altText }
            priceRange{ minVariantPrice{ amount currencyCode } }
          }
        }
      }
    }
  }
`;

// Product detail (PDP)
export const GET_PRODUCT = `
  query Product($handle:String!){
    product(handle:$handle){
      id
      handle
      title
      description
      images(first:10){ edges{ node{ url altText } } }
      variants(first:50){
        edges{
          node{
            id
            title
            availableForSale
            selectedOptions{ name value }
            price{ amount currencyCode }
          }
        }
      }
      options{ name values }
      tags
    }
  }
`;

/* =========================
   Mutations
   ========================= */

// Cart creation returns a checkoutUrl for secure hosted checkout handoff
const CART_CREATE = `
  mutation CartCreate($lines:[CartLineInput!]!){
    cartCreate(input:{ lines:$lines }){
      cart{ id checkoutUrl }
      userErrors{ field message }
    }
  }
`;

/* =========================
   Helpers
   ========================= */

// Server-only: create a Cart and return checkoutUrl (call at click time)
export async function createCartAndGetCheckoutUrl(
  lines: Array<{ merchandiseId: string; quantity: number }>
) {
  const res = await fetch(`https://${domain}/api/${apiVersion}/graphql.json`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Storefront-Access-Token': token,
    },
    body: JSON.stringify({ query: CART_CREATE, variables: { lines } }),
    cache: 'no-store',
  });

  const json = await res.json();
  const errs = json?.data?.cartCreate?.userErrors;
  if (errs?.length) throw new Error(errs.map((e: any) => e.message).join(', '));

  const url = json?.data?.cartCreate?.cart?.checkoutUrl as string | undefined;
  if (!url) throw new Error('Missing checkoutUrl');
  return url;
}
