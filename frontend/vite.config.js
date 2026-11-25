import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/users': 'http://localhost:8000',
      '/candidates': 'http://localhost:8000',
      '/recruiters': 'http://localhost:8000',
      '/companies': 'http://localhost:8000',
      '/job-offers': 'http://localhost:8000',
      '/applications': 'http://localhost:8000',
      '/admin': 'http://localhost:8000',
      '/dashboard': 'http://localhost:8000',
      '/matching': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
  build: {
    outDir: 'dist',
    rollupOptions: {},
  },
})
