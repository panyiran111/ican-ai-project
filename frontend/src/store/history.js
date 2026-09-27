/**
 * 使用历史：localStorage 持久化（最近 50 条）
 * 类型：decode 解码 / reply 回复 / topic 话题 / rehearsal 彩排
 */
const KEY = 'jiayin_history'
const MAX = 50

export function getHistory() {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return []
    return JSON.parse(raw)
  } catch {
    return []
  }
}

/**
 * @param {string} type  decode | reply | topic | rehearsal
 * @param {string} title 一行摘要（如解码的核心信息、回复的 normal 档）
 * @param {object} detail 完整结果，供回看
 */
export function addRecord(type, title, detail) {
  const list = getHistory()
  list.unshift({ type, title: String(title).slice(0, 80), detail, time: Date.now() })
  localStorage.setItem(KEY, JSON.stringify(list.slice(0, MAX)))
}

export function clearHistory() {
  localStorage.removeItem(KEY)
}

export const TYPE_META = {
  decode:    { icon: '🎧', name: '解码', route: '/decode' },
  reply:     { icon: '💬', name: '回音', route: '/reply' },
  topic:     { icon: '🎴', name: '话题', route: '/topic' },
  rehearsal: { icon: '🎭', name: '彩排', route: '/rehearsal' },
  checkin:   { icon: '📷', name: '打卡', route: '/checkin' }
}
