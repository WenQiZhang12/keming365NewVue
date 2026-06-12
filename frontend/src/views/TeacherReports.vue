<template>
  <div class="teacher-reports-page">
    <div class="container">
      <div class="breadcrumb">
        <router-link to="/">首页</router-link> &gt; 教师报告管理
      </div>
      <div class="page-header">
        <h1>👨‍🏫 学生报告管理</h1>
        <p>查看、评阅和管理所有学生提交的实验报告</p>
      </div>

      <div class="stats-row">
        <div class="stat-card c0"><div class="num">{{ stats.total }}</div><div class="label">总报告</div></div>
        <div class="stat-card c1"><div class="num">{{ stats.pending }}</div><div class="label">待评阅</div></div>
        <div class="stat-card c2"><div class="num">{{ stats.passed }}</div><div class="label">已通过</div></div>
        <div class="stat-card c3"><div class="num">{{ stats.rejected }}</div><div class="label">已驳回</div></div>
      </div>

      <div class="filter-bar">
        <input v-model="search" placeholder="搜索学生/实验..." class="search-input" />
        <select v-model="filterStatus" class="filter-select">
          <option value="all">全部状态</option>
          <option value="0">待评阅</option>
          <option value="1">已通过</option>
          <option value="-1">已驳回</option>
        </select>
      </div>

      <div v-if="loading" class="loading"><div class="spinner"></div>加载中...</div>
      <div v-else-if="filteredReports.length === 0" class="empty">
        <div class="icon">📋</div>
        <p>暂无报告</p>
      </div>
      <div v-else>
        <div v-for="r in filteredReports" :key="r.id" class="report-card" @click="goReview(r)">
          <div class="student-avatar">{{ (r.studentName || '?')[0] }}</div>
          <div class="report-info">
            <h4>{{ r.experimentName || '实验报告' }}</h4>
            <p>👤 {{ r.studentName || '未知学生' }}</p>
            <p>📅 {{ r.createTime ? r.createTime.slice(0, 16) : '-' }}</p>
          </div>
          <div class="report-score">
            <div class="big">{{ r.reportScore ?? '-' }}</div>
            <div class="hint">满分100</div>
          </div>
          <span class="status-tag" :class="statusClass(r.status)">{{ statusLabel[r.status] || '未知' }}</span>
        </div>
        <div class="pagination" v-if="totalPages > 1">
          <button :disabled="page <= 1" @click="page--; loadReports()">上一页</button>
          <span>{{ page }} / {{ totalPages }}</span>
          <button :disabled="page >= totalPages" @click="page++; loadReports()">下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const reports = ref<any[]>([])
const loading = ref(true)
const search = ref('')
const filterStatus = ref('all')
const page = ref(1)
const totalCount = ref(0)
const totalPages = computed(() => Math.ceil(totalCount.value / 20))

const statusLabel: Record<number, string> = { 1: '✅ 已通过', 0: '⏳ 待评阅', '-1': '❌ 已驳回' }
const stats = computed(() => {
  const total = reports.value.length
  const pending = reports.value.filter(r => r.status === 0).length
  const passed = reports.value.filter(r => r.status === 1).length
  const rejected = reports.value.filter(r => r.status === -1).length
  return { total, pending, passed, rejected }
})

const filteredReports = computed(() => {
  let result = reports.value
  if (search.value) {
    const kw = search.value.toLowerCase()
    result = result.filter(r =>
      (r.experimentName || '').toLowerCase().includes(kw) ||
      (r.studentName || '').toLowerCase().includes(kw)
    )
  }
  if (filterStatus.value !== 'all') {
    result = result.filter(r => String(r.status) === filterStatus.value)
  }
  return result
})

const statusClass = (s: number) => s === 1 ? 'pass' : s === 0 ? 'pending' : 'reject'

const goReview = (r: any) => {
  router.push({ path: '/review-report', query: { id: String(r.id) } })
}

const loadReports = async () => {
  loading.value = true
  try {
    const d = await api.get('/scores/all-reports/', { params: { page: page.value } })
    reports.value = d.results || []
    totalCount.value = d.count || 0
  } catch (e) { /* ignore */ }
  finally { loading.value = false }
}

onMounted(() => {
  if (!localStorage.getItem('token')) {
    router.push('/login')
    return
  }
  loadReports()
})
</script>

<style lang="scss" scoped>
.teacher-reports-page { background: #f5f6fa; min-height: 60vh; }
.container { max-width: 1000px; margin: 0 auto; padding: 20px; }
.breadcrumb { font-size: 13px; color: #999; margin-bottom: 16px; a { color: #1a237e; } }
.page-header { text-align: center; padding: 20px;
  h1 { font-size: 24px; color: #1a237e; margin-bottom: 6px; }
  p { font-size: 13px; color: #999; }
}

.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;
  @media(max-width: 600px) { grid-template-columns: repeat(2, 1fr); }
  .stat-card { background: #fff; padding: 16px; border-radius: 10px; text-align: center;
    .num { font-size: 24px; font-weight: 700; }
    .label { font-size: 12px; color: #999; margin-top: 4px; }
    &.c0 .num { color: #1a237e; } &.c1 .num { color: #e65100; } &.c2 .num { color: #2e7d32; } &.c3 .num { color: #c62828; }
  }
}

.filter-bar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;
  .search-input { padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; min-width: 240px; outline: none; }
  .filter-select { padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; }
}

.loading { text-align: center; padding: 60px; color: #999;
  .spinner { display: inline-block; width: 28px; height: 28px; border: 3px solid #e0e0e0; border-top-color: #1a237e; border-radius: 50%; animation: spin .8s linear infinite; margin-bottom: 10px; }
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; padding: 80px 20px; color: #999; .icon { font-size: 48px; margin-bottom: 12px; } }

.report-card { display: flex; align-items: center; gap: 16px; padding: 16px; background: #fff; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,.06); margin-bottom: 10px; cursor: pointer; transition: .2s;
  &:hover { box-shadow: 0 4px 12px rgba(0,0,0,.1); transform: translateY(-1px); }
  .student-avatar { width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #1a237e, #3949ab); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 600; flex-shrink: 0; }
  .report-info { flex: 1; h4 { font-size: 14px; font-weight: 600; margin-bottom: 4px; } p { font-size: 12px; color: #999; } }
  .report-score { text-align: center; .big { font-size: 24px; font-weight: 700; color: #1a237e; } .hint { font-size: 10px; color: #999; } }
  .status-tag { padding: 4px 12px; border-radius: 12px; font-size: 12px; flex-shrink: 0;
    &.pass { background: #e8f5e9; color: #2e7d32; }
    &.pending { background: #fff3e0; color: #e65100; }
    &.reject { background: #ffebee; color: #c62828; }
  }
}

.pagination { display: flex; align-items: center; justify-content: center; gap: 12px; padding: 16px 0;
  button { padding: 6px 16px; border: 1px solid #ddd; border-radius: 4px; background: #fff; cursor: pointer; &:disabled { opacity: 0.5; cursor: not-allowed; } }
}
</style>
</content>
</invoke>