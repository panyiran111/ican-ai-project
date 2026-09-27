<template>
  <div class="page">
    <div class="page-title">合养小宠物</div>
    <div class="page-sub">它是「全家的孩子」：你每次和爸妈好好说话，它就长大一点。把它的近况发给爸妈，就是一段现成的话题。</div>

    <!-- 未领养 -->
    <div class="card" v-if="!pet.adopted">
      <div class="label">接一只回家吧（起个名字，全家一起养）</div>
      <div class="type-row">
        <div
          v-for="t in types" :key="t.key"
          class="type-chip" :class="{ active: form.type === t.key }"
          @click="form.type = t.key"
        >
          <div class="type-emoji">{{ t.emoji }}</div>
          <div class="type-name">{{ t.name }}</div>
        </div>
      </div>
      <van-field
        v-model="form.name" placeholder="给它起个名字，比如：团圆 / 汤圆 / 旺财"
        maxlength="12" class="name-field"
      />
      <van-button type="primary" round block class="gradient-btn" @click="adopt">
        🏠 接它回家
      </van-button>
      <div class="tips">💡 领养后：解码 +5 / 回音 +5 / 话题 +3 / 彩排 +10 / 打卡 +10 成长值，喂食每天一次 +5。</div>
    </div>

    <!-- 已领养 -->
    <template v-else>
      <div class="card pet-card">
        <div class="pet-stage">{{ stage.name }}</div>
        <div class="pet-emoji" :class="{ jump: justFed }">{{ emoji }}</div>
        <div class="pet-name">{{ pet.name }}</div>
        <div class="pet-desc">{{ stage.desc }}</div>

        <div class="grow-head">
          <span>成长值 {{ pet.growth }}</span>
          <span v-if="next">{{ next.name }} 还差 {{ next.min - pet.growth }}</span>
          <span v-else>已是最终的「家人」形态 🏆</span>
        </div>
        <div class="grow-bar">
          <div class="grow-fill" :style="{ width: progress + '%' }"></div>
        </div>

        <div class="actions">
          <van-button
            size="small" round :type="fed ? 'default' : 'primary'" plain
            :disabled="fed" @click="doFeed"
          >🍚 {{ fed ? '今天喂过了' : '喂它一顿' }}</van-button>
          <van-button size="small" round type="primary" plain @click="share">
            💬 分享给爸妈
          </van-button>
        </div>
      </div>

      <div class="card" v-if="pet.events.length">
        <div class="label">成长日志</div>
        <div class="event" v-for="(e, i) in pet.events" :key="e.time + '-' + i">
          <span class="event-text">{{ e.text }}</span>
          <span class="event-time">{{ fmtTime(e.time) }}</span>
        </div>
      </div>

      <div class="tips">
        💡 它不只是个游戏：分享按钮会生成一段现成的话，复制发给爸妈，
        聊着聊着话就多了。断喂不惩罚，它一直都在。
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import {
  getPet, adoptPet, feed, fedToday, stageOf, nextStage,
  typeEmoji, typeName, shareText, PET_TYPES,
} from '../store/pet'

const types = PET_TYPES
const pet = ref(getPet())
const form = ref({ name: '', type: 'cat' })
const fed = ref(fedToday())
const justFed = ref(false)

const emoji = computed(() => typeEmoji(pet.value))
const stage = computed(() => stageOf(pet.value.growth))
const next = computed(() => nextStage(pet.value.growth))
const progress = computed(() => {
  if (!next.value) return 100
  const cur = stage.value.min
  return Math.min(100, Math.round(((pet.value.growth - cur) / (next.value.min - cur)) * 100))
})

onMounted(() => { pet.value = getPet() })

function adopt() {
  if (!form.value.name.trim()) { showToast('先给它起个名字吧'); return }
  pet.value = adoptPet(form.value.name, form.value.type)
  fed.value = false
  showSuccessToast(`${pet.value.name} 来到我们家啦！`)
}

function doFeed() {
  const r = feed()
  if (!r.fed) return
  pet.value = getPet()
  fed.value = true
  justFed.value = true
  setTimeout(() => { justFed.value = false }, 900)
  showSuccessToast(r.levelUp ? `吃饱了，还长大成了「${stageOf(pet.value.growth).name}」！` : '吃得津津有味 +5')
}

async function share() {
  const text = shareText()
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    const ta = document.createElement('textarea')
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
  }
  showSuccessToast('已复制，去发给爸妈吧')
}

function fmtTime(ts) {
  const d = new Date(ts)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${d.getMonth() + 1}月${d.getDate()}日 ${hh}:${mm}`
}
</script>

<style scoped>
.label { font-size: 12px; color: var(--jiayin-text-light); margin: 0 0 8px; }
.tips {
  font-size: 12px; color: var(--jiayin-text-light);
  text-align: center; margin: 14px 4px 4px; line-height: 1.7;
}

.type-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 12px; }
.type-chip {
  border: 1.5px solid #f0e2cf; border-radius: 12px; padding: 10px 6px;
  text-align: center; cursor: pointer; background: #fff; transition: all .15s ease;
}
.type-chip.active { border-color: var(--jiayin-primary); background: #fdf1e3; }
.type-emoji { font-size: 26px; line-height: 1; }
.type-name { font-size: 12px; font-weight: 600; margin-top: 4px; }
.name-field { background: #faf6f0; border-radius: 10px; margin-bottom: 12px; }

.pet-card { text-align: center; padding: 22px 16px 18px; }
.pet-stage {
  display: inline-block; font-size: 11px; font-weight: 600;
  color: var(--jiayin-primary-deep); background: #fdf1e3;
  padding: 3px 10px; border-radius: 999px; margin-bottom: 8px;
}
.pet-emoji { font-size: 72px; line-height: 1.15; }
.pet-emoji.jump { animation: petJump .8s ease; }
@keyframes petJump {
  0% { transform: scale(1); }
  35% { transform: scale(1.18) rotate(-6deg); }
  70% { transform: scale(1.05) rotate(4deg); }
  100% { transform: scale(1); }
}
.pet-name { font-size: 18px; font-weight: 700; margin-top: 6px; }
.pet-desc { font-size: 12px; color: var(--jiayin-text-light); margin-top: 4px; }

.grow-head {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 12px; color: var(--jiayin-text-light); margin: 16px 2px 6px;
}
.grow-bar { height: 10px; background: #f5ece0; border-radius: 999px; overflow: hidden; }
.grow-fill {
  height: 100%; border-radius: 999px;
  background: linear-gradient(90deg, var(--jiayin-primary), var(--jiayin-primary-deep));
  transition: width .6s ease;
}
.actions { display: flex; justify-content: center; gap: 10px; margin-top: 14px; }

.event {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 2px; border-bottom: 1px dashed #f0e6d8; font-size: 13px;
}
.event:last-child { border-bottom: none; }
.event-time { font-size: 11px; color: var(--jiayin-text-light); flex-shrink: 0; margin-left: 10px; }
</style>
