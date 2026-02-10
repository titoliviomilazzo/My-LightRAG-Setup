import { defineConfig } from 'vite'
import path from 'path'
import { webuiPrefix } from './src/lib/constants'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    },
    dedupe: ['katex']
  },
  base: webuiPrefix,
  build: {
    outDir: path.resolve(__dirname, '../lightrag/api/webui'),
    emptyOutDir: true,
    chunkSizeWarningLimit: 3800,
    rollupOptions: {
      output: {
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },
  // Safely read env vars: when Vite bundles the config, import.meta.env may be undefined.
  // Fallback to process.env when available.
  server: (() => {
    const env: any = (typeof import.meta !== 'undefined' && import.meta.env)
      ? import.meta.env
      : typeof process !== 'undefined'
      ? process.env
      : {};

    if (env.VITE_API_PROXY === 'true' && env.VITE_API_ENDPOINTS) {
      return {
        proxy: Object.fromEntries(
          String(env.VITE_API_ENDPOINTS).split(',').map((endpoint: string) => [
            endpoint,
            {
              target: env.VITE_BACKEND_URL || 'http://localhost:9621',
              changeOrigin: true,
              rewrite:
                endpoint === '/api'
                  ? (p: string) => p.replace(/^\/api/, '')
                  : endpoint === '/docs' || endpoint === '/redoc' || endpoint === '/openapi.json' || endpoint === '/static'
                  ? (p: string) => p
                  : undefined,
            },
          ])
        ),
      };
    }

    return { proxy: {} };
  })(),
})
