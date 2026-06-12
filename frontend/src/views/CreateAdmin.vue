<template>
  <div class="create-admin-page">
    <div class="container">
      <div class="page-header">
        <h1>👑 创建管理员账号</h1>
        <p>初始化数据库后用此页面创建第一个管理员</p>
      </div>

      <div class="form-card">
        <div class="alert">
          ⚠️ 仅用于初始化系统，第一个管理员账号创建后请妥善保管，删除此页面
        </div>

        <div class="form-group">
          <label>用户名 <span class="required">*</span></label>
          <input v-model="form.username" class="form-input" placeholder="admin" />
        </div>
        <div class="form-group">
          <label>密码 <span class="required">*</span></label>
          <input v-model="form.password" type="password" class="form-input" placeholder="至少6位" />
        </div>
        <div class="form-group">
          <label>确认密码 <span class="required">*</span></label>
          <input v-model="form.confirm" type="password" class="form-input" placeholder="再次输入密码" />
        </div>
        <div class="form-group">
          <label>姓名</label>
          <input v-model="form.name" class="form-input" placeholder="管理员" />
        </div>
        <div class="form-group">
          <label>手机</label>
          <input v-model="form.telephone" class="form-input" placeholder="13800000000" />
        </div>
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="form.email" type="email" class="form-input" placeholder="admin@example.com" />
        </div>

        <button class="submit-btn" @click="submit" :disabled="submitting">
          {{ submitting ? '⏳ 创建中...' : '🚀 创建管理员' }}
        </button>

        <div v-if="result" class="result" :class="result.success ? 'success' : 'fail'">
          {{ result.success ? '✅' : '❌' }} {{ result.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { toast } from '@/utils'

const router = useRouter()
const submitting = ref(false)
const result = ref<{ success: boolean; message: string } | null>(null)

const form = ref({
  username: 'admin',
  password: '',
  confirm: '',
  name: '系统管理员',
  telephone: '',
  email: ''
})

const submit = async () => {
  result.value = null

  if (!form.value.username) { toast('请输入用户名', 'error'); return }
  if (!form.value.password || form.value.password.length < 6) { toast('密码至少6位', 'error'); return }
  if (form.value.password !== form.value.confirm) { toast('两次密码不一致', 'error'); return }

  submitting.value = true
  try {
    const res: any = await api.post('/admin/create-admin/', {
      username: form.value.username,
      password: form.value.password,
      name: form.value.name,
      telephone: form.value.telephone,
      email: form.value.email,
      type: 2
    })
    result.value = { success: true, message: '管理员创建成功！请登录使用' }
    toast('创建成功', 'success')
    setTimeout(() => router.push('/login'), 2000)
  } catch (e: any) {
    result.value = { success: false, message: e.message || '创建失败' }
    toast(e.message || '创建失败', 'error')
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
.create-admin-page { background: #f5f6fa; min-height: 60vh; }
.container { max-width: 600px; margin: 0 auto; padding: 20px; }
.page-header { text-align: center; padding: 20px;
  h1 { font-size: 24px; color: #1a237e; margin-bottom: 6px; }
  p { font-size: 13px; color: #999; }
}

.form-card { background: #fff; border-radius: 12px; padding: 32px; box-shadow: 0 1px 4px rgba(0,0,0,.06);
  .alert { background: #fff3e0; color: #e65100; padding: 12px 16px; border-radius: 8px; margin-bottom: 24px; font-size: 13px; }
  .form-group { margin-bottom: 16px;
    label { display: block; font-size: 13px; color: #666; margin-bottom: 6px;
      .required { color: #e53935; }
    }
    .form-input { width: 100%; padding: 10px 14px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; outline: none;
      &:focus { border-color: #1a237e; }
    }
  }
  .submit-btn { width: 100%; padding: 12px; background: #1a237e; color: #fff; border: none; border-radius: 8px; font-size: 15px; cursor: pointer; margin-top: 8px;
    &:hover { background: #283593; }
    &:disabled { opacity: 0.6; cursor: not-allowed; }
  }
  .result { margin-top: 16px; padding: 12px; border-radius: 6px; text-align: center; font-size: 14px;
    &.success { background: #e8f5e9; color: #2e7d32; }
    &.fail { background: #ffebee; color: #c62828; }
  }
}
</style>