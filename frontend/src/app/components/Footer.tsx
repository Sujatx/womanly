import { Instagram, Facebook, Twitter } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-foreground text-white py-16 md:py-24">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          {/* Newsletter */}
          <div className="md:col-span-2">
            <h3 className="font-headline text-2xl mb-4">Join Our Newsletter</h3>
            <p className="text-white/70 mb-4">
              Subscribe to receive updates, access to exclusive deals, and more.
            </p>
            <form className="flex gap-2" onSubmit={(e) => e.preventDefault()}>
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-4 py-3 bg-white/10 border border-white/20 rounded-[var(--radius-sm)] focus:outline-none focus:border-accent text-white placeholder:text-white/50"
                aria-label="Email address"
              />
              <button
                type="submit"
                className="px-6 py-3 bg-accent text-white rounded-[var(--radius-sm)] hover:bg-accent/90 transition-colors"
              >
                Subscribe
              </button>
            </form>
          </div>

          {/* Shop */}
          <div>
            <h4 className="text-nav mb-4">Shop</h4>
            <ul className="space-y-3">
              <li>
                <a href="#new-arrivals" className="text-white/70 hover:text-white transition-colors">
                  New Arrivals
                </a>
              </li>
              <li>
                <a href="#collections" className="text-white/70 hover:text-white transition-colors">
                  Collections
                </a>
              </li>
              <li>
                <a href="#sale" className="text-white/70 hover:text-white transition-colors">
                  Sale
                </a>
              </li>
              <li>
                <a href="#gift-cards" className="text-white/70 hover:text-white transition-colors">
                  Gift Cards
                </a>
              </li>
            </ul>
          </div>

          {/* About */}
          <div>
            <h4 className="text-nav mb-4">About</h4>
            <ul className="space-y-3">
              <li>
                <a href="#our-story" className="text-white/70 hover:text-white transition-colors">
                  Our Story
                </a>
              </li>
              <li>
                <a href="#sustainability" className="text-white/70 hover:text-white transition-colors">
                  Sustainability
                </a>
              </li>
              <li>
                <a href="#careers" className="text-white/70 hover:text-white transition-colors">
                  Careers
                </a>
              </li>
              <li>
                <a href="#contact" className="text-white/70 hover:text-white transition-colors">
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-white/20 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-6">
            <a href="#privacy" className="text-small text-white/70 hover:text-white transition-colors">
              Privacy Policy
            </a>
            <a href="#terms" className="text-small text-white/70 hover:text-white transition-colors">
              Terms of Service
            </a>
            <a href="#shipping" className="text-small text-white/70 hover:text-white transition-colors">
              Shipping & Returns
            </a>
          </div>

          <div className="flex items-center gap-4">
            <a
              href="https://instagram.com"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 text-white/70 hover:text-white transition-colors"
              aria-label="Follow us on Instagram"
            >
              <Instagram className="w-5 h-5" />
            </a>
            <a
              href="https://facebook.com"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 text-white/70 hover:text-white transition-colors"
              aria-label="Follow us on Facebook"
            >
              <Facebook className="w-5 h-5" />
            </a>
            <a
              href="https://twitter.com"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 text-white/70 hover:text-white transition-colors"
              aria-label="Follow us on Twitter"
            >
              <Twitter className="w-5 h-5" />
            </a>
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
