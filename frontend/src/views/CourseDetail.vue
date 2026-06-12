<template>
  <div class="course-detail-page">
    <div class="container">
      <div class="breadcrumb">
        <router-link to="/">首页</router-link> &gt;
        <router-link to="/courses">全部课程</router-link> &gt;
        <span>{{ course?.curriculumName || '课程详情' }}</span>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>加载课程中...
      </div>

      <div v-else-if="error" class="empty">
        <div class="icon">😵</div>
        <p>加载失败：{{ error }}</p>
      </div>

      <div v-else-if="!course" class="empty">
        <div class="icon">😵</div>
        <p>缺少课程ID</p>
      </div>

      <template v-else>
        <!-- 课程头部 -->
        <div class="course-header">
          <h1>{{ course.curriculumName }}</h1>
          <div class="tags">
            <span>📂 {{ course.classifyName || '未分类' }}</span>
            <span>📊 {{ course.experiments?.length || 0 }} 个实验</span>
            <span :class="{ free: isFree }">{{ isFree ? '🆓 免费' : '💰 付费' }}</span>
          </div>
          <div class="meta">
            <span>📅 创建时间：{{ formatDate(course.createTime || '') }}</span>
          </div>
        </div>

        <!-- 主体 -->
        <div class="course-body">
          <div class="main-content">
            <!-- 章节 -->
            <div class="section-block">
              <div class="section-title">📋 课程章节</div>
              <div v-if="!course.chapters || course.chapters.length === 0" class="empty">暂无章节内容</div>
              <div v-else>
                <div v-for="(ch, ci) in course.chapters" :key="ci" class="chapter-item">
                  <div class="ch-header" @click="toggleChapter(ci)">
                    <span>📌 第{{ ci + 1 }}章：{{ ch.title }}</span>
                    <span class="arrow" :class="{ open: openChapters[ci] }">▶</span>
                  </div>
                  <div class="ch-body" :class="{ open: openChapters[ci] }">
                    <div v-if="!ch.node || ch.node.length === 0" class="ch-empty">暂无课时</div>
                    <div v-for="n in ch.node" :key="n.id" class="lesson" @click="playLesson(n.id)">
                      <span class="play">▶</span>
                      <span>{{ n.title || '课时' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 实验列表 -->
            <div class="section-block">
              <div class="section-title">🎯 实训项目</div>
              <div v-if="!course.experiments || course.experiments.length === 0" class="empty">暂无实训项目</div>
              <div v-else>
                <div v-for="exp in course.experiments" :key="exp.id" class="experiment-card" @click="startExperiment(exp.id)">
                  <div class="exp-icon">
                    <img v-if="getImageUrl(exp.image)" :src="getImageUrl(exp.image)" alt=""
                         @error="($event.target as HTMLImageElement).style.display='none'">
                    <span v-else>🔬</span>
                  </div>
                  <div class="exp-info">
                    <h4>{{ exp.title || '实验' }}</h4>
                    <p>{{ exp.sellPoint || '点击进入实训' }}</p>
                    <div class="exp-price">
                      <span class="price-text">{{ parseFloat(exp.price || 0) <= 0 ? '免费' : '¥' + parseFloat(exp.price).toFixed(2) }}</span>
                      <span v-if="exp.appliId" class="vr-tag">🖥️ 3D仿真</span>
                    </div>
                  </div>
                  <span class="exp-status" :class="(exp.status == 1 || exp.status == '1') ? 'online' : 'offline'">
                    {{ (exp.status == 1 || exp.status == '1') ? '▶ 开始学习' : '⛔ 暂不可用' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧边栏 -->
          <div class="sidebar">
            <div class="price-area">
              <div class="price">
                <span v-if="isFree" class="free">免费</span>
                <span v-else>¥{{ parseFloat(course.price || 0).toFixed(2) }}</span>
              </div>
            </div>
            <button class="btn-buy" @click="enrollCourse(course.id)">📌 加入学习计划</button>
            <div class="info-list">
              <span>🎯 实训项目：{{ course.experiments?.length || 0 }} 个</span>
              <span>📖 课程章节：{{ course.chapters?.length || 0 }} 章</span>
              <span>📅 创建时间：{{ formatDate(course.createTime || '') }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { getCurriculumDetail } from '@/api'
import { getImageUrl, formatDate, toast } from '@/utils'

const route = useRoute()
const router = useRouter()

const course = ref<any>(null)
const loading = ref(true)
const error = ref('')
const openChapters = ref<Record<number, boolean>>({})

const isFree = computed(() => parseFloat(course.value?.price || 0) <= 0)

const toggleChapter = (i: number) => {
  openChapters.value[i] = !openChapters.value[i]
}

const loadCourse = async () => {
  const id = route.params.id as string
  if (!id) { error.value = '缺少课程ID'; loading.value = false; return }

  loading.value = true
  error.value = ''
  try {
    course.value = await getCurriculumDetail(id)
    document.title = (course.value?.curriculumName || '') + ' - 科明365VR教学云平台'
  } catch (e: any) {
    error.value = e.message || '请求失败'
  } finally {
    loading.value = false
  }
}

const enrollCourse = async (id: string | number) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      toast('请先登录', 'error')
      router.push('/login')
      return
    }
    await api.post(`/courses/${id}/enroll/`)
    toast('已加入学习计划', 'success')
  } catch (e: any) {
    toast(e.message || '操作失败', 'error')
  }
}

const startExperiment = (id: string | number) => {
  router.push(`/experiment/${id}`)
}

const playLesson = (id: string | number) => {
  router.push({ path: '/lesson', query: { id: String(id) } })
}

onMounted(loadCourse)
watch(() => route.params.id, loadCourse)
</script>

<style lang="scss" scoped>
.course-detail-page { background: #f5f6fa; min-height: 60vh; }
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.breadcrumb {
  font-size: 13px; color: #999; margin-bottom: 16px;
  a { color: #1a237e; &:hover { text-decoration: underline; } }
}
.loading { text-align: center; padding: 80px; color: #999; font-size: 15px; }
.spinner {
  display: inline-block; width: 36px; height: 36px;
  border: 3px solid #e0e0e0; border-top-color: #1a237e;
  border-radius: 50%; animation: spin .8s linear infinite; margin-bottom: 12px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; padding: 80px 20px; color: #999; .icon { font-size: 48px; margin-bottom: 12px; } }

.course-header {
  background: linear-gradient(135deg, #1a237e, #3949ab);
  border-radius: 16px; padding: 40px; color: #fff; margin-bottom: 24px;
  position: relative; overflow: hidden;
  &::after { content: '🎓'; position: absolute; right: 30px; bottom: -10px; font-size: 120px; opacity: .1; }
  h1 { font-size: 28px; font-weight: 700; margin-bottom: 12px; max-width: 70%; }
  .tags { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap;
    span { padding: 4px 14px; border-radius: 20px; font-size: 12px; background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.2); }
    .free { background: rgba(103,194,58,.3); border-color: rgba(103,194,58,.5); }
  }
  .meta { display: flex; gap: 24px; font-size: 14px; opacity: .8; }
}

.course-body { display: grid; grid-template-columns: 1fr 320px; gap: 24px; align-items: start; }
@media(max-width: 900px) { .course-body { grid-template-columns: 1fr; } }
.main-content { background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,.06); }
.section-block { margin-bottom: 24px; &:last-child { margin-bottom: 0; } }
.section-title {
  font-size: 18px; font-weight: 600; margin-bottom: 16px; padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0; color: #1a237e;
}

.chapter-item { margin-bottom: 4px; border: 1px solid #eef0f4; border-radius: 10px; overflow: hidden;
  &:hover { border-color: #c5cae9; }
  .ch-header {
    padding: 14px 16px; background: #fafbff; cursor: pointer;
    display: flex; align-items: center; justify-content: space-between;
    font-size: 14px; font-weight: 600; color: #1a237e;
    .arrow { transition: transform .2s; font-size: 12px; color: #999; &.open { transform: rotate(90deg); } }
  }
  .ch-body { padding: 0 16px 8px; display: none; &.open { display: block; } }
  .ch-empty { padding: 12px 28px; color: #999; font-size: 13px; }
  .lesson {
    padding: 10px 12px 10px 28px; font-size: 13px; color: #555;
    cursor: pointer; border-radius: 6px; display: flex; align-items: center; gap: 8px;
    &:hover { background: #f5f5f5; color: #1a237e; }
    .play { width: 28px; height: 28px; border-radius: 50%; background: #e8eaf6; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #1a237e; flex-shrink: 0; }
  }
}

.experiment-card {
  display: flex; align-items: center; gap: 16px; padding: 14px 16px;
  border: 1px solid #eef0f4; border-radius: 10px; margin-bottom: 8px;
  cursor: pointer; transition: .2s;
  &:hover { border-color: #c5cae9; background: #fafbff; }
  .exp-icon { width: 60px; height: 45px; border-radius: 4px; overflow: hidden; flex-shrink: 0; background: #f5f5f5; display: flex; align-items: center; justify-content: center; font-size: 22px;
    img { width: 100%; height: 100%; object-fit: cover; }
  }
  .exp-info { flex: 1; h4 { font-size: 14px; font-weight: 600; margin-bottom: 4px; } p { font-size: 12px; color: #999; } }
  .exp-price { margin-top: 4px; .price-text { font-size: 13px; font-weight: 600; color: #1a237e; } .vr-tag { font-size: 11px; color: #67c23a; margin-left: 8px; } }
  .exp-status { padding: 4px 12px; border-radius: 12px; font-size: 12px; flex-shrink: 0;
    &.online { background: #e8f5e9; color: #2e7d32; }
    &.offline { background: #f5f5f5; color: #999; }
  }
}

.sidebar {
  background: #fff; border-radius: 12px; padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,.06); position: sticky; top: 20px;
  .price-area { text-align: center; margin-bottom: 20px; .price { font-size: 32px; font-weight: 700; color: #e53935; .free { color: #67c23a; } } }
  .btn-buy {
    display: block; width: 100%; padding: 14px; background: #1a237e; color: #fff;
    border: none; border-radius: 10px; font-size: 16px; font-weight: 600;
    cursor: pointer; margin-bottom: 16px;
    &:hover { background: #283593; }
  }
  .info-list { font-size: 13px; color: #666; line-height: 2.2;
    span { display: flex; align-items: center; gap: 8px; }
  }
}
</style>
</content>
</invoke>