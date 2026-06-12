<template>
  <header class="header">
    <div class="logo" @click="$router.push('/')">📘<span>科明365</span>VR教学云平台</div>
    <nav class="nav">
      <router-link
        v-for="item in navItems" :key="item.path"
        :to="item.path"
        :class="{ active: $route.path === item.path }"
      >{{ item.name }}</router-link>
    </nav>
    <div class="user" v-if="userStore.isLoggedIn">
      <div class="user-dropdown">
        <div class="avatar" @click.stop="showMenu = !showMenu">
          {{ (userStore.user?.name || userStore.user?.username || 'U').charAt(0).toUpperCase() }}
        </div>
        <div class="dropdown-menu" :class="{ show: showMenu }">
          <div class="dropdown-item" @click="goProfile">👤 个人中心</div>
          <div class="dropdown-item" v-if="userStore.user?.type === 2"
               @click="openAdmin">⚙️ 管理后台</div>
          <div class="dropdown-divider"></div>
          <div class="dropdown-item danger" @click="handleLogout">🚪 退出登录</div>
        </div>
      </div>
    </div>
    <div class="user" v-else>
      <router-link to="/login" class="btn btn-login">登录</router-link>
      <router-link to="/register" class="btn btn-reg">注册</router-link>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const showMenu = ref(false)

const navItems = [
  { path: '/', name: '首页' },
  { path: '/qbkc', name: '全部课程' },
  { path: '/xwzx', name: '新闻资讯' },
  { path: '/ptjj', name: '平台简介' },
  { path: '/zzch', name: '职教出海' },
  { path: '/about', name: '关于我们' },
]

const goProfile = () => { showMenu.value = false; router.push('/profile') }
const openAdmin = () => { showMenu.value = false; router.push('/admin') }

const handleLogout = () => {
  userStore.logout()
  showMenu.value = false
  router.push('/')
}

const closeMenu = (e: MouseEvent) => {
  if (!(e.target as HTMLElement).closest('.user-dropdown')) showMenu.value = false
}

onMounted(() => {
  document.addEventListener('click', closeMenu)
  if (userStore.token) userStore.fetchUser()
})
onUnmounted(() => document.removeEventListener('click', closeMenu))
</script>

<style lang="scss" scoped>
.header {
  background: linear-gradient(135deg, #1a237e, #283593);
  color: #fff; padding: 0 40px; height: 64px;
  display: flex; align-items: center;
  position: sticky; top: 0; z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,.2);
}
.logo {
  font-size: 20px; font-weight: 700; display: flex;
  align-items: center; gap: 10px; cursor: pointer;
  width: 200px; flex-shrink: 0;
  span { color: #64b5f6; }
}
.nav {
  display: grid; grid-template-columns: repeat(6, 1fr);
  width: 660px; font-size: 14px; text-align: center;
  position: absolute; left: 50%; transform: translateX(-50%);
  a {
    padding: 6px 0; border-bottom: 2px solid transparent;
    transition: .2s; color: #fff;
    &:hover, &.router-link-active, &.active { border-bottom-color: #64b5f6; color: #64b5f6; }
  }
}
.user {
  font-size: 14px; display: flex; align-items: center;
  gap: 12px; margin-left: auto;
}
.btn {
  padding: 6px 16px; border-radius: 20px; font-size: 13px;
  cursor: pointer; color: #fff;
}
.btn-login { background: #64b5f6; border: none; &:hover { background: #42a5f5; } }
.btn-reg { border: 1px solid rgba(255,255,255,.6); background: transparent; &:hover { border-color: #fff; } }
.user-dropdown { position: relative; display: inline-block; }
.avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: #64b5f6; color: #fff; display: flex;
  align-items: center; justify-content: center;
  font-size: 16px; font-weight: 700; cursor: pointer;
  transition: .2s; user-select: none;
  &:hover { background: #42a5f5; transform: scale(1.05); }
}
.dropdown-menu {
  position: absolute; top: 48px; right: 0;
  background: #fff; border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,.15);
  min-width: 160px; opacity: 0; visibility: hidden;
  transform: translateY(-6px); transition: all .2s; z-index: 200;
  &.show { opacity: 1; visibility: visible; transform: translateY(0); }
}
.dropdown-item {
  padding: 10px 16px; font-size: 13px; color: #333;
  cursor: pointer; white-space: nowrap; transition: .15s;
  &:hover { background: #f5f6fa; color: #1a237e; }
  &.danger { color: #e53935; &:hover { background: #ffebee; } }
}
.dropdown-divider { height: 1px; background: #e8e8e8; margin: 4px 0; }

@media(max-width:768px) {
  .header { padding: 0 16px; }
  .nav { display: none; }
}
</style>
