import { Instagram, Facebook, Twitter } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-foreground text-white py-8 md:py-10 lg:py-12">
      <div className="container mx-auto px-4 sm:px-6">
        {/* Newsletter Banner - Full Width */}
        <div className="bg-white/5 border border-white/10 rounded-[var(--radius-lg)] p-4 sm:p-6 mb-6">
          <div className="max-w-2xl">
            <h3 className="font-headline text-lg sm:text-xl mb-2">Join Our Newsletter</h3>
            <p className="text-white/70 mb-3 text-sm sm:text-base">
              Subscribe for updates and exclusive deals.
            </p>
            <form className="flex flex-col sm:flex-row gap-2" onSubmit={(e) => e.preventDefault()}>
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-[var(--radius-sm)] focus:outline-none focus:border-accent text-white placeholder:text-white/50 text-sm"
                aria-label="Email address"
              />
              <button
                type="submit"
                className="px-6 py-2 bg-accent text-white rounded-[var(--radius-sm)] hover:bg-accent/90 transition-colors whitespace-nowrap touch-activation text-sm"
              >
                Subscribe
              </button>
            </form>
          </div>
        </div>

        {/* Main Footer Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-6">

          {/* Shop */}
          <div>
            <h4 className="text-nav mb-2 text-xs sm:text-sm font-semibold">Shop</h4>
            <ul className="space-y-1.5">
              <li>
                <a href="#/shop" className="text-white/70 hover:text-white transition-colors text-xs sm:text-sm">
                  New Arrivals
                </a>
              </li>
              <li>
                <a href="#/shop" className="text-white/70 hover:text-white transition-colors text-xs sm:text-sm">
                  Collections
                </a>
              </li>
              <li>
                <a href="#/shop" className="text-white/70 hover:text-white transition-colors text-xs sm:text-sm">
                  Sale
                </a>
              </li>
              <li>
                <a href="#/checkout" className="text-white/70 hover:text-white transition-colors text-xs sm:text-sm">
                  Checkout
                </a>
              </li>
            </ul>
          </div>

          {/* About */}
          <div>
            <h4 className="text-nav mb-2 text-xs sm:text-sm font-semibold">About</h4>
            <ul className="space-y-1.5">
              <li>
                <a href="#/about" className="text-white/70 hover:text-white transition-colors text-xs sm:text-sm">
                  Our Story
                </a>
              </li>
              <li>
                <a href="#/about" className="text-white/70 hover:text-white transition-colors text-xs sm:text-sm">
                  Sustainability
                </a>
              </li>
              <li>
                <span className="text-white/40 text-xs sm:text-sm">Careers</span>
              </li>
              <li>
                <span className="text-white/40 text-xs sm:text-sm">Contact</span>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h4 className="text-nav mb-2 text-xs sm:text-sm font-semibold">Support</h4>
            <ul className="space-y-1.5">
              <li>
                <a href="#/checkout" className="text-white/70 hover:text-white transition-colors text-xs sm:text-sm">
                  Shipping Info
                </a>
              </li>
              <li>
                <a href="#/checkout" className="text-white/70 hover:text-white transition-colors text-xs sm:text-sm">
                  Returns
                </a>
              </li>
              <li>
                <a href="#/orders" className="text-white/70 hover:text-white transition-colors text-xs sm:text-sm">
                  Track Order
                </a>
              </li>
              <li>
                <span className="text-white/40 text-xs sm:text-sm">Help Center</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-4 border-t border-white/20">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6 text-center sm:text-left">
              <span className="text-xs sm:text-small text-white/50">© {new Date().getFullYear()} Womanly</span>
              <div className="hidden sm:flex items-center gap-3 sm:gap-4">
                <a href="#" className="text-xs sm:text-small text-white/40 hover:text-white/60 transition-colors">
                  Privacy
                </a>
                <a href="#" className="text-xs sm:text-small text-white/40 hover:text-white/60 transition-colors">
                  Terms
                </a>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <a
                href="https://instagram.com"
                target="_blank"
                rel="noopener noreferrer"
                className="p-1.5 text-white/60 hover:text-white transition-colors"
                aria-label="Follow us on Instagram"
              >
                <Instagram className="w-4 h-4" />
              </a>
              <a
                href="https://facebook.com"
                target="_blank"
                rel="noopener noreferrer"
                className="p-1.5 text-white/60 hover:text-white transition-colors"
                aria-label="Follow us on Facebook"
              >
                <Facebook className="w-4 h-4" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="p-1.5 text-white/60 hover:text-white transition-colors"
                aria-label="Follow us on Twitter"
              >
                <Twitter className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>

        <div className="text-center mt-8">
          <p className="text-small text-white/50">
            © {new Date().getFullYear()} Womanly. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
