<template>
  <div class="lesson-page">
    <div class="container">
      <div class="breadcrumb">
        <router-link to="/">首页</router-link> &gt;
        <router-link to="/courses">全部课程</router-link> &gt;
        <span>{{ lesson?.title || '课时' }}</span>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>加载课时中...
      </div>

      <div v-else-if="error" class="empty">
        <div class="icon">😵</div>
        <p>{{ error }}</p>
      </div>

      <div v-else-if="lesson" class="lesson-content">
        <h1>{{ lesson.title }}</h1>
        <div class="lesson-meta">
          <span>📅 {{ formatDate(lesson.createTime || '') }}</span>
        </div>

        <div v-if="lesson.videoUrl" class="video-wrap">
          <video :src="lesson.videoUrl" controls></video>
        </div>

        <div v-if="lesson.content" class="lesson-body" v-html="lesson.content"></div>
      </div>

      <div v-else class="empty">
        <div class="icon">😵</div>
        <p>缺少课时ID</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import { formatDate } from '@/utils'

const route = useRoute()
const lesson = ref<any>(null)
const loading = ref(true)
const error = ref('')

const loadLesson = async () => {
  const id = route.query.id as string
  const chapterId = route.query.chapter as string
  if (!id && !chapterId) { error.value = '缺少课时ID'; loading.value = false; return }

  loading.value = true
  error.value = ''
  try {
    if (id) {
      lesson.value = await api.get(`/courses/lessons/${id}/`)
    } else {
      lesson.value = await api.get(`/courses/chapters/${chapterId}/lessons/`)
    }
    document.title = (lesson.value?.title || '课时') + ' - 科明365VR教学云平台'
  } catch (e: any) {
    error.value = e.message || '请求失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadLesson)
watch(() => route.query.id, loadLesson)
</script>

<style lang="scss" scoped>
.lesson-page { background: #f5f6fa; min-height: 60vh; }
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.breadcrumb { font-size: 13px; color: #999; margin-bottom: 16px; a { color: #1a237e; &:hover { text-decoration: underline; } } }
.loading { text-align: center; padding: 80px; color: #999;
  .spinner { display: inline-block; width: 36px; height: 36px; border: 3px solid #e0e0e0; border-top-color: #1a237e; border-radius: 50%; animation: spin .8s linear infinite; margin-bottom: 12px; }
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; padding: 80px 20px; color: #999; .icon { font-size: 48px; margin-bottom: 12px; } }
.lesson-content { background: #fff; border-radius: 12px; padding: 40px; box-shadow: 0 2px 12px rgba(0,0,0,.06);
  h1 { font-size: 26px; color: #1a237e; margin-bottom: 12px; }
  .lesson-meta { color: #999; font-size: 13px; margin-bottom: 24px; }
  .video-wrap { margin-bottom: 24px; video { width: 100%; border-radius: 8px; background: #000; } }
  .lesson-body { line-height: 1.8; color: #333; font-size: 15px; :deep(p) { margin-bottom: 12px; } :deep(img) { max-width: 100%; border-radius: 6px; } }
}
</style>