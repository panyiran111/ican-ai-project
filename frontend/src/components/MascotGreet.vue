<template>
  <div class="mascot-wrap">
    <!-- 角色切换 -->
    <div class="role-chips">
      <span
        class="role-chip" :class="{ active: role === 'parent' }"
        @click="setRole('parent')"
      >👨‍👩 我是爸妈</span>
      <span
        class="role-chip" :class="{ active: role === 'child' }"
        @click="setRole('child')"
      >🧑 我是你</span>
    </div>

    <div class="mascot-row">
      <!-- 迷你小人（纯 CSS，挥手 + 眨眼 + 摇摆） -->
      <div class="mascot" :class="{ excited }" @click="nextGreet">
        <div class="head">
          <span class="eye left"></span>
          <span class="eye right"></span>
          <span class="blush left"></span>
          <span class="blush right"></span>
          <span class="mouth"></span>
        </div>
        <div class="body"></div>
        <div class="arm left-arm"></div>
        <div class="arm right-arm wave"></div>
      </div>

      <!-- 气泡 -->
      <transition name="bubble" mode="out-in">
        <div class="bubble" key="b" @click="nextGreet">
          <div class="bubble-text">{{ greet }}</div>
          <div class="bubble-hint">点我再换一句 👋</div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getProfile } from '../store/profile'
import { checkedToday, streak as streakFn, getCheckins } from '../store/checkin'
import { getPet, stageOf, typeEmoji, isAdopted } from '../store/pet'

const ROLE_KEY = 'jiayin_role'
const role = ref(localStorage.getItem(ROLE_KEY) || 'child')
const idx = ref(0)
const excited = ref(false)

function setRole(r) {
  role.value = r
  localStorage.setItem(ROLE_KEY, r)
  idx.value = 0
  poke()
}

/** 真实动态驱动的问候池 */
const greets = computed(() => {
  const p = getProfile()
  const hour = new Date().getHours()
  const period = hour < 6 ? '夜深了' : hour < 11 ? '早上好' : hour < 14 ? '中午好' : hour < 18 ? '下午好' : '晚上好'
  const pet = getPet()
  const todayCheckin = getCheckins().find(c => {
    const d = new Date()
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    return c.day === key
  })

  if (role.value === 'parent') {
    const list = [
      `${period}，叔叔阿姨好呀！我是「家音」小助手，孩子请我来陪你们聊天～ 👋`,
      p.hometown ? `听说老家是${p.hometown}，那是个好地方！孩子跟我念叨过好多次～` : `孩子跟我念叨过好多次你们，说起来眼睛都是亮的～`,
      checkedToday()
        ? `悄悄告诉你们：孩子今天打卡报平安啦，还${todayCheckin?.note ? '写了句「' + todayCheckin.note + '」' : '拍了张照片'}，放心吧！❤️`
        : `孩子今天还没打卡，估计在忙—— TA 心里是有你们的，就是嘴上不说～`,
      isAdopted() && pet.adopted
        ? `你们家还合养了一只${typeEmoji(pet)}「${pet.name}」，已经是「${stageOf(pet.growth).name}」啦，孩子养得可上心了！`
        : `孩子有时候不是不想说话，是不知道怎么开口。多问问 TA 吃了啥、睡了没，TA 就打开了～`,
      `孩子转发给你们的消息都要好好看呀，那都是 TA 想你们的方式 😊`,
      `想孩子了就点下面的「连心话题卡」，我教你们打电话聊什么，保证不冷场！`,
    ]
    return list
  }
  const list = [
    `${period}！我是家音小助手，今天也要好好和爸妈说话哦 👋`,
    checkedToday()
      ? `你今天已经打过卡啦，${streakFn()} 天连续安心，爸妈那边踏实着呢 ☀️`
      : `今天还没打卡～拍一张今天的生活，让爸妈知道你很好？`,
    isAdopted() && pet.adopted
      ? `家里的${typeEmoji(pet)}「${pet.name}」饿了没？记得去喂它一顿～`
      : `要不要接一只小宠物回家？全家人一起养，话就多了～`,
    `爸妈的养生文不是谣言，是没说出口的想你。收到就贴进「解码器」看看～`,
    `快到节假日了，提前想好和爸妈聊什么，用「话题卡」抽 5 张备着吧 🎴`,
  ]
  return list
})

const greet = computed(() => greets.value[idx.value % greets.value.length])

function poke() {
  excited.value = true
  setTimeout(() => { excited.value = false }, 800)
}

function nextGreet() {
  idx.value++
  poke()
}

onMounted(() => poke())
</script>

<style scoped>
.mascot-wrap { margin: 12px 0 2px; }

.role-chips { display: flex; justify-content: center; gap: 8px; margin-bottom: 10px; }
.role-chip {
  font-size: 11px;
  padding: 4px 12px;
  border-radius: 999px;
  border: 1.5px solid #f0e2cf;
  color: var(--jiayin-text-light);
  background: #fff;
  cursor: pointer;
  transition: all .15s ease;
  user-select: none;
}
.role-chip.active {
  border-color: var(--jiayin-primary);
  color: var(--jiayin-primary-deep);
  background: #fdf1e3;
  font-weight: 600;
}

.mascot-row { display: flex; align-items: center; gap: 12px; }

/* ---------- 迷你小人 ---------- */
.mascot {
  flex-shrink: 0;
  width: 64px;
  height: 78px;
  position: relative;
  cursor: pointer;
  animation: bob 2.6s ease-in-out infinite;
}
@keyframes bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
.mascot.excited { animation: hop .5s ease 2; }
@keyframes hop {
  0%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
}

.head {
  position: absolute; top: 0; left: 50%;
  transform: translateX(-50%);
  width: 40px; height: 38px;
  background: linear-gradient(150deg, #ffd9a8, #f7b06a);
  border: 2px solid #e8a05c;
  border-radius: 50% 50% 46% 46%;
  z-index: 2;
}
.eye {
  position: absolute; top: 14px;
  width: 5px; height: 7px;
  background: #5a4632;
  border-radius: 50%;
  animation: blink 3.5s infinite;
}
.eye.left { left: 10px; }
.eye.right { right: 10px; }
@keyframes blink {
  0%, 92%, 100% { transform: scaleY(1); }
  95% { transform: scaleY(0.1); }
}
.blush {
  position: absolute; top: 21px;
  width: 6px; height: 4px;
  background: rgba(232, 100, 80, .35);
  border-radius: 50%;
}
.blush.left { left: 5px; }
.blush.right { right: 5px; }
.mouth {
  position: absolute; top: 23px; left: 50%;
  transform: translateX(-50%);
  width: 10px; height: 5px;
  border: 1.8px solid #5a4632;
  border-top: none;
  border-radius: 0 0 10px 10px;
}

.body {
  position: absolute; bottom: 0; left: 50%;
  transform: translateX(-50%);
  width: 34px; height: 34px;
  background: linear-gradient(160deg, var(--jiayin-primary), var(--jiayin-primary-deep, #d96a2b));
  border-radius: 12px 12px 8px 8px;
  z-index: 1;
}

.arm {
  position: absolute; top: 46px;
  width: 16px; height: 5px;
  background: #f7b06a;
  border-radius: 4px;
  z-index: 3;
}
.arm.left-arm { left: 2px; transform: rotate(18deg); }
.arm.right-arm {
  right: -6px;
  transform-origin: left center;
  animation: wave 1.1s ease-in-out infinite;
}
@keyframes wave {
  0%, 100% { transform: rotate(-30deg); }
  50% { transform: rotate(28deg); }
}

/* ---------- 气泡 ---------- */
.bubble {
  flex: 1;
  background: #fff;
  border: 1.5px solid #f2c79b;
  border-radius: 14px 14px 14px 4px;
  padding: 10px 12px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(61, 47, 36, .05);
  position: relative;
}
.bubble::before {
  content: '';
  position: absolute;
  left: -7px; top: 24px;
  width: 12px; height: 12px;
  background: #fff;
  border-left: 1.5px solid #f2c79b;
  border-bottom: 1.5px solid #f2c79b;
  transform: rotate(45deg);
}
.bubble-text { font-size: 13px; line-height: 1.65; color: var(--jiayin-text); }
.bubble-hint { font-size: 10px; color: var(--jiayin-text-light); margin-top: 4px; }

.bubble-enter-active, .bubble-leave-active { transition: all .25s ease; }
.bubble-enter-from { opacity: 0; transform: translateY(6px); }
.bubble-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
