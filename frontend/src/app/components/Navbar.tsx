import { useState, useEffect } from 'react';
import { Search, Heart, ShoppingBag, User, Menu, X } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { motion, AnimatePresence } from 'motion/react';

interface NavbarProps {
  onSearchOpen: () => void;
  onCartOpen: () => void;
  cartItemCount: number;
}

export function Navbar({ onSearchOpen, onCartOpen, cartItemCount }: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isAuthenticated } = useAuth();

  // Lock body scroll when menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileMenuOpen]);

  return (
    <header className="sticky top-0 surface-panel border-b border-border z-[var(--z-header)]">
      <nav className="container mx-auto" aria-label="Main navigation">
        {/* Desktop & Tablet */}
        <div className="hidden md:flex items-center justify-between h-20 px-6">
          {/* Left: Navigation Links */}
          <div className="flex items-center gap-8">
            <a 
              href="#/shop" 
              className="text-nav text-foreground hover:text-accent transition-colors duration-[var(--motion-micro)]"
            >
              Shop
            </a>
            <a 
              href="#/wishlist" 
              className="text-nav text-foreground hover:text-accent transition-colors duration-[var(--motion-micro)]"
            >
              Wishlist
            </a>
            <a 
              href="#/orders" 
              className="text-nav text-foreground hover:text-accent transition-colors duration-[var(--motion-micro)]"
            >
              Orders
            </a>
          </div>

          {/* Center: Brand */}
          <div className="absolute left-1/2 -translate-x-1/2">
            <a 
              href="#/" 
              className="flex h-12 w-32 items-center justify-center md:h-16 md:w-40"
              aria-label="Womanly Home"
            >
              <img src="/LOGO.png" alt="Womanly" className="max-h-full max-w-full object-contain" />
            </a>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-6">
            <button
              onClick={onSearchOpen}
              className="p-2 text-foreground hover:text-accent transition-colors duration-[var(--motion-micro)]"
              aria-label="Search"
            >
              <Search className="w-5 h-5" />
            </button>
            <a
              href="#/wishlist"
              className="p-2 text-foreground hover:text-accent transition-colors duration-[var(--motion-micro)]"
              aria-label="Wishlist"
            >
              <Heart className="w-5 h-5" />
            </a>
            <button
              onClick={onCartOpen}
              className="p-2 text-foreground hover:text-accent transition-colors duration-[var(--motion-micro)] relative"
              aria-label={`Shopping cart, ${cartItemCount} items`}
            >
              <ShoppingBag className="w-5 h-5" />
              {cartItemCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-accent text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                  {cartItemCount}
                </span>
              )}
            </button>
            <a
              href={isAuthenticated ? "#/profile" : "#/auth"}
              className="p-2 text-foreground hover:text-accent transition-colors duration-[var(--motion-micro)]"
              aria-label={isAuthenticated ? "Profile" : "Login"}
            >
              <User className="w-5 h-5" />
            </a>
          </div>
        </div>

        {/* Mobile */}
        <div className="md:hidden flex items-center h-16 px-2">
          {/* Hamburger Button - Left */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-foreground hover:text-accent transition-colors flex-shrink-0"
            aria-label="Toggle menu"
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>

          {/* Centered Logo - Takes remaining space */}
          <div className="flex-1 flex items-center justify-center">
            <a 
              href="#/" 
              className="flex h-10 w-24 items-center justify-center flex-shrink-0"
              aria-label="Womanly Home"
            >
              <img src="/LOGO.png" alt="Womanly" className="max-h-full max-w-full object-contain" />
            </a>
          </div>

          {/* Action Buttons - Right */}
          <div className="flex items-center gap-1 flex-shrink-0">
            <button
              onClick={onSearchOpen}
              className="p-2 text-foreground hover:text-accent transition-colors"
              aria-label="Search"
            >
              <Search className="w-5 h-5" />
            </button>
            <button
              onClick={onCartOpen}
              className="p-2 text-foreground hover:text-accent transition-colors relative"
              aria-label={`Shopping cart, ${cartItemCount} items`}
            >
              <ShoppingBag className="w-5 h-5" />
              {cartItemCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-accent text-white text-xs w-4 h-4 rounded-full flex items-center justify-center">
                  {cartItemCount}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Mobile Drawer Menu - Slides from Left */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <>
              {/* Backdrop */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="md:hidden fixed inset-0 bg-black/30 backdrop-blur-sm z-40"
                onClick={() => setMobileMenuOpen(false)}
                aria-hidden="true"
              />

              {/* Drawer */}
              <motion.div
                initial={{ x: -320, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: -320, opacity: 0 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                className="md:hidden fixed left-0 top-0 h-full w-80 max-w-[80vw] bg-white surface-panel shadow-lg z-50 mobile-menu-drawer"
                role="dialog"
                aria-modal="true"
                aria-labelledby="mobile-menu-title"
              >
                {/* Drawer Header */}
                <div className="sticky top-0 bg-white border-b border-border px-6 py-4 flex items-center justify-between">
                  <h2 id="mobile-menu-title" className="font-headline text-lg">Menu</h2>
                  <button
                    onClick={() => setMobileMenuOpen(false)}
                    className="p-1 text-foreground hover:bg-secondary rounded transition-colors"
                    aria-label="Close menu"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                <div className="mobile-menu-scroll">
                  {/* Drawer Navigation */}
                  <nav className="px-6 py-6 space-y-2">
                      <a 
                        href="#/shop" 
                        className="block px-4 py-3 text-foreground hover:bg-secondary rounded-[var(--radius-sm)] transition-colors text-nav"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        Shop
                      </a>
                      <a 
                        href="#/wishlist" 
                        className="block px-4 py-3 text-foreground hover:bg-secondary rounded-[var(--radius-sm)] transition-colors text-nav"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        Wishlist
                      </a>
                      <a 
                        href="#/orders" 
                        className="block px-4 py-3 text-foreground hover:bg-secondary rounded-[var(--radius-sm)] transition-colors text-nav"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        Orders
                      </a>
                      <a 
                        href="#/about" 
                        className="block px-4 py-3 text-foreground hover:bg-secondary rounded-[var(--radius-sm)] transition-colors text-nav"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        About
                      </a>
                  </nav>

                  {/* Drawer Footer */}
                  <div className="px-6 py-6 border-t border-border">
                    <a 
                      href={isAuthenticated ? "#/profile" : "#/auth"}
                      className="flex items-center gap-3 px-4 py-3 text-foreground hover:bg-secondary rounded-[var(--radius-sm)] transition-colors mb-3"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <User className="w-5 h-5" />
                      <span className="text-nav">{isAuthenticated ? 'Profile' : 'Sign In'}</span>
                    </a>
                    <div className="pt-4 border-t border-border flex gap-4 justify-center">
                      <a 
                        href="https://instagram.com" 
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-muted hover:text-accent transition-colors"
                        aria-label="Instagram"
                      >
                        <Heart className="w-5 h-5" />
                      </a>
                      <a 
                        href="https://facebook.com" 
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-muted hover:text-accent transition-colors"
                        aria-label="Facebook"
                      >
                        <ShoppingBag className="w-5 h-5" />
                      </a>
                      <a 
                        href="https://twitter.com" 
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-muted hover:text-accent transition-colors"
                        aria-label="Twitter"
                      >
                        <Search className="w-5 h-5" />
                      </a>
                    </div>
                  </div>
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </nav>
    </header>
  );
}
