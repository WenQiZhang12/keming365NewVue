<template>
  <div class="profile-page">
    <div class="container">
      <div class="breadcrumb">
        <router-link to="/">首页</router-link> &gt; 个人中心
      </div>

      <!-- 未登录提示 -->
      <div v-if="!user" class="login-prompt">
        <div class="icon">🔐</div>
        <h2>请先登录</h2>
        <p>登录后查看学习计划、成绩和订单</p>
        <router-link to="/login" class="btn-login-link">去登录</router-link>
      </div>

      <template v-else>
        <div class="profile-card">
          <div class="avatar">👤</div>
          <div class="info">
            <h2>{{ user.name || user.username }}</h2>
            <p>手机：{{ user.telephone || '-' }} | 类型：{{ typeMap[user.type] || '未知' }}</p>
          </div>
          <div class="badges">
            <span class="badge" @click="editProfile">编辑资料 ✏️</span>
            <span class="badge" @click="changePassword">修改密码 🔑</span>
          </div>
        </div>

        <div class="stats-grid">
          <div v-for="(s, i) in statsList" :key="i" class="stat-card">
            <div class="num">{{ s.num }}</div>
            <div class="label">{{ s.label }}</div>
          </div>
        </div>

        <div class="tabs">
          <div v-for="t in tabs" :key="t.key" class="tab" :class="{ active: activeTab === t.key }" @click="switchTab(t.key)">
            {{ t.label }}
          </div>
        </div>
        <div class="tab-content">
          <div v-if="tabLoading" class="loading">
            <div class="spinner"></div>加载中...
          </div>
          <div v-else-if="activeTab === 'plans'">
            <div v-if="plans.length === 0" class="empty">
              <div class="icon">🔬</div>
              <p>暂无实验记录</p>
              <p class="hint">去课程页面点击「开始实验」即可加入</p>
            </div>
            <div v-else>
              <div v-for="p in plans" :key="p.id" class="plan-card" @click="goExperiment(p.id)">
                <div class="plan-icon">🔬</div>
                <div class="plan-info">
                  <h4>{{ p.title || '实验' }}</h4>
                  <p>{{ p.firstPracticeTime ? '首次练习：' + p.firstPracticeTime.slice(0, 10) : '' }}</p>
                </div>
                <span class="plan-status ing">已练习 {{ p.practiceCount }} 次</span>
              </div>
            </div>
          </div>

          <div v-else-if="activeTab === 'scores'">
            <div v-if="scores.length === 0" class="empty">
              <div class="icon">📊</div>
              <p>暂无学习记录</p>
            </div>
            <div v-else>
              <div v-for="s in scores" :key="s.id" class="score-card">
                <div class="score-icon">🔬</div>
                <div class="score-info">
                  <h4>{{ s.experimentName || '实验' }}</h4>
                  <p>{{ s.createTime ? s.createTime.slice(0, 10) : '' }}</p>
                </div>
                <div class="score-num">{{ s.reportScore || '-' }}</div>
              </div>
            </div>
          </div>

          <div v-else-if="activeTab === 'orders'">
            <div v-if="orders.length === 0" class="empty">
              <div class="icon">📦</div>
              <p>暂无订单</p>
            </div>
            <div v-else>
              <div v-for="o in orders" :key="o.id" class="order-card">
                <div class="order-header">
                  <span class="order-id">订单号：{{ o.id }}</span>
                  <span class="order-status" :class="statusClass(o.status)">{{ statusLabel[o.status] || '未知' }}</span>
                </div>
                <div class="order-body">
                  <div>{{ o.productName || '商品' }}</div>
                  <div class="price">¥{{ parseFloat(o.amount || 0).toFixed(2) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api, { getProfile } from '@/api'
import { useUserStore } from '@/stores/user'
import { toast } from '@/utils'

const router = useRouter()
const userStore = useUserStore()

const user = ref<any>(null)
const activeTab = ref<'plans' | 'scores' | 'orders'>('plans')
const tabLoading = ref(false)

const plans = ref<any[]>([])
const scores = ref<any[]>([])
const orders = ref<any[]>([])

const typeMap: Record<number, string> = { 0: '学生', 1: '教师', 2: '管理员' }
const statusLabel: Record<number, string> = { 0: '⏳ 待支付', 1: '✅ 已支付', '-1': '❌ 已取消' }
const tabs = [
  { key: 'plans' as const, label: '🔬 我的实验' },
  { key: 'scores' as const, label: '📊 学习成果' },
  { key: 'orders' as const, label: '📦 我的订单' }
]

const statsList = computed(() => {
  if (activeTab.value === 'plans') {
    return [
      { num: plans.value.length, label: '我的实验' },
      { num: plans.value.length, label: '已练习' },
      { num: 0, label: '已完成' }
    ]
  } else if (activeTab.value === 'scores') {
    const avg = scores.value.length
      ? Math.round(scores.value.reduce((s, c) => s + parseFloat(c.reportScore || 0), 0) / scores.value.length)
      : 0
    const totalTime = scores.value.reduce((s, c) => s + parseFloat(c.totalTime || 0), 0)
    return [
      { num: scores.value.length, label: '实验次数' },
      { num: avg, label: '平均分' },
      { num: Math.round(totalTime / 60), label: '学习时长(分)' }
    ]
  } else {
    const paid = orders.value.filter(o => o.status === 1).length
    const pending = orders.value.filter(o => o.status === 0).length
    return [
      { num: orders.value.length, label: '总订单' },
      { num: paid, label: '已支付' },
      { num: pending, label: '待支付' }
    ]
  }
})

const statusClass = (s: number) => s === 1 ? 'paid' : s === 0 ? 'pending' : 'cancel'

const goExperiment = (id: string | number) => {
  router.push({ path: '/experiment', query: { id: String(id) } })
}

const editProfile = () => toast('编辑资料功能开发中', 'info')
const changePassword = () => toast('修改密码功能开发中', 'info')

const switchTab = (tab: 'plans' | 'scores' | 'orders') => {
  activeTab.value = tab
  loadTab(tab)
}

const loadTab = async (tab: 'plans' | 'scores' | 'orders') => {
  tabLoading.value = true
  try {
    if (tab === 'plans') {
      const d = await api.get('/scores/my-experiments/')
      plans.value = d.results || []
    } else if (tab === 'scores') {
      const d = await api.get('/scores/my/')
      scores.value = d.results || []
    } else if (tab === 'orders') {
      const d = await api.get('/payments/orders/')
      orders.value = d.results || []
    }
  } catch (e: any) {
    toast(e.message || '加载失败', 'error')
  } finally {
    tabLoading.value = false
  }
}

const init = async () => {
  const token = localStorage.getItem('token')
  if (!token) return

  try {
    const data = await getProfile()
    if (!data || !data.username) throw new Error('获取用户信息失败')
    user.value = data
    await loadTab('plans')
  } catch (e: any) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    toast('登录已过期，请重新登录', 'error')
  }
}

onMounted(init)
watch(() => userStore.token, init)
</script>

<style lang="scss" scoped>
.profile-page { background: #f5f6fa; min-height: 60vh; }
.container { max-width: 1000px; margin: 0 auto; padding: 20px; }
.breadcrumb { font-size: 13px; color: #999; margin-bottom: 16px; a { color: #1a237e; } }

.login-prompt { text-align: center; padding: 80px 20px; background: #fff; border-radius: 12px;
  .icon { font-size: 48px; margin-bottom: 12px; }
  h2 { font-size: 20px; margin-bottom: 12px; }
  p { margin-bottom: 20px; color: #999; }
  .btn-login-link { display: inline-block; padding: 12px 32px; background: #1a237e; color: #fff; border-radius: 8px; font-size: 15px; text-decoration: none; }
}

.profile-card {
  background: linear-gradient(135deg, #1a237e, #3949ab); border-radius: 16px;
  padding: 30px; color: #fff; display: flex; align-items: center; gap: 24px; margin-bottom: 24px;
  .avatar { width: 72px; height: 72px; border-radius: 50%; background: rgba(255,255,255,.2); display: flex; align-items: center; justify-content: center; font-size: 32px; flex-shrink: 0; }
  .info { flex: 1; h2 { font-size: 22px; margin-bottom: 4px; } p { font-size: 13px; opacity: .8; } }
  .badges { display: flex; gap: 8px;
    .badge { padding: 6px 16px; border-radius: 20px; font-size: 12px; background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.2); cursor: pointer; transition: .2s;
      &:hover { background: rgba(255,255,255,.25); }
    }
  }
}

.stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; margin-bottom: 20px;
  .stat-card { text-align: center; padding: 16px; background: #fafbff; border-radius: 10px; border: 1px solid #eef0f4;
    .num { font-size: 24px; font-weight: 700; color: #1a237e; }
    .label { font-size: 12px; color: #999; margin-top: 4px; }
  }
}

.tabs { display: flex; background: #fff; border-radius: 12px 12px 0 0; overflow: hidden;
  .tab { flex: 1; padding: 14px; text-align: center; font-size: 14px; cursor: pointer; border-bottom: 3px solid transparent; color: #666; transition: .2s;
    &:hover { color: #1a237e; }
    &.active { color: #1a237e; border-bottom-color: #1a237e; font-weight: 600; }
  }
}

.tab-content {
  background: #fff; border-radius: 0 0 12px 12px; padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,.06); margin-bottom: 24px; min-height: 300px;
}

.loading { text-align: center; padding: 60px; color: #999;
  .spinner { display: inline-block; width: 28px; height: 28px; border: 3px solid #e0e0e0; border-top-color: #1a237e; border-radius: 50%; animation: spin .8s linear infinite; margin-bottom: 10px; }
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; padding: 60px 20px; color: #999; .icon { font-size: 48px; margin-bottom: 12px; } .hint { font-size: 13px; color: #bbb; margin-top: 8px; } }

.plan-card { display: flex; align-items: center; gap: 16px; padding: 16px; border: 1px solid #eef0f4; border-radius: 10px; margin-bottom: 10px; cursor: pointer; transition: .2s;
  &:hover { border-color: #c5cae9; background: #fafbff; }
  .plan-icon { width: 48px; height: 48px; border-radius: 10px; background: linear-gradient(135deg, #e8eaf6, #c5cae9); display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0; }
  .plan-info { flex: 1; h4 { font-size: 14px; font-weight: 600; margin-bottom: 4px; } p { font-size: 12px; color: #999; } }
  .plan-status { padding: 4px 12px; border-radius: 12px; font-size: 12px; &.ing { background: #e3f2fd; color: #1565c0; } &.done { background: #e8f5e9; color: #2e7d32; } }
}

.score-card { display: flex; align-items: center; gap: 16px; padding: 14px 16px; border: 1px solid #eef0f4; border-radius: 10px; margin-bottom: 8px; transition: .2s;
  &:hover { border-color: #c5cae9; }
  .score-icon { width: 40px; height: 40px; border-radius: 8px; background: linear-gradient(135deg, #fff3e0, #ffe0b2); display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
  .score-info { flex: 1; h4 { font-size: 14px; font-weight: 600; margin-bottom: 2px; } p { font-size: 12px; color: #999; } }
  .score-num { font-size: 20px; font-weight: 700; color: #1a237e; }
}

.order-card { border: 1px solid #eef0f4; border-radius: 10px; padding: 16px; margin-bottom: 10px;
  .order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;
    .order-id { font-size: 12px; color: #999; }
    .order-status { padding: 3px 10px; border-radius: 10px; font-size: 11px;
      &.paid { background: #e8f5e9; color: #2e7d32; }
      &.pending { background: #fff3e0; color: #e65100; }
      &.cancel { background: #f5f5f5; color: #999; }
    }
  }
  .order-body { font-size: 13px; color: #555; line-height: 1.8; .price { font-size: 18px; font-weight: 700; color: #e53935; margin-top: 4px; } }
}

@media(max-width: 768px) {
  .profile-card { flex-direction: column; text-align: center; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
</content>
</invoke>