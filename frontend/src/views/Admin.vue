<template>
  <div class="admin-page">
    <div class="container">
      <div class="page-header">
        <h1>👑 管理后台</h1>
        <p>用户管理、课程审核、系统监控</p>
      </div>

      <!-- 概览统计 -->
      <div class="stats-row">
        <div class="stat-card" :class="`c${i}`" v-for="(s, i) in statsCards" :key="i">
          <div class="num">{{ s.num }}</div>
          <div class="label">{{ s.label }}</div>
        </div>
      </div>

      <!-- Tab -->
      <div class="tabs">
        <div v-for="t in tabs" :key="t.key" class="tab" :class="{ active: activeTab === t.key }" @click="switchTab(t.key)">
          {{ t.label }}
        </div>
      </div>

      <!-- 用户管理 -->
      <div v-if="activeTab === 'users'" class="tab-content">
        <div class="toolbar">
          <input v-model="userSearch" placeholder="搜索用户..." class="search-input" @input="loadUsers" />
          <select v-model="userFilter" @change="loadUsers" class="filter-select">
            <option value="all">全部</option>
            <option value="0">学生</option>
            <option value="1">教师</option>
            <option value="2">管理员</option>
          </select>
        </div>
        <div v-if="users.length === 0" class="empty">暂无用户数据</div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>ID</th><th>用户名</th><th>姓名</th><th>手机</th><th>类型</th><th>状态</th><th>注册时间</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>{{ u.id }}</td>
              <td>{{ u.username }}</td>
              <td>{{ u.name || '-' }}</td>
              <td>{{ u.telephone || '-' }}</td>
              <td><span class="tag" :class="`type-${u.type}`">{{ typeMap[u.type] || '未知' }}</span></td>
              <td><span class="tag" :class="u.status === 1 ? 'active' : 'inactive'">{{ u.status === 1 ? '启用' : '禁用' }}</span></td>
              <td>{{ u.createTime ? u.createTime.slice(0, 10) : '-' }}</td>
              <td>
                <button class="btn-sm" @click="toggleUserStatus(u)">{{ u.status === 1 ? '禁用' : '启用' }}</button>
                <button class="btn-sm danger" @click="deleteUser(u)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="pagination" v-if="userTotalPages > 1">
          <button :disabled="userPage <= 1" @click="userPage--; loadUsers()">上一页</button>
          <span>{{ userPage }} / {{ userTotalPages }}</span>
          <button :disabled="userPage >= userTotalPages" @click="userPage++; loadUsers()">下一页</button>
        </div>
      </div>

      <!-- 课程管理 -->
      <div v-else-if="activeTab === 'courses'" class="tab-content">
        <div class="toolbar">
          <input v-model="courseSearch" placeholder="搜索课程..." class="search-input" @input="loadCourses" />
        </div>
        <div v-if="courses.length === 0" class="empty">暂无课程数据</div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>ID</th><th>课程名</th><th>分类</th><th>价格</th><th>实验数</th><th>章节数</th><th>创建时间</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in courses" :key="c.id">
              <td>{{ c.id }}</td>
              <td>{{ c.curriculumName }}</td>
              <td>{{ c.classifyName || '-' }}</td>
              <td>{{ parseFloat(c.price || 0) <= 0 ? '免费' : '¥' + parseFloat(c.price).toFixed(2) }}</td>
              <td>{{ c.experimentCount || 0 }}</td>
              <td>{{ c.chapterCount || 0 }}</td>
              <td>{{ c.createTime ? c.createTime.slice(0, 10) : '-' }}</td>
              <td>
                <button class="btn-sm" @click="viewCourse(c)">查看</button>
                <button class="btn-sm danger" @click="deleteCourse(c)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="pagination" v-if="courseTotalPages > 1">
          <button :disabled="coursePage <= 1" @click="coursePage--; loadCourses()">上一页</button>
          <span>{{ coursePage }} / {{ courseTotalPages }}</span>
          <button :disabled="coursePage >= courseTotalPages" @click="coursePage++; loadCourses()">下一页</button>
        </div>
      </div>

      <!-- 系统监控 -->
      <div v-else-if="activeTab === 'system'" class="tab-content">
        <div class="system-info">
          <h3>系统信息</h3>
          <div class="info-grid">
            <div class="info-item"><span>系统状态</span><b class="ok">✅ 正常运行</b></div>
            <div class="info-item"><span>当前时间</span><b>{{ currentTime }}</b></div>
            <div class="info-item"><span>API 地址</span><b>{{ apiBase }}</b></div>
            <div class="info-item"><span>登录状态</span><b>{{ isLoggedIn ? '✅ 已登录' : '❌ 未登录' }}</b></div>
            <div class="info-item"><span>用户类型</span><b>{{ isAdmin ? '👑 管理员' : '普通用户' }}</b></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { toast, formatDate } from '@/utils'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref<'users' | 'courses' | 'system'>('users')
const tabs = [
  { key: 'users' as const, label: '👥 用户管理' },
  { key: 'courses' as const, label: '📚 课程管理' },
  { key: 'system' as const, label: '🖥️ 系统信息' }
]

const typeMap: Record<number, string> = { 0: '学生', 1: '教师', 2: '管理员' }
const apiBase = (import.meta.env.VITE_API_BASE_URL || '/api/v1')

const isLoggedIn = computed(() => !!localStorage.getItem('token'))
const isAdmin = computed(() => userStore.user?.type === 2)

const users = ref<any[]>([])
const userTotal = ref(0)
const userPage = ref(1)
const userSearch = ref('')
const userFilter = ref('all')
const userTotalPages = computed(() => Math.ceil(userTotal.value / 20))

const courses = ref<any[]>([])
const courseTotal = ref(0)
const coursePage = ref(1)
const courseSearch = ref('')
const courseTotalPages = computed(() => Math.ceil(courseTotal.value / 20))

const statsCards = ref([
  { num: 0, label: '总用户' },
  { num: 0, label: '总课程' },
  { num: 0, label: '总实验' },
  { num: 0, label: '总订单' }
])

const currentTime = ref('')
let timer: any = null

const updateTime = () => { currentTime.value = new Date().toLocaleString('zh-CN') }

const loadStats = async () => {
  try {
    const d = await api.get('/admin/stats/')
    if (d) {
      statsCards.value = [
        { num: d.userCount || 0, label: '总用户' },
        { num: d.courseCount || 0, label: '总课程' },
        { num: d.experimentCount || 0, label: '总实验' },
        { num: d.orderCount || 0, label: '总订单' }
      ]
    }
  } catch { /* ignore */ }
}

const loadUsers = async () => {
  try {
    const d = await api.get('/admin/users/', {
      params: { page: userPage.value, search: userSearch.value, type: userFilter.value }
    })
    users.value = d.results || []
    userTotal.value = d.count || 0
  } catch (e: any) { toast(e.message || '加载用户失败', 'error') }
}

const loadCourses = async () => {
  try {
    const d = await api.get('/admin/courses/', {
      params: { page: coursePage.value, search: courseSearch.value }
    })
    courses.value = d.results || []
    courseTotal.value = d.count || 0
  } catch (e: any) { toast(e.message || '加载课程失败', 'error') }
}

const switchTab = (tab: 'users' | 'courses' | 'system') => {
  activeTab.value = tab
  if (tab === 'users') loadUsers()
  else if (tab === 'courses') loadCourses()
}

const toggleUserStatus = async (u: any) => {
  if (!confirm(`确认${u.status === 1 ? '禁用' : '启用'}用户「${u.username}」？`)) return
  try {
    await api.post(`/admin/users/${u.id}/toggle/`)
    toast('操作成功', 'success')
    loadUsers()
  } catch (e: any) { toast(e.message || '操作失败', 'error') }
}

const deleteUser = async (u: any) => {
  if (!confirm(`确认删除用户「${u.username}」？该操作不可恢复！`)) return
  try {
    await api.delete(`/admin/users/${u.id}/`)
    toast('已删除', 'success')
    loadUsers()
  } catch (e: any) { toast(e.message || '删除失败', 'error') }
}

const viewCourse = (c: any) => router.push({ path: '/course', query: { id: String(c.id) } })
const deleteCourse = async (c: any) => {
  if (!confirm(`确认删除课程「${c.curriculumName}」？`)) return
  try {
    await api.delete(`/admin/courses/${c.id}/`)
    toast('已删除', 'success')
    loadCourses()
  } catch (e: any) { toast(e.message || '删除失败', 'error') }
}

onMounted(() => {
  if (!isLoggedIn.value) {
    toast('请先登录', 'error')
    router.push('/login')
    return
  }
  if (!isAdmin.value) {
    toast('您没有管理员权限', 'error')
    router.push('/')
    return
  }
  updateTime()
  timer = setInterval(updateTime, 1000)
  loadStats()
  loadUsers()
})

onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style lang="scss" scoped>
.admin-page { background: #f5f6fa; min-height: 60vh; }
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.page-header { text-align: center; padding: 30px 20px 20px;
  h1 { font-size: 28px; color: #1a237e; margin-bottom: 8px; }
  p { font-size: 14px; color: #999; }
}

.stats-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px;
  .stat-card { background: #fff; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,.06);
    .num { font-size: 32px; font-weight: 700; color: #1a237e; }
    .label { font-size: 13px; color: #999; margin-top: 4px; }
    &.c0 { background: linear-gradient(135deg, #e3f2fd, #bbdefb); .num { color: #1565c0; } }
    &.c1 { background: linear-gradient(135deg, #f3e5f5, #e1bee7); .num { color: #6a1b9a; } }
    &.c2 { background: linear-gradient(135deg, #e8f5e9, #c8e6c9); .num { color: #2e7d32; } }
    &.c3 { background: linear-gradient(135deg, #fff3e0, #ffe0b2); .num { color: #e65100; } }
  }
}

.tabs { display: flex; background: #fff; border-radius: 12px 12px 0 0; overflow: hidden; margin-bottom: 0;
  .tab { flex: 1; padding: 14px; text-align: center; font-size: 14px; cursor: pointer; border-bottom: 3px solid transparent; color: #666; transition: .2s;
    &:hover { color: #1a237e; }
    &.active { color: #1a237e; border-bottom-color: #1a237e; font-weight: 600; }
  }
}

.tab-content { background: #fff; border-radius: 0 0 12px 12px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,.06); }

.toolbar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;
  .search-input { padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; min-width: 240px; outline: none; &:focus { border-color: #1a237e; } }
  .filter-select { padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; }
}

.data-table { width: 100%; border-collapse: collapse;
  th, td { padding: 12px 8px; text-align: left; border-bottom: 1px solid #eef0f4; font-size: 13px; }
  th { background: #fafbff; color: #666; font-weight: 600; }
  tr:hover { background: #fafbff; }
  .tag { padding: 2px 8px; border-radius: 10px; font-size: 11px;
    &.type-0 { background: #e3f2fd; color: #1565c0; }
    &.type-1 { background: #f3e5f5; color: #6a1b9a; }
    &.type-2 { background: #fff3e0; color: #e65100; }
    &.active { background: #e8f5e9; color: #2e7d32; }
    &.inactive { background: #ffebee; color: #c62828; }
  }
  .btn-sm { padding: 4px 10px; font-size: 11px; border-radius: 4px; background: #1a237e; color: #fff; border: none; cursor: pointer; margin-right: 4px;
    &.danger { background: #e53935; }
    &:hover { opacity: 0.85; }
  }
}

.pagination { display: flex; align-items: center; justify-content: center; gap: 12px; padding: 16px 0;
  button { padding: 6px 16px; border: 1px solid #ddd; border-radius: 4px; background: #fff; cursor: pointer; &:disabled { opacity: 0.5; cursor: not-allowed; } }
}

.empty { text-align: center; padding: 60px 20px; color: #999; }

.system-info { h3 { font-size: 18px; color: #1a237e; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 2px solid #f0f0f0; }
  .info-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px;
    .info-item { display: flex; justify-content: space-between; padding: 12px 16px; background: #fafbff; border-radius: 8px; font-size: 14px; span { color: #999; } b { color: #333; } .ok { color: #2e7d32; } }
  }
}
</style>