<template>
  <van-popup v-model:show="show" position="bottom" round :style="{ maxHeight: '82vh' }" class="profile-popup">
    <div class="popup-head">
      <div class="popup-title">👨‍👩‍👧 我家的小档案</div>
      <div class="popup-sub">填一次，之后生成的每句话都带上你家的味道（存在本机，不会上传）</div>
    </div>

    <div class="form">
      <div class="field-row">
        <van-field v-model="form.mom_call" label="怎么叫妈妈" placeholder="妈 / 老妈 / 母上" />
        <van-field v-model="form.dad_call" label="怎么叫爸爸" placeholder="爸 / 老爸" />
      </div>
      <van-field v-model="form.hometown" label="老家" placeholder="如：山东济南" />
      <van-field v-model="form.mom_dish" label="妈妈拿手菜" placeholder="如：红烧排骨" />
      <van-field v-model="form.dad_hobby" label="爸爸的爱好" placeholder="如：下象棋 / 钓鱼" />
      <van-field v-model="form.pet" label="家里的猫狗" placeholder="如：橘猫胖虎（没有就不填）" />

      <van-button type="primary" round block class="gradient-btn" style="margin-top: 14px" @click="save">
        保存档案
      </van-button>
      <div class="empty-link" v-if="!isEmpty" @click="clear">清空档案</div>
    </div>
  </van-popup>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { showSuccessToast } from 'vant'
import { getProfile, saveProfile, emptyProfile, isProfileEmpty } from '../store/profile'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue', 'saved'])

const show = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v)
})

const form = reactive({ ...emptyProfile })
const isEmpty = ref(true)

watch(show, v => {
  if (v) {
    Object.assign(form, getProfile())
    isEmpty.value = isProfileEmpty()
  }
})

function save() {
  saveProfile({ ...form })
  isEmpty.value = isProfileEmpty()
  showSuccessToast(isEmpty.value ? '已保存（还是空的哦）' : '档案已保存，生成内容会更懂你家')
  emit('saved')
  show.value = false
}

function clear() {
  Object.assign(form, emptyProfile)
  saveProfile({ ...emptyProfile })
  isEmpty.value = true
  showSuccessToast('已清空')
  emit('saved')
  show.value = false
}
</script>

<style scoped>
.popup-head { padding: 18px 18px 6px; }
.popup-title { font-size: 17px; font-weight: 700; }
.popup-sub { font-size: 12px; color: var(--jiayin-text-light); margin-top: 4px; line-height: 1.6; }
.form { padding: 8px 12px 24px; overflow-y: auto; }
.field-row { display: flex; }
.field-row :deep(.van-field) { flex: 1; }
.empty-link {
  text-align: center;
  font-size: 12px;
  color: var(--jiayin-text-light);
  margin-top: 12px;
  cursor: pointer;
}
</style>
