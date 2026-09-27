<template>
  <div class="page">
    <div class="page-title">高难对话彩排室</div>
    <div class="page-sub">挂科了、要生活费、想辞职……先和 AI 版爸妈练一遍，练顺了再打那个电话。</div>

    <!-- 场景选择 -->
    <div class="card" v-if="!started">
      <div class="label">这次要开口说什么？</div>
      <div class="scenes">
        <div
          v-for="s in scenes" :key="s.key"
          class="scene-chip"
          :class="{ active: scene === s.key }"
          @click="scene = s.key"
        >
          <div class="scene-emoji">{{ s.emoji }}</div>
          <div class="scene-name">{{ s.name }}</div>
          <div class="scene-desc">对{{ s.parent }}说</div>
        </div>
      </div>
      <van-button
        type="primary" round block class="gradient-btn"
        :loading="loading" loading-text="正在接通…"
        @click="start"
      >🎬 开始彩排</van-button>
      <div class="tips">💡 AI 爸妈会先起话头，你只要顺着把心里话说出来就行，说砸了可以随时重来。</div>
    </div>

    <!-- 聊天界面 -->
    <template v-if="started">
      <div class="chat-head">
        <span class="chat-title">{{ meta.parentEmoji }} {{ meta.parent }} · 彩排中</span>
        <span class="chat-scene">{{ meta.sceneName }}</span>
        <van-button size="small" plain round class="restart-btn" @click="restart">↺ 换场景重来</van-button>
      </div>

      <div class="chat-box card" ref="chatBox">
        <div
          v-for="(m, i) in messages" :key="i"
          class="msg-row" :class="m.role === 'user' ? 'mine' : 'theirs'"
        >
          <div class="avatar" v-if="m.role !== 'user'">{{ meta.parentEmoji }}</div>
          <div class="bubble">{{ m.content }}</div>
        </div>
        <div v-if="thinking" class="msg-row theirs">
          <div class="avatar">{{ meta.parentEmoji }}</div>
          <div class="bubble typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="input-bar card">
        <van-field
          v-model="draft" rows="1" autosize type="textarea"
          placeholder="试着把这句话说出口…"
          maxlength="500" class="input-field"
          @keydown.enter.exact.prevent="send"
        />
        <van-button
          type="primary" round class="send-btn" :loading="thinking"
          loading-text="…" @click="send"
        >发送</van-button>
      </div>

      <div class="tips">💡 彩排没有输赢：说得磕磕绊绊也没关系，多来几轮就顺了。</div>
    </template>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { showToast } from 'vant'
import { addRecord } from '../store/history'
import { apiUrl } from '../api'

const scenes = [
  { key: 'fail_exam',  emoji: '📚', name: '挂科了',     parent: '妈妈' },
  { key: 'breakup',    emoji: '💔', name: '分手了',     parent: '妈妈' },
  { key: 'quit_job',   emoji: '💼', name: '想辞职',     parent: '爸爸' },
  { key: 'money_short',emoji: '💰', name: '生活费不够', parent: '妈妈' }
]

const scene = ref('fail_exam')
const started = ref(false)
const loading = ref(false)
const thinking = ref(false)
const sessionId = ref('')
const draft = ref('')
const messages = ref([])
const chatBox = ref(null)

const meta = ref({ sceneName: '', parent: '', parentEmoji: '👩' })

async function start() {
  loading.value = true
  try {
    const res = await fetch(apiUrl('/api/rehearsal/start'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scene: scene.value })
    })
    if (!res.ok) throw new Error()
    const data = await res.json()
    sessionId.value = data.session_id
    meta.value = {
      sceneName: data.scene_name,
      parent: data.parent,
      parentEmoji: data.parent_emoji || '👩'
    }
    messages.value = [{ role: 'assistant', content: data.opening }]
    started.value = true
    scrollToBottom()
  } catch {
    showToast('接通失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

async function send() {
  const text = draft.value.trim()
  if (!text) { showToast('先输入想说的话'); return }
  if (thinking.value) return
  draft.value = ''
  messages.value.push({ role: 'user', content: text })
  thinking.value = true
  scrollToBottom()
  try {
    const res = await fetch(apiUrl('/api/rehearsal/chat'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId.value, content: text })
    })
    if (!res.ok) throw new Error()
    const data = await res.json()
    messages.value.push({ role: 'assistant', content: data.reply })
    if (data.turn === 3) {
      addRecord('rehearsal', `和 AI${meta.value.parent}练了「${meta.value.sceneName}」，练到第 3 轮`, { scene: meta.value.sceneName })
    }
  } catch {
    messages.value.push({ role: 'assistant', content: '（信号不好，刚才那句妈没听清，你再说一遍？）' })
  } finally {
    thinking.value = false
    scrollToBottom()
  }
}

function restart() {
  started.value = false
  messages.value = []
  sessionId.value = ''
  draft.value = ''
}

async function scrollToBottom() {
  await nextTick()
  if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
}
</script>

<style scoped>
.label {
  font-size: 12px;
  color: var(--jiayin-text-light);
  margin: 0 0 8px;
}

.scenes {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 14px;
}
.scene-chip {
  border: 1.5px solid #f0e2cf;
  border-radius: 12px;
  padding: 10px 8px;
  text-align: center;
  cursor: pointer;
  background: #fff;
  transition: all .15s ease;
}
.scene-chip.active {
  border-color: var(--jiayin-primary);
  background: #fdf1e3;
}
.scene-chip:active { opacity: .85; }
.scene-emoji { font-size: 22px; line-height: 1; }
.scene-name { font-size: 13px; font-weight: 600; margin-top: 4px; }
.scene-desc { font-size: 11px; color: var(--jiayin-text-light); margin-top: 2px; }

.chat-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 4px 4px 10px;
  font-weight: 700;
  font-size: 15px;
}
.chat-scene {
  font-size: 11px;
  font-weight: 500;
  color: var(--jiayin-primary-deep);
  background: #fdf1e3;
  padding: 3px 8px;
  border-radius: 999px;
}
.restart-btn {
  margin-left: auto;
  flex-shrink: 0;
  font-size: 12px;
}

.chat-box {
  padding: 12px;
  min-height: 300px;
  max-height: 46vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.msg-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.msg-row.mine {
  justify-content: flex-end;
}
.avatar {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #fdf1e3;
  border: 1px solid #f0e2cf;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.bubble {
  max-width: 78%;
  padding: 9px 12px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.65;
  word-break: break-word;
  white-space: pre-wrap;
  animation: popIn .22s ease both;
}
@keyframes popIn {
  from { opacity: 0; transform: translateY(6px) scale(.97); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.theirs .bubble {
  background: #faf6f0;
  color: var(--jiayin-text);
  border-top-left-radius: 4px;
}
.mine .bubble {
  background: linear-gradient(135deg, var(--jiayin-primary), var(--jiayin-primary-deep));
  color: #fff;
  border-top-right-radius: 4px;
}

.typing {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 13px 14px;
}
.typing span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c9a06c;
  animation: blink 1.2s infinite both;
}
.typing span:nth-child(2) { animation-delay: .2s; }
.typing span:nth-child(3) { animation-delay: .4s; }
@keyframes blink {
  0%, 80%, 100% { opacity: .25; }
  40% { opacity: 1; }
}

.input-bar {
  margin-top: 10px;
  padding: 8px;
  display: flex;
  align-items: flex-end;
  gap: 8px;
}
.input-field {
  flex: 1;
  background: #faf6f0;
  border-radius: 10px;
  padding: 4px 2px;
}
.send-btn {
  flex-shrink: 0;
  height: 36px;
  padding: 0 16px;
}

.tips {
  font-size: 12px;
  color: var(--jiayin-text-light);
  text-align: center;
  margin: 12px 4px 4px;
  line-height: 1.6;
}
</style>
