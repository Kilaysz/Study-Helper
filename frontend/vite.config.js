import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // CRITICAL: Force esbuild/vite to target a newer version that supports import.meta
  esbuild: {
    target: 'es2020',
  },
  build: {
    target: 'es2020',
  },
  server: {
    host: true // Ensure it listens on all local IPs
  }
})