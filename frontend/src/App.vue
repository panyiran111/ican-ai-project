<template>
  <div class="app-shell">
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>

    <van-tabbar route fixed placeholder safe-area-inset-bottom active-color="#e8833a">
      <van-tabbar-item replace to="/" icon="wap-home-o">家音</van-tabbar-item>
      <van-tabbar-item replace to="/decode" icon="volume-o">解码</van-tabbar-item>
      <van-tabbar-item replace to="/reply" icon="chat-o">回音</van-tabbar-item>
      <van-tabbar-item replace to="/rehearsal" icon="friends-o">彩排</van-tabbar-item>
      <van-tabbar-item replace to="/topic" icon="notes-o">话题</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}
</style>
