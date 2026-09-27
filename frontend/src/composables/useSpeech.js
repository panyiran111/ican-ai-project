/**
 * 语音能力组合式函数（Web Speech API，Chrome/Edge 原生支持）
 * - useRecognition：说话 → 文字（zh-CN），实时追加到目标 ref
 * - useSpeaker：文字 → 朗读（带播放/停止切换）
 * 不支持的浏览器自动降级：调用时弹 toast 提示
 */
import { ref, onBeforeUnmount } from 'vue'
import { showToast } from 'vant'

/* ---------------- 语音识别（听写） ---------------- */

export function useRecognition(target, { append = false } = {}) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  const listening = ref(false)
  let recog = null

  function toggle() {
    if (listening.value) { stop(); return }
    start()
  }

  function start() {
    if (!SR) {
      showToast('当前浏览器不支持语音输入，建议用 Chrome / Edge')
      return
    }
    recog = new SR()
    recog.lang = 'zh-CN'
    recog.continuous = true
    recog.interimResults = true

    let finalText = append ? (target.value || '') : ''

    recog.onresult = e => {
      let interim = ''
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const r = e.results[i]
        if (r.isFinal) finalText += r[0].transcript
        else interim += r[0].transcript
      }
      target.value = finalText + interim
    }
    recog.onerror = ev => {
      listening.value = false
      if (ev.error === 'not-allowed') showToast('麦克风权限被拒绝，请在浏览器设置中允许')
      else if (ev.error !== 'aborted') showToast('没听清，再试一次？')
    }
    recog.onend = () => { listening.value = false }

    try { recog.start(); listening.value = true } catch { /* 重复启动忽略 */ }
  }

  function stop() {
    if (recog) { try { recog.stop() } catch { /* 忽略 */ } }
    listening.value = false
  }

  onBeforeUnmount(stop)
  return { listening, toggle, stop }
}

/* ---------------- 语音合成（朗读） ---------------- */

export function useSpeaker() {
  const speakingKey = ref('') // 正在朗读的条目 key，用于按钮态

  function speak(text, key = 'default') {
    if (!('speechSynthesis' in window)) {
      showToast('当前浏览器不支持朗读，建议用 Chrome / Edge')
      return
    }
    if (speakingKey.value === key) { stop(); return }
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    u.lang = 'zh-CN'
    u.rate = 1.0
    u.onend = () => { speakingKey.value = '' }
    u.onerror = () => { speakingKey.value = '' }
    speakingKey.value = key
    window.speechSynthesis.speak(u)
  }

  function stop() {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel()
    speakingKey.value = ''
  }

  onBeforeUnmount(stop)
  return { speakingKey, speak, stop }
}

/** 环境是否支持语音输入（用于 UI 上隐藏麦克风按钮） */
export function recognitionSupported() {
  return Boolean(window.SpeechRecognition || window.webkitSpeechRecognition)
}
