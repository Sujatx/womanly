import { useEffect, useRef, useState } from 'react';
import { X, Search as SearchIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { products } from '@/app/data/products';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const [results, setResults] = useState(products.slice(0, 6));

  // Focus trap and ESC handler
  useEffect(() => {
    if (!isOpen) return;

    // Focus input when opened
    setTimeout(() => inputRef.current?.focus(), 100);

    // Lock scroll
    document.body.style.overflow = 'hidden';
    document.body.style.paddingRight = '0px'; // Scrollbar compensation

    // ESC handler
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);

    return () => {
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  // Search logic (mock debounced search)
  useEffect(() => {
    if (!query.trim()) {
      setResults(products.slice(0, 6));
      return;
    }

    const timer = setTimeout(() => {
      const filtered = products.filter(
        (p) =>
          p.name.toLowerCase().includes(query.toLowerCase()) ||
          p.collection.toLowerCase().includes(query.toLowerCase())
      );
      setResults(filtered);
    }, 300); // 300ms debounce

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.35, ease: [0.2, 0.8, 0.2, 1] }}
            className="fixed inset-0 bg-backdrop-black backdrop-blur-sm z-[var(--z-backdrop)]"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.35, ease: [0.2, 0.8, 0.2, 1] }}
            className="fixed inset-0 z-[var(--z-modal)] overflow-y-auto"
            role="dialog"
            aria-modal="true"
            aria-labelledby="search-heading"
          >
            <div className="min-h-screen bg-white px-6 py-12 md:py-24">
              <div className="container mx-auto max-w-4xl">
                {/* Header */}
                <div className="flex items-center justify-between mb-12">
                  <h2 id="search-heading" className="font-headline text-4xl md:text-5xl">
                    Search
                  </h2>
                  <button
                    onClick={onClose}
                    className="p-2 text-foreground hover:text-accent transition-colors"
                    aria-label="Close search"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                {/* Search Input */}
                <div className="relative mb-12">
                  <SearchIcon className="absolute left-0 top-1/2 -translate-y-1/2 w-6 h-6 text-muted" />
                  <input
                    ref={inputRef}
                    type="search"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search for products..."
                    className="w-full pl-10 pr-4 py-4 border-b-2 border-border focus:border-accent bg-transparent text-2xl placeholder:text-muted outline-none transition-colors"
                    aria-label="Search products"
                    aria-describedby="search-results-status"
                  />
                </div>

                {/* Results */}
                <div
                  role="region"
                  aria-live="polite"
                  aria-atomic="true"
                  id="search-results-status"
                  className="sr-only"
                >
                  {results.length} results found
                </div>

                {results.length > 0 ? (
                  <div>
                    <h3 className="text-nav text-muted mb-6">
                      {query ? 'Results' : 'Popular Products'}
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                      {results.map((product) => (
                        <a
                          key={product.id}
                          href={`#product/${product.id}`}
                          className="group"
                          onClick={onClose}
                        >
                          <div className="aspect-[4/5] bg-secondary rounded-[var(--radius-md)] overflow-hidden mb-3">
                            <img
                              src={product.images[0]}
                              alt={product.name}
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-[var(--motion-major)]"
                            />
                          </div>
                          <p className="text-small text-muted mb-1">{product.collection}</p>
                          <p className="font-medium">{product.name}</p>
                          <p className="text-small mt-1">${product.salePrice || product.price}</p>
                        </a>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-muted text-lg">No products found for "{query}"</p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
