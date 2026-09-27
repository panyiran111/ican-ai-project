<template>
  <div class="page">
    <div class="page-title">关心解码器</div>
    <div class="page-sub">把爸妈的养生文、60 秒语音（转文字后）贴进来，看看背后藏着的关心。</div>

    <div class="card">
      <div class="input-row">
        <van-field
          v-model="input"
          type="textarea"
          rows="5"
          placeholder="例如：转发的《十种致癌食物，千万别再吃了！》全文…"
          autosize
          maxlength="2000"
          show-word-limit
          class="input-field"
        />
        <div
          class="mic"
          :class="{ recording: listening }"
          @click="toggleMic"
        >
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
      <van-button
        type="primary" round block class="gradient-btn"
        :loading="loading" loading-text="正在解码…"
        @click="decode"
      >翻译这份关心</van-button>
    </div>

    <div v-if="result" class="card result">
      <div class="result-head">💛 解码结果</div>
      <div class="result-block">
        <div class="block-label">她真正想说的（核心信息压缩）</div>
        <div class="block-body">{{ result.core }}</div>
      </div>
      <div class="result-block">
        <div class="block-label">言外之意（情感解码）</div>
        <div class="block-body highlight">{{ result.emotion }}</div>
      </div>
      <div class="result-block" v-if="result.intent">
        <div class="block-label">建议你回应的点</div>
        <div class="block-body">{{ result.intent }}</div>
      </div>
      <div class="risk" v-if="result.risk_level">
        内容可信度提示：{{ result.risk_note }}
      </div>
      <van-button
        round block plain type="primary" class="go-reply"
        @click="goReply"
      >💬 听懂了，去回音壁生成回复 →</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { profileSummary } from '../store/profile'
import { addRecord } from '../store/history'
import { useRecognition } from '../composables/useSpeech'
import { apiUrl } from '../api'

const router = useRouter()
const input = ref('')
const { listening, toggle: toggleMic } = useRecognition(input)
const loading = ref(false)
const result = ref(null)

const samples = [
  '震惊！《十种致癌食物，年轻人天天在吃！》你天天点外卖，奶茶当水喝，我看了整晚睡不着，转给你看看，千万要注意啊！',
  '儿子，我今天去菜市场看到你爱吃的排骨想了半天买没买，你爸说等你中秋回来再买新鲜的。你工作最近忙不忙？我看你朋友圈凌晨两点还在发东西，别老熬夜，胃药我给你寄了两盒在抽屉里。',
  '早上好！天冷了记得加衣服。这个养生讲座的王教授说得特别好，我每天早上五点起来听，你要是能一起听就好了。你中秋到底回不回家？你爸嘴上不说，天天在日历上画圈。'
]

async function decode() {
  if (!input.value.trim()) { showToast('先把内容贴进来吧'); return }
  loading.value = true
  result.value = null
  try {
    const res = await fetch(apiUrl('/api/decode'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: input.value, profile: profileSummary() })
    })
    if (!res.ok) throw new Error()
    result.value = await res.json()
    addRecord('decode', result.value.core, result.value)
  } catch {
    showToast('解码失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

function goReply() {
  router.push({ path: '/reply', query: { c: input.value } })
}
</script>

<style scoped>
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
.result-head { font-weight: 700; font-size: 16px; margin-bottom: 12px; }
.result-block { margin-bottom: 12px; }
.block-label { font-size: 11px; color: var(--jiayin-text-light); margin-bottom: 4px; }
.block-body { font-size: 14px; line-height: 1.7; }
.block-body.highlight {
  background: #fdf1e3;
  border-radius: 10px;
  padding: 10px 12px;
  color: var(--jiayin-primary-deep);
  font-weight: 500;
}
.risk {
  font-size: 12px;
  color: var(--jiayin-text-light);
  background: #faf6f0;
  border-radius: 8px;
  padding: 8px 10px;
  line-height: 1.6;
}
.go-reply { margin-top: 4px; font-weight: 600; }
</style>
