import { defineConfig } from 'vite'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    // The React and Tailwind plugins are both required for Make, even if
    // Tailwind is not being actively used – do not remove them
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      // Alias @ to the src directory
      '@': path.resolve(__dirname, './src'),
    },
  },

  // File types to support raw imports. Never add .css, .tsx, or .ts files to this.
  assetsInclude: ['**/*.svg', '**/*.csv'],
  
  build: {
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
    
    // Small assets inlined as base64 (reduces HTTP requests)
    assetsInlineLimit: 8192,
    
    // CSS code splitting enabled by default (good for performance)
    cssCodeSplit: true,
    
    rollupOptions: {
      output: {
        // Manual chunks for better caching and code splitting
        manualChunks: (id) => {
          // Vendor chunks
          if (id.includes('node_modules')) {
            if (id.includes('react')) return 'react-vendor'
            if (id.includes('radix-ui')) return 'ui-vendor'
            if (id.includes('framer-motion')) return 'animations'
            if (id.includes('lucide-react')) return 'icons'
            return 'vendor'
          }
          
          // Route-specific chunks for code splitting
          if (id.includes('AuthPage')) return 'auth'
          if (id.includes('ProductDetailModal')) return 'product-detail'
          if (id.includes('CartDrawer')) return 'cart'
        },
        
        // Optimize generated bundle filename patterns
        entryFileNames: 'js/[name].[hash].js',
        chunkFileNames: 'js/[name].[hash].js',
        assetFileNames: ({ name }) => {
          if (name.endsWith('.css')) {
            return 'css/[name].[hash][extname]'
          }
          return 'assets/[name].[hash][extname]'
        },
      },
    },
    
    // Disable source maps in production (smaller bundle)
    sourcemap: false,
    
    // Use esbuild for faster builds
    minify: 'esbuild',
    esbuild: {
      // Drop console and debugger statements
      drop: ['console', 'debugger'],
    },
  },
  
  // Preview server config (for production preview)
  preview: {
    port: 5173,
    strictPort: true,
  },
})
