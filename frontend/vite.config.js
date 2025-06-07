import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  esbuild: {
    loader: 'jsx',
    include: /src\/.*\.[jt]sx?$/,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://20.205.22.95:5000',
        changeOrigin: true,
      }
    }
  }
})