<template>
  <div class="experiment-page">
    <div class="container">
      <div class="breadcrumb">
        <router-link to="/">首页</router-link> &gt;
        <router-link to="/qbkc">全部课程</router-link> &gt;
        <span>{{ fromName || '实验操作' }}</span> &gt;
        <span>{{ experiment?.title || '加载中...' }}</span>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>加载中...
      </div>

      <div v-else-if="error" class="empty">
        <div class="icon">😵</div>
        <p>加载失败：{{ error }}</p>
      </div>

      <template v-else-if="experiment">
        <div class="exp-header">
          <div class="exp-cover">
            <img v-if="getImageUrl(experiment.image)" :src="getImageUrl(experiment.image)" alt=""
                 @error="($event.target as HTMLImageElement).style.display='none'">
            <span v-else>🔬</span>
          </div>
          <div class="exp-meta">
            <h2>{{ experiment.title }}</h2>
            <button class="btn-enter" @click="startExperiment" :disabled="entering">
              {{ entering ? '进入中...' : '▶ 进入实验' }}
            </button>
          </div>
        </div>

        <div class="exp-tabs-wrap">
          <div class="exp-tabs">
            <div class="tab-btn" :class="{ active: activeTab === 'analysis' }" @click="activeTab = 'analysis'">📊 数据分析</div>
            <div class="tab-btn" :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">📝 内容概述</div>
          </div>

          <div v-if="activeTab === 'analysis'" class="tab-panel">
            <div class="stats-row">
              <div class="stat-box">
                <div class="stat-label">访问总量</div>
                <div class="stat-value">{{ stats.totalVisits || 0 }}</div>
                <div class="stat-new">新增 {{ stats.newVisits || 0 }}</div>
              </div>
              <div class="stat-box">
                <div class="stat-label">练习总次数</div>
                <div class="stat-value">{{ stats.totalPractice || 0 }}</div>
                <div class="stat-new">新增 {{ stats.newPractice || 0 }}</div>
              </div>
            </div>

            <div class="charts-grid">
              <div class="chart-box">
                <div class="chart-title">📈 访问总量趋势</div>
                <canvas ref="cumVisitsCanvas" height="200"></canvas>
              </div>
              <div class="chart-box">
                <div class="chart-title">📈 练习总次数趋势</div>
                <canvas ref="cumPracticeCanvas" height="200"></canvas>
              </div>
              <div class="chart-box">
                <div class="chart-title">📈 新增访问量趋势</div>
                <canvas ref="dailyVisitsCanvas" height="200"></canvas>
              </div>
              <div class="chart-box">
                <div class="chart-title">📈 新增练习次数趋势</div>
                <canvas ref="dailyPracticeCanvas" height="200"></canvas>
              </div>
            </div>
          </div>

          <div v-else class="tab-panel">
            <div class="overview">
              <h3>{{ experiment.title }}</h3>
              <p v-if="experiment.sellPoint">{{ experiment.sellPoint }}</p>
              <p v-else>本实验通过虚拟仿真技术，沉浸式展现实验场景与操作流程，让学生能在安全环境中反复练习，掌握核心知识点。</p>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { getImageUrl, toast } from '@/utils'

const route = useRoute()
const router = useRouter()

const experiment = ref<any>(null)
const loading = ref(true)
const error = ref('')
const activeTab = ref<'analysis' | 'overview'>('analysis')
const entering = ref(false)
const fromName = ref('')

const stats = ref({ 
  totalVisits: 0, 
  totalPractice: 0,
  newVisits: 0,
  newPractice: 0,
  dailyVisits: [] as any[], 
  dailyPractice: [] as any[],
  cumulativeVisits: [] as any[],
  cumulativePractice: [] as any[]
})
const cumVisitsCanvas = ref<HTMLCanvasElement | null>(null)
const cumPracticeCanvas = ref<HTMLCanvasElement | null>(null)
const dailyVisitsCanvas = ref<HTMLCanvasElement | null>(null)
const dailyPracticeCanvas = ref<HTMLCanvasElement | null>(null)

const loadExperiment = async () => {
  const id = route.params.id as string
  fromName.value = decodeURIComponent((route.query.fromName as string) || '')
  if (!id) { error.value = '缺少实验ID'; loading.value = false; return }

  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/courses/experiments/${id}/`)
    experiment.value = data
    document.title = (experiment.value?.title || '') + ' - 科明365VR教学云平台'
    await api.post(`/courses/experiments/${id}/record-visit/`).catch(() => {})
    await loadStats(id)
  } catch (e: any) {
    error.value = e.message || '请求失败'
  } finally {
    loading.value = false
  }
}

const loadStats = async (id: string) => {
  try {
    const { data } = await api.get(`/courses/experiments/${id}/stats/`)
    if (data) {
      stats.value = {
        totalVisits: data.totalVisits || 0,
        totalPractice: data.totalPractice || 0,
        newVisits: data.newVisits || 0,
        newPractice: data.newPractice || 0,
        dailyVisits: data.dailyVisits || [],
        dailyPractice: data.dailyPractice || [],
        cumulativeVisits: data.cumulativeVisits || [],
        cumulativePractice: data.cumulativePractice || []
      }
    }
  } catch { /* ignore stats error */ }
}

const drawChart = (canvas: HTMLCanvasElement | null, data: any[], color: string) => {
  if (!canvas) {
    console.log('canvas is null')
    return
  }
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    console.log('ctx is null')
    return
  }
  const parentWidth = canvas.parentElement?.clientWidth || 400
  const w = canvas.width = Math.max(parentWidth, 200)
  const h = canvas.height = 200
  ctx.clearRect(0, 0, w, h)
  if (!data || data.length === 0) {
    ctx.fillStyle = '#999'
    ctx.font = '13px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('暂无数据', w / 2, h / 2)
    return
  }
  
  const values = data.map((d: any) => d.count || 0)
  const max = Math.max(...values, 1)
  const min = Math.min(...values, 0)
  const range = max - min || 1
  
  let tickStep = 1
  const targetTicks = 5
  
  if (range > 100) {
    tickStep = Math.ceil(range / targetTicks / 10) * 10
  } else if (range > 10) {
    tickStep = Math.ceil(range / targetTicks)
  }
  
  const chartMin = Math.floor(min / tickStep) * tickStep
  const chartMax = Math.ceil(max / tickStep) * tickStep
  const actualRange = chartMax - chartMin || 1
  
  const pad = 40
  const stepX = (w - pad) / data.length
  
  ctx.strokeStyle = '#eee'
  ctx.lineWidth = 1
  ctx.fillStyle = '#666'
  ctx.font = '10px sans-serif'
  ctx.textAlign = 'right'
  
  const yLabels = Math.ceil(actualRange / tickStep) + 1
  for (let i = 0; i < yLabels; i++) {
    const value = chartMin + i * tickStep
    const y = pad + (h - pad * 2) * (1 - (value - chartMin) / actualRange)
    ctx.beginPath()
    ctx.moveTo(pad - 5, y)
    ctx.lineTo(w - 10, y)
    ctx.stroke()
    ctx.fillText(Math.round(value).toString(), pad - 8, y + 3)
  }
  
  ctx.beginPath()
  ctx.strokeStyle = color
  ctx.lineWidth = 2
  ctx.shadowColor = color
  ctx.shadowBlur = 4
  
  data.forEach((d: any, i: number) => {
    const v = d.count || 0
    const x = pad + i * stepX
    const normalizedV = (v - chartMin) / actualRange
    const y = pad + (h - pad * 2) * (1 - normalizedV)
    if (i === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  ctx.stroke()
  ctx.shadowBlur = 0
  
  ctx.textAlign = 'center'
  data.forEach((d: any, i: number) => {
    const v = d.count || 0
    const x = pad + i * stepX
    const normalizedV = (v - chartMin) / actualRange
    const y = pad + (h - pad * 2) * (1 - normalizedV)
    
    ctx.beginPath()
    ctx.fillStyle = color
    ctx.arc(x, y, 4, 0, Math.PI * 2)
    ctx.fill()
    
    ctx.beginPath()
    ctx.fillStyle = '#fff'
    ctx.arc(x, y, 2, 0, Math.PI * 2)
    ctx.fill()
    
    ctx.fillStyle = '#666'
    ctx.font = '10px sans-serif'
    ctx.fillText((d.date || '').slice(5), x, h - 12)
  })
}

const startExperiment = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    if (confirm('您尚未登录，是否前往登录？')) {
      router.push('/login')
    }
    return
  }
  entering.value = true
  try {
    const { data } = await api.post(`/courses/experiments/${experiment.value.id}/yqpath/`)
    if (data.code !== 0) {
      toast(data.message || '进入实验失败', 'error')
      return
    }
    let yqUrl: string = data.details?.resultUrl || ''
    const internalHosts = [
      'http://58.56.66.170:8181', 'https://58.56.66.170:8181',
      'http://58.56.66.170', 'https://58.56.66.170'
    ]
    for (const h of internalHosts) {
      if (yqUrl.indexOf(h) === 0) { yqUrl = yqUrl.substring(h.length); break }
    }
    yqUrl = 'https://yq.keming365.com' + yqUrl
    const appKey = data.details?.appKey || ''
    const finalUrl = yqUrl + '&appKey=' + appKey + '&timestamp=' + data.details?.timestamp + '&signature=' + data.details?.token
    window.open(finalUrl, '_blank')
  } catch (e: any) {
    toast(e.message || '进入实验失败', 'error')
  } finally {
    entering.value = false
  }
}

const drawCharts = () => {
  nextTick(() => {
    drawChart(cumVisitsCanvas.value, stats.value.cumulativeVisits, '#1a237e')
    drawChart(cumPracticeCanvas.value, stats.value.cumulativePractice, '#2e7d32')
    drawChart(dailyVisitsCanvas.value, stats.value.dailyVisits, '#e53935')
    drawChart(dailyPracticeCanvas.value, stats.value.dailyPractice, '#ffc107')
  })
}

onMounted(async () => {
  await loadExperiment()
  drawCharts()
})
watch(() => route.params.id, async () => {
  await loadExperiment()
  drawCharts()
})
watch(() => stats.value.totalVisits, () => {
  drawCharts()
})
</script>

<style lang="scss" scoped>
.experiment-page { background: #f5f6fa; min-height: 60vh; }
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.breadcrumb {
  font-size: 13px; color: #999; margin-bottom: 16px;
  a { color: #1a237e; &:hover { text-decoration: underline; } }
}
.loading { text-align: center; padding: 80px; color: #999;
  .spinner { display: inline-block; width: 36px; height: 36px; border: 3px solid #e0e0e0; border-top-color: #1a237e; border-radius: 50%; animation: spin .8s linear infinite; margin-bottom: 12px; }
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; padding: 80px 20px; color: #999; .icon { font-size: 48px; margin-bottom: 12px; } }

.exp-header {
  background: #fff; border-radius: 12px; padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,.06); margin-bottom: 20px;
  display: flex; gap: 20px; align-items: flex-start;
  .exp-cover { width: 220px; height: 155px; border-radius: 8px; overflow: hidden; background: #f5f5f5; display: flex; align-items: center; justify-content: center; font-size: 48px; flex-shrink: 0;
    img { width: 100%; height: 100%; object-fit: cover; }
  }
  .exp-meta { flex: 1; h2 { font-size: 22px; color: #1a237e; margin-bottom: 16px; font-weight: 700; } }
  .btn-enter {
    display: inline-block; padding: 12px 32px; background: #1a237e; color: #fff;
    border: none; border-radius: 8px; font-size: 15px; cursor: pointer; margin-top: 8px;
    box-shadow: 0 2px 8px rgba(26,35,126,.3);
    &:hover { background: #283593; }
    &:disabled { opacity: 0.6; cursor: not-allowed; }
  }
}

.exp-tabs-wrap {
  background: #fff; border-radius: 12px; padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,.06);
  .exp-tabs { display: flex; gap: 0; border-bottom: 2px solid #e8e8e8; margin-bottom: 20px;
    .tab-btn { padding: 12px 24px; font-size: 15px; cursor: pointer; color: #666; margin-bottom: -2px; transition: .2s;
      &:hover { color: #1a237e; }
      &.active { border-bottom: 2px solid #1a237e; color: #1a237e; font-weight: 600; }
    }
  }
}

.stats-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px;
  .stat-box { flex: 1; min-width: 280px; padding: 12px 16px; border-radius: 10px; text-align: center; background: linear-gradient(135deg, #f3e5f5, #ede7f6);
    .stat-label { font-size: 12px; color: #666; }
    .stat-value { font-size: 28px; font-weight: 700; color: #1a237e; margin-top: 4px; }
    .stat-new { font-size: 12px; color: #ff5252; margin-top: 4px; }
    &:last-child { 
      background: linear-gradient(135deg, #e8f5e9, #f1f8e9); 
      .stat-value { color: #2e7d32; } 
      .stat-new { color: #66bb6a; }
    }
  }
}

.charts-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;
  @media(max-width: 768px) { grid-template-columns: 1fr; }
  .chart-box { canvas { width: 100%; border-radius: 8px; border: 1px solid #e0e0e0; } }
  .chart-title { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 8px; }
}

.overview { padding: 8px;
  h3 { font-size: 18px; color: #1a237e; margin-bottom: 12px; }
  p { font-size: 14px; color: #555; line-height: 1.8; }
}
</style>