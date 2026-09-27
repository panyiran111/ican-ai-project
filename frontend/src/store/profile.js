/**
 * 爸妈画像：localStorage 持久化
 * 首次使用引导填写，之后所有模块生成内容时注入专属细节
 */
const KEY = 'jiayin_profile'

export const emptyProfile = {
  mom_call: '',      // 怎么称呼妈妈，如「妈」「老妈」
  dad_call: '',      // 怎么称呼爸爸
  hometown: '',      // 老家，如「山东济南」
  mom_dish: '',      // 妈妈的拿手菜，如「红烧排骨」
  dad_hobby: '',     // 爸爸的爱好，如「下象棋」「钓鱼」
  pet: ''            // 家里的猫狗，如「橘猫胖虎」
}

export function getProfile() {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return { ...emptyProfile }
    return { ...emptyProfile, ...JSON.parse(raw) }
  } catch {
    return { ...emptyProfile }
  }
}

export function saveProfile(p) {
  localStorage.setItem(KEY, JSON.stringify(p))
}

export function isProfileEmpty() {
  const p = getProfile()
  return !p.mom_dish && !p.dad_hobby && !p.hometown && !p.pet
}

/** 生成给后端的紧凑画像摘要（空字段自动剔除） */
export function profileSummary() {
  const p = getProfile()
  const parts = []
  if (p.mom_call) parts.push(`称呼妈妈「${p.mom_call}」`)
  if (p.dad_call) parts.push(`称呼爸爸「${p.dad_call}」`)
  if (p.hometown) parts.push(`老家${p.hometown}`)
  if (p.mom_dish) parts.push(`妈妈拿手菜是${p.mom_dish}`)
  if (p.dad_hobby) parts.push(`爸爸爱好${p.dad_hobby}`)
  if (p.pet) parts.push(`家里养了${p.pet}`)
  return parts.join('；')
}
