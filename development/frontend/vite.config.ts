import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { tanstackRouter } from '@tanstack/router-plugin/vite'

export default defineConfig({
  appType: 'spa',
  server: {
    host: 'wagtail-ninja-frontend',
    port: 3000,
    proxy: {
      '/api': 'http://wagtail-ninja-django:8000',
    },
  },
  plugins: [
      tanstackRouter({
          // Optional: Configure target framework (e.g., 'react')
          target: 'react',
          // Optional: Enable auto code-splitting
          autoCodeSplitting: true,
        }),
      react(),
  ],
})
