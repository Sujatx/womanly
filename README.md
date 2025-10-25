

```markdown
# Womanly 🛍️

A modern, high-performance fashion e-commerce platform built with Next.js 15, featuring real-time cart/wishlist sync, inline search, and optimized product pages.

## 🚀 Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: CSS Modules + inline styles
- **Data Source**: DummyJSON API (mock e-commerce data)
- **State Management**: React hooks + localStorage + cross-tab events
- **Image Optimization**: next/image with remote patterns
- **Payments**: Stripe & Shopify integrations (ready for future implementation)

## 📁 Project Structure

```
womanly/
├── app/                        # Next.js App Router
│   ├── layout.tsx              # Root layout: header, footer, global shell
│   ├── page.tsx                # Homepage: hero + categories + featured products
│   ├── globals.css             # Global styles and CSS resets
│   ├── not-found.tsx           # Custom 404 page
│   ├── collections/[handle]/   # Product listing pages (PLP)
│   │   ├── page.tsx            # Server component entry
│   │   ├── plp-client.tsx      # Client filters, sorting, grid
│   │   └── loading.tsx         # Loading skeleton
│   ├── products/[handle]/      # Product detail pages (PDP)
│   │   ├── page.tsx            # Server entry
│   │   └── loading.tsx         # Loading state
│   └── api/checkout/           # Server API routes
│       ├── shopify/route.ts    # Shopify checkout endpoint
│       └── stripe/route.ts     # Stripe payment endpoint
├── components/                 # Reusable UI components
│   ├── HeaderCart.tsx          # Cart icon + drawer trigger
│   ├── HeaderSearch.tsx        # Inline search with live suggestions
│   ├── HeaderWishlist.tsx      # Wishlist icon + drawer
│   ├── CartDrawer.tsx          # Sliding cart panel
│   ├── ProductCard.tsx         # Product grid card with wishlist heart
│   ├── PDPClient.tsx           # PDP orchestrator: variants, add-to-cart
│   ├── PDPGallery.tsx          # Vertical thumbnails + main image
│   ├── VariantSelector.tsx     # Size/color option buttons
│   ├── SizeGuideModal.tsx      # Size chart modal
│   ├── DeliveryReturns.tsx     # Reassurance block
│   ├── CheckoutButtons.tsx     # Buy Now action
│   ├── SimilarProducts.tsx     # Sidebar product recommendations
│   ├── PLPFilters.tsx          # Category/price filters
│   └── Button.tsx              # Shared button component
├── lib/                        # Business logic and utilities
│   ├── cart.ts                 # Cart hook: add, remove, sync, persist
│   ├── wishlist.ts             # Wishlist hook with localStorage
│   ├── dummyjson.ts            # DummyJSON API client
│   ├── plp-transform.ts        # PLP data transformers
│   ├── shopify.ts              # Shopify SDK helpers (future)
│   └── stripe.ts               # Stripe SDK helpers (future)
├── types/
│   └── product.ts              # TypeScript interfaces
├── public/
│   └── favicon.ico             # Site favicon
├── next.config.js              # Next.js configuration
├── tsconfig.json               # TypeScript config
├── package.json                # Dependencies and scripts
└── .env.local                  # Environment variables (not in repo)
```

## ✨ Key Features

### 🛒 Cart System
- **Persistent storage**: Cart data saved to localStorage (`cart_v1`)
- **Cross-tab sync**: Changes sync instantly across browser tabs via storage events
- **Real-time updates**: Custom `cart:update` event keeps all components in sync
- **Auto-open drawer**: Adding items triggers `cart:open` event for instant feedback
- **Quantity controls**: Increment/decrement per line item
- **Implementation**: `lib/cart.ts` + `components/CartDrawer.tsx`

### ❤️ Wishlist System
- **Toggle on/off**: Heart button on every ProductCard
- **Persistent**: Saved to localStorage (`wishlist_v1`)
- **Cross-tab sync**: Same storage event pattern as cart
- **Drawer UI**: Slide-in panel showing saved products
- **Implementation**: `lib/wishlist.ts` + `components/HeaderWishlist.tsx`

### 🔍 Inline Search
- **Live suggestions**: Debounced fetch to DummyJSON search API (200ms delay)
- **Keyboard navigation**: Arrow keys, Enter to open, Escape to close
- **ARIA compliant**: role="combobox", proper focus management
- **No separate page**: Integrated directly into header for speed
- **Hover support**: Mouse users can hover suggestions to preview
- **Implementation**: `components/HeaderSearch.tsx`

### 🖼️ Product Detail Page (PDP)
- **Two-column layout**: Gallery left, details/actions right (single column on mobile)
- **Vertical thumbnails**: Left rail with hover/focus to swap main image
- **Fixed-ratio main image**: 4:5 aspect box with next/image fill eliminates bottom gaps
- **Variant selection**: Size/Color buttons with disabled states for unavailable combos
- **Add to cart**: Inline feedback ("Added") + drawer auto-open
- **Size guide modal**: Category-specific size charts
- **Similar products**: Sidebar fetches by category with fallback to generic products
- **Implementation**: `components/PDPClient.tsx` + `components/PDPGallery.tsx`

### 🖼️ Image Optimization
- **next/image**: Automatic optimization, lazy loading, WebP format
- **Responsive sizing**: `sizes` prop delivers correct image resolution per viewport
- **Remote patterns**: DummyJSON domains whitelisted in `next.config.js`
- **No CLS**: width/height or fill prevents layout shift during load

### 📦 Product Listing Page (PLP)
- **Server + client hybrid**: Initial data server-rendered for SEO
- **Filters**: Category, price range (client-side state)
- **Sorting**: Price, name, newest (updates grid instantly)
- **Grid layout**: Responsive cards with hover effects
- **Implementation**: `app/collections/[handle]/plp-client.tsx`

## 🛠️ Setup Instructions

### Prerequisites
- **Node.js**: 18.17 or higher
- **npm**: 9.6 or higher (or use pnpm/yarn)

### Installation

1. **Clone the repository**
   ```
   git clone https://github.com/yourusername/womanly.git
   cd womanly
   ```

2. **Install dependencies**
   ```
   npm install
   ```

3. **Configure environment variables**
   Create `.env.local` in the project root:
   ```
   # Optional: Add when ready to implement payments
   # STRIPE_SECRET_KEY=sk_test_...
   # SHOPIFY_STOREFRONT_TOKEN=...
   # SHOPIFY_STORE_DOMAIN=yourstore.myshopify.com
   ```

4. **Run development server**
   ```
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) in your browser.

5. **Build for production**
   ```
   npm run build
   npm start
   ```

## ⚙️ Configuration

### Image Domains (Required)
`next.config.js` must include DummyJSON image hosts:
```
module.exports = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'cdn.dummyjson.com', pathname: '/**' },
      { protocol: 'https', hostname: 'i.dummyjson.com', pathname: '/**' },
      { protocol: 'https', hostname: 'dummyjson.com', pathname: '/**' },
    ],
  },
};
```
**Why?** Next.js blocks external images by default for security. This whitelists DummyJSON.

**Important**: Restart dev server after changing `next.config.js`.

### TypeScript
- Strict mode enabled in `tsconfig.json`
- Type definitions: `types/product.ts`
- Next.js types auto-generated in `next-env.d.ts`

## 🏗️ Architecture Decisions

### Why App Router?
- **Server Components**: Faster initial page loads, better SEO
- **File-based routing**: Intuitive structure, automatic code splitting
- **Streaming**: Progressive rendering with loading.tsx boundaries
- **Modern**: Next.js 13+ recommended pattern

### Why localStorage for Cart/Wishlist?
- **No backend required**: Instant MVP without DB/auth
- **Fast**: Zero latency for reads/writes
- **Cross-tab sync**: Storage events keep multiple tabs in sync
- **Easy migration**: Can swap for API calls later without changing hook interfaces

### Why Custom Events?
- **Decoupling**: Components don't need direct refs to each other
- **Async-safe**: `setTimeout(() => dispatchEvent(...), 0)` prevents "Cannot update component while rendering" React errors
- **Flexible**: Any component can listen to `cart:update`, `cart:open`, `wishlist:update`

### Why DummyJSON?
- **Free mock API**: No signup, rate limits generous for dev
- **Realistic data**: Products with variants, images, categories
- **Easy swap**: Replace fetch calls in `lib/dummyjson.ts` to switch to real backend

## 📊 Data Flow Examples

### Adding to Cart
1. User clicks "Add to cart" in `PDPClient`
2. `add()` from `useCart` hook → updates React state
3. Writes to `localStorage` under `cart_v1` key
4. `writeCart()` dispatches `cart:update` custom event (async)
5. All mounted `useCart` instances listen and re-sync
6. `HeaderCart` count updates, drawer can open via `cart:open` event

### Search Flow
1. User types in `HeaderSearch` input
2. Debounced (200ms) fetch to `https://dummyjson.com/products/search?q=term`
3. Results render in dropdown listbox
4. Arrow keys navigate (keyboard), hover works (mouse)
5. Enter/click → `router.push(/products/{id})`
6. Dropdown closes on blur or Escape

### Variant Selection on PDP
1. User clicks Size "M" in `VariantSelector`
2. `onChange` updates `selected` state in `PDPClient`
3. `activeVariant` recomputed (useMemo): finds variant matching all selected options
4. Price, image, add-to-cart ID reflect active variant
5. Disabled values computed: checks which size/color combos have no available variants

## 🔌 API Routes (Future)

- **`/api/checkout/shopify/route.ts`**: Placeholder for Shopify Storefront API checkout
- **`/api/checkout/stripe/route.ts`**: Placeholder for Stripe Payment Intent creation
- **Status**: Endpoints exist but return placeholders; gate with env flags before going live

## 🎨 Styling Approach

- **Inline styles**: Component-specific layout (display: grid, flexbox, spacing)
- **globals.css**: Shared base styles, resets, utility classes (`.muted`, `.rounded`, `.container`)
- **CSS-in-JS** (styled-jsx): Media queries for responsive grids (e.g., PDPClient desktop layout)
- **No UI library**: Custom components for full control and minimal bundle size

## 🚧 Known Issues & TODOs

### Current Bugs (Fixed)
- ✅ "Cannot update component while rendering" → fixed with `setTimeout(() => dispatchEvent(...), 0)`
- ✅ "e.currentTarget is null" in search blur → fixed by using stable `rootRef.current`
- ✅ "Invalid src prop" for DummyJSON images → fixed by adding `remotePatterns`

### Roadmap
- [ ] Implement real checkout with Stripe/Shopify
- [ ] Add product reviews (DummyJSON has review data)
- [ ] SEO: metadata per route, Open Graph images, structured data
- [ ] Analytics: track add-to-cart, wishlist, search queries
- [ ] Mobile improvements: sticky add-to-cart bar, touch-friendly thumbnails
- [ ] Error boundaries for graceful error handling
- [ ] Loading skeletons for better perceived performance
- [ ] A11y audit: screen reader testing, ARIA labels verification

## 📝 Common Tweaks

| What to Change | Where | Example |
|----------------|-------|---------|
| Header height | PDPClient sticky top | Change `top: 96px` to match your header |
| Gallery width | PDPClient left column | Adjust `maxWidth: 680` for wider/narrower |
| Main image ratio | PDPGallery aspect | Change `aspectRatio: '4 / 5'` for different proportions |
| Similar products count | SimilarProducts | Pass `limit={12}` for more items |
| Cart/Wishlist icons | HeaderCart/HeaderWishlist | Swap SVG/emoji for custom icons |

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - feel free to use this project for learning or commercial purposes.

## 🙏 Acknowledgments

- **DummyJSON** for free mock e-commerce API
- **Next.js team** for App Router and image optimization
- **Vercel** for seamless deployment platform

---

**Built with ❤️ using Next.js 15 and TypeScript**
```

Copy this entire markdown block into a README.md file at your project root, commit it, and push to GitHub—it's ready to onboard contributors and serve as comprehensive documentation.[1]

[1](https://nextjs.org/docs/app/api-reference/config/next-config-js)