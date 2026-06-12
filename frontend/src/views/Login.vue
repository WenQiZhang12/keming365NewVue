<template>
  <div class="login-page">
    <div class="container">
      <div class="logo">
        <h1>🔐 科明365VR教学云平台</h1>
        <p>专业的虚拟仿真教学平台</p>
      </div>

      <div class="form-group">
        <input v-model="form.username" type="text" placeholder="用户名"
               @keydown.enter="pwdRef?.focus()" />
      </div>

      <div class="form-group">
        <input ref="pwdRef" v-model="form.password" type="password" placeholder="密码"
               @keydown.enter="doLogin" />
      </div>

      <button class="login-btn" :disabled="loading" @click="doLogin">
        {{ loading ? '登录中...' : '登录' }}
      </button>

      <p class="error-msg">{{ errorMsg }}</p>

      <div class="link-row">
        <a href="#" @click.prevent="showForgotPassword">忘记密码？</a>
        <router-link to="/register">注册账号</router-link>
      </div>

      <div class="switch-mode">
        <router-link to="/">← 返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const pwdRef = ref<HTMLInputElement | null>(null)
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({ username: '', password: '' })

const doLogin = async () => {
  errorMsg.value = ''
  if (!form.username.trim()) { errorMsg.value = '请输入用户名'; return }
  if (!form.password) { errorMsg.value = '请输入密码'; return }

  loading.value = true
  try {
    await userStore.login(form.username.trim(), form.password)
    const redirect = sessionStorage.getItem('redirectAfterLogin') || '/'
    sessionStorage.removeItem('redirectAfterLogin')
    router.push(redirect)
  } catch (e: any) {
    errorMsg.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}

const showForgotPassword = () => {
  alert('忘记密码功能即将上线，请联系管理员重置密码')
}

onMounted(() => {
  if (userStore.token) router.push('/')
})
</script>

<style lang="scss" scoped>
.login-page {
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  background: linear-gradient(135deg, #1a237e, #3949ab);
  min-height: 100vh; display: flex; align-items: center;
  justify-content: center; padding: 20px;
}
.container {
  background: #fff; border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,.3);
  width: 100%; max-width: 420px; padding: 40px;
}
.logo {
  text-align: center; margin-bottom: 32px;
  h1 { font-size: 28px; color: #1a237e; margin-bottom: 8px; }
  p { color: #666; font-size: 14px; }
}
.form-group {
  margin-bottom: 20px;
  input {
    width: 100%; padding: 12px 16px; border: 1px solid #ddd;
    border-radius: 8px; font-size: 15px; outline: none;
    transition: border-color .2s;
    &:focus { border-color: #1a237e; }
    &::placeholder { color: #999; }
  }
}
.login-btn {
  width: 100%; padding: 14px; background: #1a237e; color: #fff;
  border: none; border-radius: 8px; font-size: 16px; cursor: pointer;
  transition: background .2s;
  &:hover { background: #283593; }
  &:active { transform: scale(.98); }
  &:disabled { background: #999; cursor: not-allowed; }
}
.error-msg {
  color: #e53935; font-size: 13px; text-align: center;
  margin-top: 12px; min-height: 20px;
}
.link-row {
  display: flex; justify-content: space-between;
  margin-top: 16px; font-size: 13px;
  a { color: #1a237e; text-decoration: none; &:hover { text-decoration: underline; } }
}
.switch-mode {
  text-align: center; margin-top: 24px; padding-top: 24px;
  border-top: 1px solid #eee;
  a { color: #1a237e; font-weight: 500; }
}
</style>
