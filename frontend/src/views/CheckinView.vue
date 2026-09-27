<template>
  <div class="page">
    <div class="page-title">每日安心打卡</div>
    <div class="page-sub">拍一张今天的生活，一句话就好。爸妈看到的不是照片，是「我今天也挺好」。</div>

    <!-- 状态卡 -->
    <div class="card status-card">
      <div class="streak-box">
        <div class="streak-num">🔥 {{ streakDays }}</div>
        <div class="streak-label">爸妈已连续 {{ streakDays }} 天<br />知道你很好</div>
      </div>
      <div class="peace-box">
        <div class="peace-head">
          <span>安心值</span>
          <span class="peace-num">{{ peace }}%</span>
        </div>
        <div class="peace-bar">
          <div class="peace-fill" :style="{ width: peace + '%' }"></div>
        </div>
        <div class="peace-tip" v-if="next">{{ next.icon }} 再坚持 {{ next.days - streakDays }} 天解锁「{{ next.name }}」</div>
        <div class="peace-tip" v-else>🏆 全部徽章已解锁，你是长情冠军</div>
      </div>
    </div>

    <!-- 今日打卡 -->
    <div class="card" v-if="!done">
      <div class="label">今天的照片 + 一句话</div>
      <div class="pick-row">
        <div class="photo-box" v-if="photo" @click="pick">
          <img :src="photo" alt="今日照片" />
        </div>
        <div class="photo-empty" v-else @click="pick">
          <van-icon name="photograph" size="26" color="#c9b8a8" />
          <span>拍照 / 选一张</span>
        </div>
      </div>
      <van-field
        v-model="note" type="textarea" rows="2" autosize maxlength="200"
        placeholder="一句话，比如：食堂新出的糖醋排骨，想到妈做的了"
        class="note-field"
      />
      <div class="source-row">
        <van-button size="small" plain round @click="pick(false)">📷 相机</van-button>
        <van-button size="small" plain round @click="pick(true)">🖼 相册</van-button>
      </div>
      <van-button
        type="primary" round block class="gradient-btn"
        :loading="submitting" loading-text="正在保存…"
        @click="submit"
      >{{ photo || note ? '打卡 ✅' : '不拍照也行，直接打卡' }}</van-button>
      <div class="tips">💡 也可以只写一句话。断签不惩罚，想起来就补上。</div>
    </div>

    <div class="card done-card" v-else>
      <div class="done-emoji">☀️</div>
      <div class="done-title">今天已经打过卡啦</div>
      <div class="done-sub">明天再来，把这份安心续上</div>
    </div>

    <!-- 徽章墙 -->
    <div class="card">
      <div class="label">徽章墙</div>
      <div class="badges">
        <div class="badge" v-for="b in badges" :key="b.days" :class="{ earned: b.earned }">
          <div class="badge-icon">{{ b.icon }}</div>
          <div class="badge-name">{{ b.name }}</div>
          <div class="badge-days">{{ b.days }}天</div>
          <div class="badge-desc">{{ b.earned ? b.desc : '未解锁' }}</div>
        </div>
      </div>
    </div>

    <!-- 时间轴 -->
    <div class="card" v-if="list.length">
      <div class="label">我的安心足迹（{{ list.length }} 天）</div>
      <div class="timeline">
        <div class="tl-item" v-for="c in list" :key="c.day">
          <div class="tl-dot"></div>
          <div class="tl-body">
            <div class="tl-day">{{ prettyDay(c.day) }}</div>
            <img v-if="c.photo" :src="c.photo" class="tl-photo" alt="" />
            <div class="tl-note" v-if="c.note">{{ c.note }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import {
  getCheckins, addCheckin, compressImage, checkedToday,
  streak, peaceLevel, earnedBadges, nextBadge
} from '../store/checkin'
import { addRecord } from '../store/history'
import { gain } from '../store/pet'

const streakDays = ref(0)
const peace = ref(0)
const badges = ref([])
const next = ref(null)
const done = ref(false)
const list = ref([])
const photo = ref('')
const note = ref('')
const submitting = ref(false)

let fileInput = null

onMounted(() => refresh())

function refresh() {
  streakDays.value = streak()
  peace.value = peaceLevel()
  badges.value = earnedBadges()
  next.value = nextBadge()
  done.value = checkedToday()
  list.value = getCheckins()
}

/** 临时 input[type=file] 拉起相机/相册（H5 通用） */
function pick(useAlbum = false) {
  if (fileInput) document.body.removeChild(fileInput)
  fileInput = document.createElement('input')
  fileInput.type = 'file'
  fileInput.accept = 'image/*'
  fileInput.capture = useAlbum ? undefined : 'environment'
  fileInput.style.display = 'none'
  fileInput.onchange = async () => {
    const f = fileInput.files && fileInput.files[0]
    if (!f) return
    try {
      photo.value = await compressImage(f)
    } catch {
      showToast('这张图片读取失败，换一张试试')
    }
  }
  document.body.appendChild(fileInput)
  fileInput.click()
}

async function submit() {
  submitting.value = true
  try {
    addCheckin({ photo: photo.value, note: note.value.trim() })
    addRecord('checkin', note.value.trim() || '今日安心打卡（附照片）', { day: new Date().toLocaleDateString() })
    const g = gain('checkin')
    showSuccessToast(g?.levelUp
      ? `打卡成功！宠物也长大成「${g.stage}」啦 🎉`
      : streakDays.value === 0 ? '打卡成功，安心值 +1 天！' : `已连续 ${streakDays.value + 1} 天，安心值上涨！`)
    photo.value = ''
    note.value = ''
    refresh()
  } finally {
    submitting.value = false
  }
}

function prettyDay(day) {
  const [y, m, d] = day.split('-').map(Number)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const that = new Date(y, m - 1, d)
  const diff = Math.round((today - that) / 86400000)
  if (diff === 0) return '今天'
  if (diff === 1) return '昨天'
  return `${m}月${d}日`
}
</script>

<style scoped>
.label { font-size: 12px; color: var(--jiayin-text-light); margin: 0 0 8px; }

.status-card {
  display: flex;
  gap: 16px;
  align-items: center;
  background: linear-gradient(135deg, #fff 30%, #fdf1e3 100%);
}
.streak-box { text-align: center; flex-shrink: 0; }
.streak-num { font-size: 30px; font-weight: 800; color: var(--jiayin-primary-deep); line-height: 1.1; }
.streak-label { font-size: 11px; color: var(--jiayin-text-light); margin-top: 6px; line-height: 1.5; }
.peace-box { flex: 1; }
.peace-head { display: flex; justify-content: space-between; font-size: 12px; color: var(--jiayin-text-light); }
.peace-num { font-weight: 700; color: var(--jiayin-primary-deep); }
.peace-bar {
  height: 8px;
  background: #f0e2cf;
  border-radius: 999px;
  margin: 6px 0 8px;
  overflow: hidden;
}
.peace-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--jiayin-accent), var(--jiayin-primary));
  transition: width .6s ease;
}
.peace-tip { font-size: 11px; color: var(--jiayin-text-light); }

.photo-empty {
  width: 100%;
  min-height: 120px;
  border: 1.5px dashed #e3d2ba;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  color: var(--jiayin-text-light);
  cursor: pointer;
  background: #faf6f0;
}
.photo-box {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  max-height: 260px;
}
.photo-box img { width: 100%; display: block; }
.note-field {
  background: #faf6f0;
  border-radius: 10px;
  margin-top: 10px;
}
.source-row { display: flex; gap: 8px; margin: 10px 0 14px; }

.done-card { text-align: center; padding: 26px 16px; }
.done-emoji { font-size: 40px; }
.done-title { font-size: 16px; font-weight: 700; margin-top: 8px; }
.done-sub { font-size: 12px; color: var(--jiayin-text-light); margin-top: 4px; }

.badges { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 4px; }
.badge {
  flex-shrink: 0;
  width: 92px;
  border: 1.5px solid #f0e2cf;
  border-radius: 12px;
  padding: 10px 6px;
  text-align: center;
  opacity: .45;
  filter: grayscale(.9);
}
.badge.earned {
  opacity: 1;
  filter: none;
  border-color: var(--jiayin-primary);
  background: #fdf9f2;
}
.badge-icon { font-size: 26px; }
.badge-name { font-size: 12px; font-weight: 700; margin-top: 4px; }
.badge-days { font-size: 10px; color: var(--jiayin-primary-deep); font-weight: 600; }
.badge-desc { font-size: 10px; color: var(--jiayin-text-light); margin-top: 3px; line-height: 1.4; }

.timeline { position: relative; padding-left: 14px; }
.tl-item { position: relative; padding: 0 0 16px; }
.tl-item:last-child { padding-bottom: 2px; }
.tl-dot {
  position: absolute;
  left: -14px;
  top: 5px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--jiayin-primary);
}
.tl-item::before {
  content: '';
  position: absolute;
  left: -11px;
  top: 14px;
  bottom: -2px;
  width: 2px;
  background: #f0e2cf;
}
.tl-item:last-child::before { display: none; }
.tl-day { font-size: 13px; font-weight: 700; }
.tl-photo {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  border-radius: 10px;
  margin-top: 6px;
}
.tl-note { font-size: 13px; color: var(--jiayin-text); margin-top: 6px; line-height: 1.6; }

.tips { font-size: 12px; color: var(--jiayin-text-light); text-align: center; margin: 12px 4px 2px; line-height: 1.6; }
</style>
