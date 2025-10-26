[README.md](https://github.com/user-attachments/files/23151182/README.md)
# Womanly 🛍️

Modern e-commerce platform built with Next.js 15, TypeScript, and DummyJSON API.

**Live:** [womanly-beryl.vercel.app](https://womanly-beryl.vercel.app/)

## Tech Stack

- Next.js 15 (App Router), TypeScript
- CSS Modules, localStorage sync
- DummyJSON API (mock data)

## Features

- **Cart & Wishlist:** Persistent, cross-tab sync
- **Inline Search:** Debounced live suggestions
- **Product Pages:** Variant selection, image gallery, similar products
- **Listing Pages:** Filters, sorting, responsive grid

## Setup

```bash
git clone https://github.com/yourusername/womanly.git
cd womanly
npm install
npm run dev
```

Open [localhost:3000](http://localhost:3000)

## Configuration

Add to `next.config.js`:

```js
module.exports = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'cdn.dummyjson.com', pathname: '/**' },
      { protocol: 'https', hostname: 'i.dummyjson.com', pathname: '/**' },
    ],
  },
};
```

Restart dev server after changes.

## Structure

```
app/
├── layout.tsx           # Global shell
├── page.tsx             # Homepage
├── collections/[handle] # Product listings
└── products/[handle]    # Product details
components/              # UI components
lib/                     # Hooks, API clients
```

## Roadmap

- [ ] Real checkout (Stripe/Shopify)
- [ ] SEO metadata
- [ ] Analytics integration
- [ ] Mobile improvements

## License

MIT- free for personal, learning, commercial use.

---

Built by Sujat
