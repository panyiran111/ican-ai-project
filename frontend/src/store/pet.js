/**
 * 合养小宠物：localStorage 持久化（与打卡同思路：纯本地、不上传、温柔不惩罚）
 *
 * 产品逻辑：宠物是「全家的孩子」——
 * - 子女完成沟通任务（解码/回音/话题/彩排/打卡）→ 宠物获得成长值
 * - 每天可以喂一次；断喂不惩罚，宠物不会离开
 * - 「分享给爸妈」把宠物近况变成一段现成的聊天素材
 */
const KEY = 'jiayin_pet'
const MAX_EVENTS = 12

export const PET_TYPES = [
  { key: 'cat',    emoji: '🐱', name: '小猫' },
  { key: 'dog',    emoji: '🐶', name: '小狗' },
  { key: 'rabbit', emoji: '🐰', name: '小兔' },
]

/** 成长阶段（growth 达到 min 进入该阶段） */
export const STAGES = [
  { min: 0,   name: '幼崽', desc: '刚来我们家，怯生生的' },
  { min: 40,  name: '少年', desc: '活泼好动，爱撒娇' },
  { min: 120, name: '成年', desc: '稳重了些，但还是粘人' },
  { min: 300, name: '家人', desc: '早已是家里的一员' },
]

/** 沟通任务 → 成长值 */
export const TASK_POINTS = {
  decode: 5, reply: 5, topic: 3, rehearsal: 10, checkin: 10,
}
export const TASK_NAMES = {
  decode: '解码了一份关心', reply: '认真回了爸妈的话',
  topic: '抽了话题卡', rehearsal: '彩排了难开口的话', checkin: '打卡报了平安',
}

function emptyPet() {
  return { adopted: false, name: '', type: 'cat', growth: 0, lastFeedDay: '', events: [] }
}

export function getPet() {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return emptyPet()
    return { ...emptyPet(), ...JSON.parse(raw) }
  } catch {
    return emptyPet()
  }
}

export function savePet(p) {
  try {
    localStorage.setItem(KEY, JSON.stringify(p))
  } catch { /* 存储满等异常：静默，不影响主流程 */ }
}

export function isAdopted() {
  return getPet().adopted
}

function dayKey(d = new Date()) {
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

function addEvent(p, text) {
  p.events.unshift({ time: Date.now(), text })
  p.events = p.events.slice(0, MAX_EVENTS)
}

export function adoptPet(name, type) {
  const p = emptyPet()
  p.adopted = true
  p.name = String(name || '').trim().slice(0, 12) || '团圆'
  p.type = PET_TYPES.some(t => t.key === type) ? type : 'cat'
  addEvent(p, `${p.name} 来到我们家 🎉`)
  savePet(p)
  return p
}

export function typeEmoji(p = getPet()) {
  return PET_TYPES.find(t => t.key === p.type)?.emoji || '🐱'
}

export function typeName(p = getPet()) {
  return PET_TYPES.find(t => t.key === p.type)?.name || '小猫'
}

export function stageOf(growth) {
  let s = STAGES[0]
  for (const st of STAGES) if (growth >= st.min) s = st
  return s
}

export function nextStage(growth) {
  return STAGES.find(st => growth < st.min) || null
}

/** 完成沟通任务 → 领成长值（未领养返回 null，静默不打扰） */
export function gain(task) {
  const p = getPet()
  if (!p.adopted) return null
  const pts = TASK_POINTS[task]
  if (!pts) return null
  const before = stageOf(p.growth)
  p.growth += pts
  addEvent(p, `${TASK_NAMES[task] || task} +${pts}`)
  const after = stageOf(p.growth)
  if (before.name !== after.name) addEvent(p, `长大啦：${before.name} → ${after.name} 🎉`)
  savePet(p)
  return { pts, levelUp: before.name !== after.name, stage: after.name }
}

export function fedToday() {
  return getPet().lastFeedDay === dayKey()
}

/** 每日喂食一次（+5），断喂不惩罚 */
export function feed() {
  const p = getPet()
  if (!p.adopted || p.lastFeedDay === dayKey()) return { fed: false }
  p.lastFeedDay = dayKey()
  const before = stageOf(p.growth)
  p.growth += 5
  addEvent(p, '喂了顿饭 🍚 +5')
  const after = stageOf(p.growth)
  if (before.name !== after.name) addEvent(p, `长大啦：${before.name} → ${after.name} 🎉`)
  savePet(p)
  return { fed: true, levelUp: before.name !== after.name }
}

/** 生成分享给爸妈的聊天文案（复制用） */
export function shareText() {
  const p = getPet()
  if (!p.adopted) return ''
  const stage = stageOf(p.growth)
  const t = typeName(p)
  const shareScripts = [
    `给你看看我们家的${t}「${p.name}」，它现在是${stage.name}啦～${typeEmoji(p)}`,
    `「${p.name}」今天又长大了一点，等放假回去，它就认识你们了 ${typeEmoji(p)}`,
    `${p.name}说：让爸妈也看看我嘛 ${typeEmoji(p)}（它想你们了）`,
  ]
  return shareScripts[p.growth % shareScripts.length]
}
