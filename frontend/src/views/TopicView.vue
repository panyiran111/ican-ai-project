<template>
  <div class="page">
    <div class="page-title">连心话题卡</div>
    <div class="page-sub">打电话前抽 5 张话题卡，让"吃了吗"之后还有话聊。</div>

    <div class="card">
      <div class="label">这次通话是什么场景？</div>
      <div class="scenes">
        <div
          v-for="s in scenes" :key="s.key"
          class="scene-chip"
          :class="{ active: scene === s.key }"
          @click="scene = s.key"
        >
          <div class="scene-emoji">{{ s.emoji }}</div>
          <div class="scene-name">{{ s.name }}</div>
          <div class="scene-desc">{{ s.desc }}</div>
        </div>
      </div>
      <van-button
        type="primary" round block class="gradient-btn"
        :loading="loading" loading-text="正在抽卡…"
        @click="draw"
      >🎴 抽 5 张话题</van-button>
    </div>

    <div v-if="result" class="result-wrap">
      <div class="result-head">
        <span>💬 这次可以这么聊</span>
        <span class="scene-tag">{{ result.scene_name }}</span>
      </div>

      <div
        v-for="(t, i) in result.topics" :key="i"
        class="topic-card"
        :style="{ animationDelay: (i * 0.12) + 's' }"
      >
        <div class="topic-front">
          <div class="topic-no">{{ i + 1 }}</div>
          <div class="topic-text">{{ t }}</div>
          <div class="topic-actions">
            <van-button size="small" plain round @click="copy(t, '话题' + (i + 1))">
              <van-icon name="copy" />&nbsp;复制
            </van-button>
          </div>
        </div>
      </div>

      <div class="tips">
        💡 小技巧：一次用一张就够，爸妈聊开了就顺着往下聊。
        还没想好怎么开口？<span class="link" @click="goRehearsal">去彩排室练一遍 →</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import { profileSummary } from '../store/profile'
import { addRecord } from '../store/history'
import { gain } from '../store/pet'
import { apiUrl } from '../api'

const router = useRouter()
const scene = ref('before_home')
const loading = ref(false)
const result = ref(null)

const scenes = [
  { key: 'before_home', emoji: '🏠', name: '回家前', desc: '买好票，通话预热' },
  { key: 'festival',    emoji: '🥮', name: '节日',  desc: '中秋/春节/端午' },
  { key: 'birthday',    emoji: '🎂', name: '生日',  desc: '爸妈或自己生日' },
  { key: 'daily',       emoji: '📞', name: '普通通话', desc: '日常问候不尬聊' }
]

function goRehearsal() {
  router.push('/rehearsal')
}

async function draw() {
  loading.value = true
  result.value = null
  try {
    const res = await fetch(apiUrl('/api/topic'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scene: scene.value, profile: profileSummary() })
    })
    if (!res.ok) throw new Error()
    result.value = await res.json()
    addRecord('topic', `【${result.value.scene_name}】${result.value.topics?.[0] || ''}`, result.value)
    const g = gain('topic')
    if (g?.levelUp) showToast(`家里的宠物长大成「${g.stage}」啦 🎉`)
  } catch {
    showToast('抽卡失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

async function copy(text, name) {
  if (!text) { showToast('该话题暂无内容'); return }
  try {
    await navigator.clipboard.writeText(text)
    showSuccessToast(`${name}已复制`)
  } catch {
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
.scene-desc { font-size: 11px; color: var(--jiayin-text-light); margin-top: 2px; line-height: 1.4; }

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

.topic-card {
  background: var(--jiayin-card);
  border-radius: 14px;
  padding: 12px 14px 8px;
  margin-bottom: 10px;
  box-shadow: 0 2px 10px rgba(61, 47, 36, 0.06);
  animation: flipIn .5s ease both;
}
@keyframes flipIn {
  from {
    opacity: 0;
    transform: perspective(600px) rotateX(35deg) translateY(14px);
  }
  to {
    opacity: 1;
    transform: perspective(600px) rotateX(0) translateY(0);
  }
}
.topic-front {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.topic-no {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--jiayin-primary), var(--jiayin-primary-deep));
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
}
.topic-text {
  flex: 1;
  font-size: 14px;
  line-height: 1.7;
  color: var(--jiayin-text);
  word-break: break-word;
}
.topic-actions {
  flex-shrink: 0;
  align-self: flex-end;
}

.tips {
  font-size: 12px;
  color: var(--jiayin-text-light);
  text-align: center;
  margin: 14px 4px 4px;
  line-height: 1.6;
}
.tips .link {
  color: var(--jiayin-primary-deep);
  font-weight: 600;
  cursor: pointer;
}
</style>
