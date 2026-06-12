<template>
  <div class="register-page">
    <div class="register-box">
      <div class="logo">🎓 科明365 <span>VR教学云平台 · 用户注册</span></div>

      <div class="form-group">
        <label>用户名</label>
        <input v-model="form.username" type="text" placeholder="请输入用户名" maxlength="20"
               :class="{ error: errors.username }" />
        <div class="error-msg" v-if="errors.username">{{ errors.username }}</div>
      </div>

      <div class="form-group">
        <label>姓名</label>
        <input v-model="form.name" type="text" placeholder="请输入真实姓名" maxlength="20"
               :class="{ error: errors.name }" />
        <div class="error-msg" v-if="errors.name">{{ errors.name }}</div>
      </div>

      <div class="form-group">
        <label>密码</label>
        <input v-model="form.password" type="password" placeholder="请输入密码（至少6位）" maxlength="32"
               :class="{ error: errors.password }" />
        <div class="error-msg" v-if="errors.password">{{ errors.password }}</div>
      </div>

      <div class="form-group">
        <label>确认密码</label>
        <input v-model="form.password2" type="password" placeholder="请再次输入密码" maxlength="32"
               :class="{ error: errors.password2 }" />
        <div class="error-msg" v-if="errors.password2">{{ errors.password2 }}</div>
      </div>

      <div class="form-group">
        <label>手机号（选填）</label>
        <input v-model="form.phone" type="text" placeholder="请输入手机号" maxlength="11" />
      </div>

      <button class="btn" :disabled="loading" @click="doRegister">
        {{ loading ? '注册中...' : '注册' }}
      </button>

      <div class="tips">已有账号？<router-link to="/login">立即登录</router-link></div>
      <div class="reg-msg" :class="{ success: regSuccess }">{{ regMsg }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const loading = ref(false)
const regMsg = ref('')
const regSuccess = ref(false)

const form = reactive({
  username: '', name: '', password: '', password2: '', phone: ''
})
const errors = reactive({
  username: '', name: '', password: '', password2: ''
})

const clearErrors = () => {
  errors.username = errors.name = errors.password = errors.password2 = ''
}

const doRegister = async () => {
  clearErrors()
  regMsg.value = ''
  regSuccess.value = false
  let ok = true

  if (!form.username.trim()) { errors.username = '请输入用户名'; ok = false }
  if (!form.name.trim()) { errors.name = '请输入姓名'; ok = false }
  if (!form.password || form.password.length < 6) { errors.password = '密码至少6位'; ok = false }
  if (form.password !== form.password2) { errors.password2 = '两次密码不一致'; ok = false }
  if (form.phone && !/^1\d{10}$/.test(form.phone)) { regMsg.value = '手机号格式不正确'; ok = false }
  if (!ok) return

  loading.value = true
  try {
    await api.post('/accounts/auth/register/', {
      username: form.username.trim(),
      name: form.name.trim(),
      password: form.password,
      telephone: form.phone || undefined
    })
    regSuccess.value = true
    regMsg.value = '注册成功！即将跳转登录...'
    setTimeout(() => router.push('/login'), 1500)
  } catch (e: any) {
    regMsg.value = e.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.register-page {
  font-family: 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, #1a237e, #283593);
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
}
.register-box {
  background: #fff; border-radius: 16px; padding: 40px;
  width: 420px; box-shadow: 0 20px 60px rgba(0,0,0,.3);
}
.logo {
  text-align: center; font-size: 22px; font-weight: 700;
  color: #1a237e; margin-bottom: 24px;
  span { color: #666; font-size: 13px; font-weight: 400; display: block; margin-top: 4px; }
}
.form-group {
  margin-bottom: 16px;
  label { font-size: 13px; color: #666; display: block; margin-bottom: 4px; font-weight: 600; }
  input {
    width: 100%; padding: 10px 12px; border: 1px solid #ddd;
    border-radius: 8px; font-size: 14px; outline: none; transition: .2s;
    &:focus { border-color: #1a237e; box-shadow: 0 0 0 3px rgba(26,35,126,.1); }
    &.error { border-color: #e53935; }
  }
}
.error-msg { color: #e53935; font-size: 12px; margin-top: 4px; }
.btn {
  width: 100%; padding: 12px; background: #1a237e; color: #fff;
  border: none; border-radius: 8px; font-size: 15px; cursor: pointer;
  transition: .2s; font-weight: 600;
  &:hover { background: #283593; }
  &:disabled { background: #999; cursor: not-allowed; }
}
.tips {
  text-align: center; margin-top: 16px; font-size: 13px; color: #999;
  a { color: #1a237e; text-decoration: none; font-weight: 600; &:hover { text-decoration: underline; } }
}
.reg-msg {
  text-align: center; margin-top: 12px; font-size: 13px; color: #e53935;
  &.success { color: #2e7d32; }
}
</style>
