/**
 * 每日安心打卡：localStorage 持久化
 * - 照片压缩到 ~500px 存 base64（localStorage 单条上限约 5MB，最多存 90 天）
 * - 连续天数：今天已打卡返回当前连击；昨天没打但今天打了从 1 重新数（温柔断签不惩罚）
 */
const KEY = 'jiayin_checkins'
const MAX = 90

export function getCheckins() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || []
  } catch {
    return []
  }
}

function save(list) {
  localStorage.setItem(KEY, JSON.stringify(list.slice(0, MAX)))
}

function dayKey(d = new Date()) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

export function checkedToday() {
  const today = dayKey()
  return getCheckins().some(c => c.day === today)
}

/** 连续天数（今天打过=当前连击；今天没打但昨天有=昨天为止的连击） */
export function streak() {
  const list = getCheckins()
  if (!list.length) return 0
  const days = new Set(list.map(c => c.day))
  const d = new Date()
  if (!days.has(dayKey(d))) d.setDate(d.getDate() - 1) // 今天还没打，从昨天数
  let n = 0
  while (days.has(dayKey(d))) {
    n++
    d.setDate(d.getDate() - 1)
  }
  return n
}

export function totalDays() {
  return getCheckins().length
}

export function addCheckin({ photo = '', note = '' }) {
  const list = getCheckins()
  const day = dayKey()
  const entry = { day, photo, note: String(note).slice(0, 200), time: Date.now() }
  const idx = list.findIndex(c => c.day === day)
  if (idx >= 0) list.splice(idx, 1) // 同一天重打=覆盖
  list.unshift(entry)
  save(list)
  return entry
}

/** 图片压缩：canvas 缩放到 maxW 内，输出 jpeg base64（质量 0.7） */
export function compressImage(file, maxW = 640) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = e => {
      const img = new Image()
      img.onload = () => {
        const scale = Math.min(1, maxW / img.width)
        const canvas = document.createElement('canvas')
        canvas.width = img.width * scale
        canvas.height = img.height * scale
        canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height)
        resolve(canvas.toDataURL('image/jpeg', 0.7))
      }
      img.onerror = reject
      img.src = e.target.result
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

/** 徽章体系：3/7/21/50/90 天（21 天 = 习惯养成） */
export const BADGES = [
  { days: 3,  icon: '🌱', name: '冒芽',   desc: '妈妈开始习惯每天看看你' },
  { days: 7,  icon: '🔥', name: '小灶火', desc: '一周了，爸妈的心放下一半' },
  { days: 21, icon: '🌟', name: '习惯成', desc: '21 天，安心成了日常' },
  { days: 50, icon: '💎', name: '心意石', desc: '50 天，份量沉甸甸' },
  { days: 90, icon: '🏆', name: '长情奖', desc: '90 天，天天都在说「我很好」' }
]

export function earnedBadges() {
  const s = streak()
  return BADGES.map(b => ({ ...b, earned: s >= b.days }))
}

/** 下一个待解锁徽章（全部解锁返回 null） */
export function nextBadge() {
  const s = streak()
  return BADGES.find(b => s < b.days) || null
}

/** 安心值：streak/21 封顶 100（呼应 21 天习惯） */
export function peaceLevel() {
  return Math.min(100, Math.round((streak() / 21) * 100))
}

/** 温柔断签文案：昨天断了但今天还没打 */
export function gentleNudge() {
  const list = getCheckins()
  if (!list.length) return '今天拍一张吧，让爸妈知道你很好'
  const y = new Date()
  y.setDate(y.getDate() - 1)
  const yesterdayKey = dayKey(y)
  const hasYesterday = list.some(c => c.day === yesterdayKey)
  if (!hasYesterday && !checkedToday()) {
    return '昨天断了一天，没关系，今天重新开始就好'
  }
  return ''
}
