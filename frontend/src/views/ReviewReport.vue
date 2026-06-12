<template>
  <div class="review-page">
    <div class="container">
      <div class="breadcrumb">
        <router-link to="/">首页</router-link> &gt;
        <router-link to="/teacher-reports">教师报告</router-link> &gt;
        <span>评阅报告</span>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>加载中...
      </div>

      <div v-else-if="error" class="empty">
        <div class="icon">😵</div>
        <p>{{ error }}</p>
      </div>

      <template v-else-if="report">
        <div class="report-header">
          <h1>📋 {{ report.experimentName || '实验报告' }}</h1>
          <p>学生：{{ report.studentName || '-' }} | 时间：{{ formatDate(report.createTime || '') }}</p>
        </div>

        <div class="report-grid">
          <div class="main-content">
            <div v-for="(sec, i) in sections" :key="i" class="section-block">
              <h3>{{ sec.title }}</h3>
              <div v-if="sec.type === 'score'">
                <div class="big-score">{{ report.reportScore || '-' }}</div>
                <p class="hint">满分100分</p>
              </div>
              <div v-else-if="sec.type === 'steps' && report.steps" class="steps-list">
                <div v-for="(step, idx) in report.steps" :key="idx" class="step-item">
                  <div class="step-num">{{ idx + 1 }}</div>
                  <div class="step-content">
                    <h4>{{ step.title || '步骤' }}</h4>
                    <p>{{ step.content || '' }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="text-content">{{ sec.getValue() }}</div>
            </div>

            <div class="action-bar">
              <textarea v-model="teacherComment" placeholder="评阅意见..." class="comment-area"></textarea>
              <div class="action-buttons">
                <input v-model.number="newScore" type="number" min="0" max="100" class="score-input" placeholder="分数">
                <button class="btn-pass" @click="submitReview(1)">✅ 通过</button>
                <button class="btn-reject" @click="submitReview(0)">❌ 驳回</button>
              </div>
            </div>
          </div>

          <div class="sidebar">
            <h3>📊 报告信息</h3>
            <div class="info-card">
              <div class="info-row"><span>报告ID</span><b>{{ report.id }}</b></div>
              <div class="info-row"><span>学生</span><b>{{ report.studentName || '-' }}</b></div>
              <div class="info-row"><span>实验</span><b>{{ report.experimentName || '-' }}</b></div>
              <div class="info-row"><span>用时</span><b>{{ report.totalTime || '-' }} 分钟</b></div>
              <div class="info-row"><span>提交时间</span><b>{{ formatDate(report.createTime || '') }}</b></div>
              <div class="info-row"><span>得分</span><b class="big">{{ report.reportScore || '待评' }}</b></div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { formatDate, toast } from '@/utils'

const route = useRoute()
const router = useRouter()
const report = ref<any>(null)
const loading = ref(true)
const error = ref('')
const teacherComment = ref('')
const newScore = ref<number | null>(null)

const sections = [
  { title: '📊 报告得分', type: 'score', getValue: () => '' },
  { title: '📝 实验总结', type: 'text', getValue: () => report.value?.summary || '未填写' },
  { title: '🔬 操作步骤', type: 'steps', getValue: () => '' },
  { title: '💭 心得体会', type: 'text', getValue: () => report.value?.reflection || '未填写' }
]

const loadReport = async () => {
  const id = route.params.id as string
  if (!id) { error.value = '缺少报告ID'; loading.value = false; return }

  loading.value = true
  error.value = ''
  try {
    report.value = await api.get(`/scores/reports/${id}/`)
    document.title = '评阅报告 - 科明365VR教学云平台'
  } catch (e: any) {
    error.value = e.message || '请求失败'
  } finally {
    loading.value = false
  }
}

const submitReview = async (status: number) => {
  const token = localStorage.getItem('token')
  if (!token) {
    toast('请先登录', 'error')
    router.push('/login')
    return
  }
  try {
    await api.post(`/scores/reports/${report.value.id}/review/`, {
      status, comment: teacherComment.value, score: newScore.value
    })
    toast(status === 1 ? '已通过' : '已驳回', 'success')
    router.push('/teacher-reports')
  } catch (e: any) {
    toast(e.message || '评阅失败', 'error')
  }
}

onMounted(loadReport)
watch(() => route.params.id, loadReport)
</script>

<style lang="scss" scoped>
.review-page { background: #f5f6fa; min-height: 60vh; }
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.breadcrumb { font-size: 13px; color: #999; margin-bottom: 16px; a { color: #1a237e; } }

.loading { text-align: center; padding: 80px; color: #999;
  .spinner { display: inline-block; width: 36px; height: 36px; border: 3px solid #e0e0e0; border-top-color: #1a237e; border-radius: 50%; animation: spin .8s linear infinite; margin-bottom: 12px; }
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; padding: 80px 20px; color: #999; .icon { font-size: 48px; margin-bottom: 12px; } }

.report-header { text-align: center; padding: 30px 20px;
  h1 { font-size: 26px; color: #1a237e; margin-bottom: 8px; }
  p { font-size: 14px; color: #999; }
}

.report-grid { display: grid; grid-template-columns: 1fr 300px; gap: 24px; align-items: start;
  @media(max-width: 900px) { grid-template-columns: 1fr; }
}

.main-content { background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,.06); }
.section-block { margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #eef0f4; &:last-child { border-bottom: none; }
  h3 { font-size: 17px; color: #1a237e; margin-bottom: 12px; }
  .text-content { font-size: 14px; color: #555; line-height: 1.8; }
  .big-score { font-size: 60px; font-weight: 700; color: #1a237e; text-align: center; padding: 20px; }
  .hint { text-align: center; font-size: 13px; color: #999; }
  .steps-list .step-item { display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid #f5f5f5;
    .step-num { width: 32px; height: 32px; border-radius: 50%; background: #e8eaf6; color: #1a237e; display: flex; align-items: center; justify-content: center; font-weight: 600; flex-shrink: 0; }
    .step-content { flex: 1; h4 { font-size: 14px; margin-bottom: 4px; } p { font-size: 13px; color: #666; line-height: 1.6; } }
  }
}

.action-bar { background: #fafbff; padding: 16px; border-radius: 8px; margin-top: 16px;
  .comment-area { width: 100%; min-height: 80px; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; font-family: inherit; resize: vertical; outline: none;
    &:focus { border-color: #1a237e; }
  }
  .action-buttons { display: flex; gap: 8px; margin-top: 12px;
    .score-input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; width: 80px; }
    .btn-pass, .btn-reject { padding: 8px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; color: #fff; }
    .btn-pass { background: #67c23a; }
    .btn-reject { background: #e53935; margin-left: auto; }
  }
}

.sidebar { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,.06);
  h3 { font-size: 16px; color: #1a237e; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid #eef0f4; }
  .info-card { .info-row { display: flex; justify-content: space-between; padding: 8px 0; font-size: 13px; span { color: #999; } b { color: #333; } .big { font-size: 16px; color: #1a237e; } } }
}
</style>