<template>
  <div class="page">
    <div class="page-title">回音壁</div>
    <div class="page-sub">把"嗯、在忙、知道了"升级成像你说的、有温度的话。先告诉家音：你平时是怎么说话的？</div>

    <div class="card">
      <div class="label">父母说了什么 / 你想回应的话题</div>
      <div class="input-row">
        <van-field
          v-model="input"
          type="textarea"
          rows="4"
          placeholder="例如：妈转了一篇《十种致癌食物》给我…"
          autosize
          maxlength="2000"
          show-word-limit
          class="input-field"
        />
        <div class="mic" :class="{ recording: listening }" @click="toggleMic">
          <van-icon :name="listening ? 'pause-circle-o' : 'audio'" />
          <span>{{ listening ? '停止' : '说话' }}</span>
        </div>
      </div>
      <div class="mic-tip" v-if="listening">🎙 正在听你说…（说完点「停止」）</div>
      <div class="chips">
        <van-tag
          v-for="(c, i) in samples" :key="i"
          plain round color="#e8833a" size="medium"
          class="chip"
          @click="input = c"
        >示例{{ i + 1 }}</van-tag>
      </div>
      <div class="label" style="margin-top: 6px;">你的语气画像</div>
      <div class="tones">
        <div
          v-for="t in tones" :key="t.key"
          class="tone-chip"
          :class="{ active: tone === t.key }"
          @click="tone = t.key"
        >
          <div class="tone-emoji">{{ t.emoji }}</div>
          <div class="tone-name">{{ t.name }}</div>
          <div class="tone-desc">{{ t.desc }}</div>
        </div>
      </div>
      <van-button
        type="primary" round block class="gradient-btn"
        :loading="loading" loading-text="正在生成…"
        @click="generate"
      >生成 3 档回复</van-button>
    </div>

    <div v-if="result" class="result-wrap">
      <div class="result-head">
        <span>💬 家音建议你这样说</span>
        <span class="scene-tag" v-if="result.scene_name">{{ result.scene_name }}</span>
      </div>

      <div class="reply-card" v-for="r in replyList" :key="r.key">
        <div class="reply-head">
          <span class="reply-emoji">{{ r.emoji }}</span>
          <span class="reply-name">{{ r.name }}</span>
          <span class="reply-tag" v-if="tone === r.key">· 当前画像</span>
        </div>
        <div class="reply-body">{{ r.text }}</div>
        <div class="reply-actions">
          <van-button
            size="small" plain round
            :type="speakingKey === r.key ? 'danger' : 'default'"
            @click="speak(r.text, r.key)"
          >
            <van-icon :name="speakingKey === r.key ? 'pause-circle-o' : 'volume-o'" />&nbsp;{{ speakingKey === r.key ? '停止' : '朗读' }}
          </van-button>
          <van-button size="small" plain round @click="copy(r.text, r.name)">
            <van-icon name="copy" />&nbsp;一键复制
          </van-button>
        </div>
      </div>

      <div class="next-step">
        <span>复制好了，还是不敢发 / 怕打电话说不顺？</span>
        <span class="next-link" @click="goRehearsal">去彩排室练一遍 →</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import { profileSummary } from '../store/profile'
import { addRecord } from '../store/history'
import { gain } from '../store/pet'
import { useRecognition, useSpeaker } from '../composables/useSpeech'
import { apiUrl } from '../api'

const router = useRouter()
const input = ref('')
const { listening, toggle: toggleMic } = useRecognition(input)
const { speakingKey, speak } = useSpeaker()
const tone = ref('normal')
const loading = ref(false)
const result = ref(null)

const samples = [
  '震惊！《十种致癌食物，年轻人天天在吃！》你天天点外卖，奶茶当水喝，我看了整晚睡不着，转给你看看，千万要注意啊！',
  '儿子，我今天去菜市场看到你爱吃的排骨想了半天买没买，你爸说等你中秋回来再买新鲜的。你工作最近忙不忙？',
  '妈问你钱够不够花，别省着，想吃啥吃点好的。你对象的事呢？有没有合适的？'
]

const tones = [
  { key: 'tough',  emoji: '😎', name: '嘴硬', desc: '轻描淡写，但让爸妈安心' },
  { key: 'normal', emoji: '🙂', name: '标准', desc: '温和得体，给具体细节' },
  { key: 'sweet',  emoji: '🥺', name: '撒娇', desc: '情感外露，会用 ❤️' }
]

const replyMeta = [
  { key: 'tough',  emoji: '😎', name: '嘴硬档' },
  { key: 'normal', emoji: '🙂', name: '标准档' },
  { key: 'sweet',  emoji: '🥺', name: '撒娇档' }
]

const replyList = computed(() => {
  if (!result.value) return []
  return replyMeta.map(m => ({
    ...m,
    text: (result.value.replies && result.value.replies[m.key]) || ''
  }))
})

onMounted(() => {
  // 从解码器一键跳转：携带原文预填
  const c = router.currentRoute.value.query.c
  if (c) input.value = String(c).slice(0, 2000)
})

function goRehearsal() {
  router.push('/rehearsal')
}

async function generate() {
  if (!input.value.trim()) { showToast('先把内容贴进来吧'); return }
  loading.value = true
  result.value = null
  try {
    const res = await fetch(apiUrl('/api/reply'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: input.value, tone: tone.value, profile: profileSummary() })
    })
    if (!res.ok) throw new Error()
    result.value = await res.json()
    addRecord('reply', result.value.replies?.normal || result.value.scene_name, result.value)
    const g = gain('reply')
    if (g?.levelUp) showToast(`家里的宠物长大成「${g.stage}」啦 🎉`)
  } catch {
    showToast('生成失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

async function copy(text, name) {
  if (!text) { showToast('该档暂无文案'); return }
  try {
    await navigator.clipboard.writeText(text)
    showSuccessToast(`${name}已复制`)
  } catch {
    // 兜底：旧浏览器/非安全上下文
    const ta = document.createElement('textarea')
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    showSuccessToast(`${name}已复制`)
  }
}
</script>

<style scoped>
.label {
  font-size: 12px;
  color: var(--jiayin-text-light);
  margin: 0 0 8px;
}
.chips { margin: 10px 0 14px; display: flex; flex-wrap: wrap; gap: 8px; }
.chip { cursor: pointer; }

.input-row { display: flex; gap: 8px; align-items: flex-start; }
.input-field { flex: 1; background: #faf6f0; border-radius: 10px; }
.mic {
  flex-shrink: 0;
  width: 52px;
  border: 1.5px solid #f0e2cf;
  border-radius: 12px;
  padding: 8px 0;
  text-align: center;
  cursor: pointer;
  font-size: 11px;
  color: var(--jiayin-text-light);
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  transition: all .15s ease;
}
.mic .van-icon { font-size: 22px; }
.mic.recording {
  border-color: #e64340;
  color: #e64340;
  background: #fdf0ef;
  animation: micPulse 1.2s infinite;
}
@keyframes micPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(230, 67, 64, 0.25); }
  50% { box-shadow: 0 0 0 6px rgba(230, 67, 64, 0); }
}
.mic-tip { font-size: 12px; color: #e64340; margin: 6px 2px 0; }

.tones {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
}
.tone-chip {
  flex: 1;
  border: 1.5px solid #f0e2cf;
  border-radius: 12px;
  padding: 10px 6px;
  text-align: center;
  cursor: pointer;
  background: #fff;
  transition: all .15s ease;
}
.tone-chip.active {
  border-color: var(--jiayin-primary);
  background: #fdf1e3;
}
.tone-chip:active { opacity: .85; }
.tone-emoji { font-size: 22px; line-height: 1; }
.tone-name { font-size: 13px; font-weight: 600; margin-top: 4px; }
.tone-desc { font-size: 11px; color: var(--jiayin-text-light); margin-top: 2px; line-height: 1.4; }

.result-wrap { margin-top: 4px; }
.result-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 700;
  font-size: 15px;
  margin: 6px 4px 10px;
}
.scene-tag {
  font-size: 11px;
  font-weight: 500;
  color: var(--jiayin-primary-deep);
  background: #fdf1e3;
  padding: 3px 8px;
  border-radius: 999px;
}

.reply-card {
  background: var(--jiayin-card);
  border-radius: 14px;
  padding: 14px 14px 10px;
  margin-bottom: 12px;
  box-shadow: 0 2px 10px rgba(61, 47, 36, 0.06);
}
.reply-head {
  display: flex;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}
.reply-emoji { margin-right: 6px; font-size: 16px; }
.reply-tag {
  margin-left: 6px;
  font-size: 11px;
  font-weight: 500;
  color: var(--jiayin-primary-deep);
  background: #fdf1e3;
  padding: 2px 7px;
  border-radius: 999px;
}
.reply-body {
  font-size: 14px;
  line-height: 1.75;
  color: var(--jiayin-text);
  background: #faf6f0;
  border-radius: 10px;
  padding: 10px 12px;
  white-space: pre-wrap;
  word-break: break-word;
}
.reply-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.next-step {
  margin: 4px 2px 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  color: var(--jiayin-text-light);
}
.next-link {
  color: var(--jiayin-primary-deep);
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}
</style>