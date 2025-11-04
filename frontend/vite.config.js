import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // Bind to all interfaces for container access
    port: 3000,
    allowedHosts: true,  // Allow all hosts (for preview/proxy environments)
    proxy: {
      '/agent': {
        target: process.env.BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})

