import { fileURLToPath, URL } from 'node:url'

import { defineConfig, optimizeDeps } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  optimizeDeps: {
    include: [
      '@fawmi/vue-google-maps',
      'marker-clusterer-plus',
      'fast-deep-equal'
    ]
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: false
      }
    }
  }
})
