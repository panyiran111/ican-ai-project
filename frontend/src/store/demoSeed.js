/**
 * 演示数据预埋：录屏前访问 /?demo=seed 一键填充
 * - 小档案（山东济南 / 酸菜鱼 / 下象棋 / 橘猫胖虎）→ 天气卡、个性化文案立即生效
 * - 连续 7 天打卡（今天故意留空，方便录屏现场演示「去打卡」→ 解锁「小灶火」徽章）
 * - 合养宠物「团圆」已领养、少年期、今天未喂（方便现场演示喂食）
 * - 最近动态 3 条（首页不空荡）
 */
import { saveProfile } from './profile'
import { savePet } from './pet'

const dayKey = (d = new Date()) => {
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

export function isDemoSeedQuery() {
  return new URLSearchParams(location.search).get('demo') === 'seed'
}

export function seedDemoData() {
  // 1) 小档案
  saveProfile({
    mom_call: '妈',
    dad_call: '爸',
    hometown: '山东济南',
    mom_dish: '酸菜鱼',
    dad_hobby: '下象棋',
    pet: '橘猫胖虎',
  })

  // 2) 打卡：昨天往前 7 天（今天留空，现场演示打卡 → 8 天连击，小灶火徽章到手）
  const checkins = []
  const notes = ['食堂的酸菜鱼没有妈做的好吃', '今天跑步三公里', '和室友拍了合照', '图书馆学了一下午', '降温了加了衣服', '给家里打了电话', '吃了热乎的早饭']
  for (let i = 1; i <= 7; i++) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    checkins.push({ day: dayKey(d), photo: '', note: notes[i - 1] || '', time: d.getTime() + 20 * 3600 * 1000 })
  }
  localStorage.setItem('jiayin_checkins', JSON.stringify(checkins))

  // 3) 宠物：已领养「团圆」，成长 46（少年期），今天未喂（现场演示喂食 +5）
  const ev = []
  const now = Date.now()
  const H = 3600 * 1000
  const evt = (h, text) => ev.push({ time: now - h * H, text })
  evt(240, '团圆 来到我们家 🎉')
  evt(180, '打卡报了平安 +10')
  evt(120, '彩排了难开口的话 +10')
  evt(60, '解码了一份关心 +5')
  evt(30, '认真回了爸妈的话 +5')
  evt(12, '喂了顿饭 🍚 +5')
  savePet({ adopted: true, name: '团圆', type: 'cat', growth: 46, lastFeedDay: '', events: evt })

  // 4) 最近动态 3 条
  const history = [
    { type: 'rehearsal', title: '彩排「挂科了」：最难的一句已经说出口', detail: {}, time: now - 26 * H },
    { type: 'reply', title: '把「嗯，知道了」升级成了心里话', detail: {}, time: now - 50 * H },
    { type: 'decode', title: '解码：转发「这三种食物千万别隔夜吃」= 想你回家吃饭', detail: {}, time: now - 74 * H },
  ]
  localStorage.setItem('jiayin_history', JSON.stringify(history))

  // 5) 清掉 URL 参数，避免刷新重复预埋
  history.replaceState(null, '', location.pathname)
}
