# Womanly Frontend

Next.js 15 application for the Womanly e-commerce store.

## Features
*   **App Router:** Utilizing the latest Next.js features.
*   **Client Components:** Interactive Cart, Wishlist, and Checkout drawers.
*   **State Management:** React Context for Auth, Custom Hooks for Cart.
*   **Styling:** CSS Modules with global variables.

## Development
```bash
npm install
npm run dev
```

## Environment Variables
Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_razorpay_key_id
```