/**
 * API 地址统一出口：
 * - 本地开发：VITE_API_BASE 为空 → 请求相对路径，走 Vite 代理（127.0.0.1:8000）
 * - 线上部署：构建时注入 VITE_API_BASE=https://xxx.onrender.com → 直连线上后端
 */
const BASE = (import.meta.env.VITE_API_BASE || '').replace(/\/+$/, '')

export function apiUrl(path) {
  return BASE + path
}

export async function apiPost(path, body) {
  const res = await fetch(apiUrl(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  if (!res.ok) throw new Error(`API ${path} -> ${res.status}`)
  return res.json()
}
