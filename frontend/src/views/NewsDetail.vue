<template>
  <div class="news-detail-page">
    <div class="container">
      <div class="back-row">
        <router-link to="/xwzx">← 返回新闻列表</router-link>
      </div>
      <div class="breadcrumb">
        <router-link to="/">首页</router-link> &gt;
        <router-link to="/xwzx">新闻资讯</router-link> &gt;
        <span>{{ news?.title || '新闻详情' }}</span>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>加载中...
      </div>

      <div v-else-if="error" class="empty">
        <div class="icon">😵</div>
        <p>加载失败：{{ error }}</p>
      </div>

      <div v-else-if="news" class="article">
        <h1>{{ news.title }}</h1>
        <div class="meta">
          <span>📅 {{ formatDate(news.createTime || news.time || '') }}</span>
          <span>👁️ {{ news.browsetimes || 0 }} 次阅读</span>
        </div>
        <div v-if="news.coverImg" class="cover">
          <img :src="getImageUrl(news.coverImg)" :alt="news.title"
               @error="($event.target as HTMLImageElement).style.display='none'" />
        </div>
        <div v-else class="cover">
          <div class="placeholder">📰</div>
        </div>
        <div class="content" v-html="htmlContent"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getNewsDetail } from '@/api'
import { getImageUrl, formatDate } from '@/utils'
import type { NewsItem } from '@/types'

const route = useRoute()
const news = ref<NewsItem | null>(null)
const loading = ref(true)
const error = ref('')

const htmlContent = computed(() => {
  const content = news.value?.content || ''
  return content
    .replace(/\n/g, '</p><p>')
    .replace(/<p><\/p>/g, '<p><br></p>')
})

const loadNews = async () => {
  const id = route.params.id as string
  if (!id) { error.value = '缺少新闻ID'; loading.value = false; return }

  loading.value = true
  error.value = ''
  try {
    news.value = await getNewsDetail(id)
    document.title = (news.value?.title || '') + ' - 科明365VR教学云平台'
  } catch (e: any) {
    error.value = e.message || '请求失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadNews)
watch(() => route.params.id, loadNews)
</script>

<style lang="scss" scoped>
.news-detail-page {
  background: #f5f6fa; min-height: 60vh;
}
.container { max-width: 900px; margin: 0 auto; padding: 20px; }
.breadcrumb {
  font-size: 13px; color: #999; margin-bottom: 20px;
  a { color: #1a237e; &:hover { text-decoration: underline; } }
}
.back-row {
  margin-bottom: 16px;
  a {
    padding: 8px 20px; border: 1px solid #ddd; border-radius: 20px;
    font-size: 13px; color: #666; cursor: pointer; transition: .2s;
    background: #fff; text-decoration: none;
    &:hover { color: #1a237e; border-color: #1a237e; }
  }
}
.article {
  background: #fff; border-radius: 12px; padding: 40px;
  box-shadow: 0 2px 12px rgba(0,0,0,.06);
  h1 { font-size: 26px; font-weight: 700; color: #1a237e; margin-bottom: 16px; line-height: 1.4; }
  .meta {
    display: flex; gap: 20px; font-size: 13px; color: #999;
    margin-bottom: 24px; padding-bottom: 20px;
    border-bottom: 1px solid #f0f0f0; flex-wrap: wrap;
    span { display: flex; align-items: center; gap: 6px; }
  }
  .cover {
    margin-bottom: 24px; border-radius: 8px; overflow: hidden; max-height: 400px;
    img { width: 100%; height: auto; object-fit: cover; }
    .placeholder {
      height: 200px; background: linear-gradient(135deg, #e3f2fd, #bbdefb);
      display: flex; align-items: center; justify-content: center;
      font-size: 48px; border-radius: 8px;
    }
  }
  .content {
    font-size: 15px; line-height: 1.9; color: #444;
    :deep(p) { margin-bottom: 16px; }
    :deep(img) { max-width: 100%; border-radius: 8px; margin: 16px 0; }
  }
}
.loading {
  text-align: center; padding: 80px; color: #999; font-size: 15px;
  .spinner {
    display: inline-block; width: 36px; height: 36px;
    border: 3px solid #e0e0e0; border-top-color: #1a237e;
    border-radius: 50%; animation: spin .8s linear infinite; margin-bottom: 12px;
  }
}
.empty {
  text-align: center; padding: 80px; color: #999;
  .icon { font-size: 48px; margin-bottom: 12px; }
}
@keyframes spin { to { transform: rotate(360deg) } }

@media(max-width:768px) {
  .article { padding: 20px; h1 { font-size: 20px; } }
}
</style>
