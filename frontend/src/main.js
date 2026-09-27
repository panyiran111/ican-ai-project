import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import Vant from 'vant'
import 'vant/lib/index.css'
import './style.css'
import App from './App.vue'

const routes = [
  { path: '/', name: 'home', component: () => import('./views/HomeView.vue'), meta: { title: '家音' } },
  { path: '/decode', name: 'decode', component: () => import('./views/DecodeView.vue'), meta: { title: '关心解码器' } },
  { path: '/reply', name: 'reply', component: () => import('./views/ReplyView.vue'), meta: { title: '回音壁' } },
  { path: '/rehearsal', name: 'rehearsal', component: () => import('./views/RehearsalView.vue'), meta: { title: '彩排室' } },
  { path: '/topic', name: 'topic', component: () => import('./views/TopicView.vue'), meta: { title: '连心话题卡' } },
  { path: '/checkin', name: 'checkin', component: () => import('./views/CheckinView.vue'), meta: { title: '安心打卡' } },
  { path: '/pet', name: 'pet', component: () => import('./views/PetView.vue'), meta: { title: '合养小宠物' } }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.use(Vant)
app.mount('#app')
