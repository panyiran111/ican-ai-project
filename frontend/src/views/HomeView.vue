<template>
  <div class="page">
    <!-- 今日卡：日期 + 节日倒计时 -->
    <div class="card today-bar">
      <span class="today-date">📅 {{ todayText }}</span>
      <span class="today-fest" v-if="fest">🗓 {{ fest.name }}还有 {{ fest.days }} 天，通话时聊聊？</span>
    </div>

    <div class="hero">
      <div class="hero-badge">AI 家庭沟通翻译官</div>
      <h1 class="hero-title">爸妈的每一条养生文<br />都是没说出口的想你</h1>
      <p class="hero-sub">家音站在两代人中间：把养生文翻成关心，把"嗯"翻成"我也想你"。</p>
      <div class="hero-profile" @click="profileShow = true">
        <span v-if="!hasProfile">＋ 建一份「我家小档案」，让 AI 更懂你家</span>
        <span v-else>🏠 {{ profileText }} · 点击修改</span>
      </div>
    </div>

    <!-- 老家天气卡：天气 = 现成的关心话题 -->
    <div class="card weather-card" v-if="weather">
      <div class="w-now">
        <span class="w-emoji">{{ weather.emoji }}</span>
        <span class="w-city">{{ weather.city }}</span>
        <span class="w-temp">{{ weather.temp }}℃</span>
        <span class="w-desc">{{ weather.desc }}</span>
      </div>
      <div class="w-range" v-if="weather.tmax != null">{{ weather.tmin }}℃ ~ {{ weather.tmax }}℃</div>
      <div class="w-tip">{{ weather.tip }}</div>
      <van-button size="small" round type="primary" plain class="w-btn" @click="goReplyWithWeather">
        💬 拿天气跟爸妈聊两句 →
      </van-button>
    </div>
    <div class="card weather-card" v-else-if="!hasProfile" @click="profileShow = true">
      <div class="w-tip" style="margin:0">📍 填一下「我家小档案」的老家，就能看到爸妈那边的天气</div>
    </div>

    <!-- 每日安心打卡横幅 -->
    <div class="card checkin-banner" :class="{ done: checkinDone }" @click="$router.push('/checkin')">
      <div class="cb-left">
        <div class="cb-streak" v-if="checkinStreak > 0">🔥 {{ checkinStreak }}</div>
        <div class="cb-streak" v-else>📷</div>
      </div>
      <div class="cb-body">
        <div class="cb-title">
          <template v-if="checkinDone">今日已打卡，安心续上了 ☀️</template>
          <template v-else>{{ nudgeText }}</template>
        </div>
        <div class="cb-sub">爸妈已连续 {{ checkinStreak }} 天知道你很好 · 点击{{ checkinDone ? '回看足迹' : '去打卡' }} →</div>
      </div>
      <img v-if="todayPhoto" :src="todayPhoto" class="cb-photo" alt="" />
    </div>

    <div class="card feature" v-for="f in features" :key="f.to" @click="$router.push(f.to)">
      <div class="feature-icon">{{ f.icon }}</div>
      <div class="feature-body">
        <div class="feature-name">{{ f.name }}</div>
        <div class="feature-desc">{{ f.desc }}</div>
      </div>
      <van-icon name="arrow" color="#c9b8a8" />
    </div>

    <!-- 最近动态 -->
    <div v-if="records.length" class="recent">
      <div class="recent-head">
        <span>📔 最近的家音</span>
        <span class="clear" @click="onClear">清空</span>
      </div>
      <div class="card recent-item" v-for="(r, i) in records.slice(0, 5)" :key="r.time + '-' + i">
        <div class="recent-icon">{{ TYPE_META[r.type]?.icon || '📝' }}</div>
        <div class="recent-body">
          <div class="recent-title">{{ r.title }}</div>
          <div class="recent-time">{{ fmtTime(r.time) }} · {{ TYPE_META[r.type]?.name || r.type }}</div>
        </div>
      </div>
    </div>

    <div class="card demo-entry" @click="$router.push('/decode')">
      <van-icon name="play-circle-o" size="20" color="#e8833a" />
      <span>一键体验「王阿姨」演示剧本</span>
    </div>

    <ProfilePopup v-model="profileShow" @saved="refreshProfile" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import ProfilePopup from '../components/ProfilePopup.vue'
import { getProfile, isProfileEmpty } from '../store/profile'
import { getHistory, clearHistory, TYPE_META } from '../store/history'
import { checkedToday, streak as checkinStreakFn, gentleNudge, getCheckins } from '../store/checkin'
import { apiGet } from '../api'

const router = useRouter()
const profileShow = ref(false)
const hasProfile = ref(false)
const profileText = ref('')
const records = ref([])
const checkinDone = ref(false)
const checkinStreak = ref(0)
const nudgeText = ref('今天拍一张吧，让爸妈知道你很好')
const todayPhoto = ref('')
const weather = ref(null)

// ---------- 今日卡：日期 + 节日倒计时 ----------
const WEEK = ['日', '一', '二', '三', '四', '五', '六']
const now = new Date()
const todayText = `${now.getMonth() + 1}月${now.getDate()}日 星期${WEEK[now.getDay()]}`

const FESTIVALS = [
  { date: '2026-10-01', name: '国庆' },
  { date: '2027-01-01', name: '元旦' },
  { date: '2027-02-06', name: '春节' },
  { date: '2027-09-15', name: '中秋' },
]
const fest = (() => {
  const today0 = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  for (const f of FESTIVALS) {
    const [y, m, d] = f.date.split('-').map(Number)
    const days = Math.round((new Date(y, m - 1, d) - today0) / 86400000)
    if (days > 0) return { name: f.name, days }
  }
  return null
})()

const features = [
  { icon: '🎧', name: '关心解码器', desc: '60秒语音、养生文，翻译成背后没说出口的关心', to: '/decode' },
  { icon: '💬', name: '回音壁', desc: '把"嗯、在忙、知道了"升级成像你说的心里话', to: '/reply' },
  { icon: '🎭', name: '高难对话彩排室', desc: '挂科了/要生活费，先和 AI 版爸妈彩排一遍', to: '/rehearsal' },
  { icon: '🎴', name: '连心话题卡', desc: '通话前 5 个不尬聊的开放式话题', to: '/topic' },
  { icon: '🐾', name: '合养小宠物', desc: '全家的孩子：你每次好好说话，它就长大一点', to: '/pet' }
]

function refreshProfile() {
  const p = getProfile()
  hasProfile.value = !isProfileEmpty()
  const bits = []
  if (p.hometown) bits.push(p.hometown)
  if (p.mom_dish) bits.push(`妈妈的味道是${p.mom_dish}`)
  if (p.dad_hobby) bits.push(`爸爸爱${p.dad_hobby}`)
  profileText.value = bits.join(' · ')
}

onMounted(() => {
  refreshProfile()
  records.value = getHistory()
  refreshCheckin()
  loadWeather()
})

// ---------- 老家天气 ----------
async function loadWeather() {
  const p = getProfile()
  if (!p.hometown) { hasProfile.value = isProfileEmpty(); return }
  try {
    weather.value = await apiGet('/api/weather?city=' + encodeURIComponent(p.hometown))
  } catch {
    weather.value = null  // 静默失败，不占首页
  }
}

function goReplyWithWeather() {
  const w = weather.value
  if (!w) return
  const c = w.desc.includes('雨')
    ? `老家今天${w.desc}，出门记得带伞、走路慢一点呀`
    : `老家今天${w.desc}，${w.temp}℃，你们注意添减衣服`
  router.push({ path: '/reply', query: { c } })
}

function refreshCheckin() {
  checkinDone.value = checkedToday()
  checkinStreak.value = checkinStreakFn()
  nudgeText.value = gentleNudge() || '今天拍一张吧，让爸妈知道你很好'
  const todayEntry = getCheckins().find(c => {
    const d = new Date()
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    return c.day === key
  })
  todayPhoto.value = todayEntry?.photo || ''
}

function fmtTime(ts) {
  const d = new Date(ts)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${d.getMonth() + 1}月${d.getDate()}日 ${hh}:${mm}`
}

function onClear() {
  showConfirmDialog({ title: '清空最近记录', message: '清空后不可恢复，确定吗？' })
    .then(() => { clearHistory(); records.value = []; showToast('已清空') })
    .catch(() => {})
}
</script>

<style scoped>
.hero {
  background: linear-gradient(150deg, #f7c873 0%, #f59e5b 100%);
  border-radius: 20px;
  padding: 28px 20px;
  color: #fff;
  margin: 12px 0 18px;
}
.hero-badge {
  display: inline-block;
  font-size: 11px;
  background: rgba(255, 255, 255, 0.25);
  padding: 3px 10px;
  border-radius: 999px;
  margin-bottom: 12px;
}
.hero-title {
  font-size: 24px;
  line-height: 1.45;
  margin: 0 0 10px;
  font-weight: 700;
}
.hero-sub {
  font-size: 13px;
  opacity: 0.92;
  margin: 0;
  line-height: 1.7;
}
.hero-profile {
  margin-top: 14px;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.22);
  border-radius: 10px;
  padding: 8px 10px;
  cursor: pointer;
  line-height: 1.5;
}
.today-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
}
.today-date { flex-shrink: 0; }
.today-fest {
  font-size: 12px;
  font-weight: 500;
  color: var(--jiayin-primary-deep);
  text-align: right;
  line-height: 1.4;
}

.weather-card {
  border: 1.5px solid #cfe3f2;
  background: linear-gradient(135deg, #fff 40%, #eef6fc 100%);
}
.w-now { display: flex; align-items: baseline; gap: 8px; }
.w-emoji { font-size: 22px; }
.w-city { font-size: 14px; font-weight: 700; }
.w-temp { font-size: 20px; font-weight: 800; color: var(--jiayin-primary-deep); }
.w-desc { font-size: 13px; color: var(--jiayin-text-light); }
.w-range { font-size: 11px; color: var(--jiayin-text-light); margin-top: 2px; }
.w-tip {
  font-size: 13px;
  line-height: 1.6;
  margin: 8px 0 4px;
}
.w-btn { margin-top: 6px; }

.checkin-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  border: 1.5px solid #f2c79b;
  background: linear-gradient(135deg, #fff 40%, #fdf1e3 100%);
}
.checkin-banner:active { opacity: 0.85; }
.checkin-banner.done { border-color: #cfe8d0; background: linear-gradient(135deg, #fff 40%, #f0f9ef 100%); }
.cb-left { flex-shrink: 0; }
.cb-streak {
  font-size: 20px;
  font-weight: 800;
  color: var(--jiayin-primary-deep);
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: #fdf1e3;
  display: flex;
  align-items: center;
  justify-content: center;
}
.done .cb-streak { background: #e9f6e9; }
.cb-body { flex: 1; min-width: 0; }
.cb-title { font-size: 14px; font-weight: 600; line-height: 1.4; }
.cb-sub { font-size: 11px; color: var(--jiayin-text-light); margin-top: 4px; line-height: 1.5; }
.cb-photo {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  object-fit: cover;
}

.feature {
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
}
.feature:active { opacity: 0.8; }
.feature-icon {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: #fdf1e3;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}
.feature-name { font-weight: 600; font-size: 15px; }
.feature-desc { font-size: 12px; color: var(--jiayin-text-light); margin-top: 3px; }

.recent { margin-top: 6px; }
.recent-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 700;
  font-size: 15px;
  margin: 6px 4px 10px;
}
.recent-head .clear {
  font-size: 12px;
  font-weight: 400;
  color: var(--jiayin-text-light);
  cursor: pointer;
}
.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  margin-bottom: 8px;
}
.recent-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: #fdf1e3;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
.recent-title {
  font-size: 13px;
  line-height: 1.5;
  color: var(--jiayin-text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.recent-time { font-size: 11px; color: var(--jiayin-text-light); margin-top: 3px; }

.demo-entry {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--jiayin-primary-deep);
  cursor: pointer;
  border: 1px dashed #f2c79b;
}
</style>
