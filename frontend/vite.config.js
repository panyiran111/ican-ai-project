import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 本地开发代理目标可通过环境变量覆盖，默认本地后端
const proxyTarget = process.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: proxyTarget,
        changeOrigin: true
      }
    }
  }
})
