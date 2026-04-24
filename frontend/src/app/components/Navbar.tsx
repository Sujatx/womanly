import { useState } from 'react';
import { Search, Heart, ShoppingBag, User, Menu, X } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface NavbarProps {
  onSearchOpen: () => void;
  onCartOpen: () => void;
  cartItemCount: number;
}

export function Navbar({ onSearchOpen, onCartOpen, cartItemCount }: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isAuthenticated } = useAuth();

  return (
    <header className="sticky top-0 surface-panel border-b border-border z-[var(--z-header)]">
      <nav className="container mx-auto px-6" aria-label="Main navigation">
        {/* Desktop & Tablet */}
        <div className="hidden md:flex items-center justify-between h-20">
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
        <div className="md:hidden flex items-center justify-between h-16">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-foreground"
            aria-label="Toggle menu"
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>

          <a 
            href="#/" 
            className="flex h-10 w-24 items-center justify-center sm:h-12 sm:w-28"
            aria-label="Womanly Home"
          >
            <img src="/favicon.png" alt="Womanly" className="max-h-full max-w-full object-contain" />
          </a>

          <div className="flex items-center gap-4">
            <button
              onClick={onSearchOpen}
              className="p-2 text-foreground"
              aria-label="Search"
            >
              <Search className="w-5 h-5" />
            </button>
            <button
              onClick={onCartOpen}
              className="p-2 text-foreground relative"
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

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-6 border-t border-border">
            <div className="flex flex-col gap-6">
              <a 
                href="#/shop" 
                className="text-nav text-foreground"
                onClick={() => setMobileMenuOpen(false)}
              >
                Shop
              </a>
              <a 
                href="#/wishlist" 
                className="text-nav text-foreground"
                onClick={() => setMobileMenuOpen(false)}
              >
                Wishlist
              </a>
              <a 
                href="#/orders" 
                className="text-nav text-foreground"
                onClick={() => setMobileMenuOpen(false)}
              >
                Orders
              </a>
              <div className="pt-6 border-t border-border flex gap-6">
                <a href="#/wishlist" className="text-foreground" aria-label="Wishlist">
                  <Heart className="w-5 h-5" />
                </a>
                <a 
                  href={isAuthenticated ? "#/profile" : "#/auth"}
                  className="text-foreground" 
                  aria-label={isAuthenticated ? "Profile" : "Login"}
                >
                  <User className="w-5 h-5" />
                </a>
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
