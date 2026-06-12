<template>
  <div class="container" style="padding-top: 20px;">
    <div class="breadcrumb">
      <router-link to="/">首页</router-link> &gt; 新闻资讯
    </div>

    <div class="page-header">
      <h1>📰 新闻资讯</h1>
      <p>了解科明365VR教学云平台的最新动态</p>
    </div>

    <div class="search-bar">
      <input v-model="search" placeholder="搜索新闻标题..." @keydown.enter="doSearch">
      <button @click="doSearch">🔍 搜索</button>
    </div>

    <div class="news-list">
      <div v-if="loading" class="loading"><div class="spinner"></div>加载中...</div>
      <div v-else-if="error" class="empty"><div class="icon">😵</div><p>{{ error }}</p></div>
      <div v-else-if="news.length === 0" class="empty"><div class="icon">📭</div><p>暂无新闻</p></div>
      <div v-else v-for="n in news" :key="n.id" class="news-item" @click="openDetail(n.id)">
        <div class="thumb">
          <img v-if="n.coverImg" :src="getImageUrl(n.coverImg)" alt=""
               @error="($event.target as HTMLImageElement).style.display='none'">
          <span v-else>📰</span>
        </div>
        <div class="info">
          <div>
            <h3>{{ n.title }}</h3>
            <div class="summary">{{ stripHtml(n.content || '').slice(0, 120) }}</div>
          </div>
          <div class="meta">
            <span>📅 {{ formatDate(n.createTime || n.time || '') }}</span>
            <span>👁️ {{ n.browsetimes || 0 }} 次阅读</span>
          </div>
        </div>
      </div>
    </div>

    <Pagination v-model:page="page" :total="total" :page-size="PAGE_SIZE" @update:page="goPage" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getNews } from '@/api'
import { getImageUrl, stripHtml, formatDate } from '@/utils'
import Pagination from '@/components/Pagination.vue'
import type { NewsItem } from '@/types'

const route = useRoute()
const PAGE_SIZE = 10

const search = ref('')
const page = ref(1)
const total = ref(0)
const news = ref<NewsItem[]>([])
const loading = ref(true)
const error = ref('')

const loadNews = async () => {
  loading.value = true
  error.value = ''
  try {
    const params: Record<string, any> = {
      page: page.value,
      page_size: PAGE_SIZE,
      ordering: '-priority,-time'
    }
    if (search.value) params.search = search.value
    const res = await getNews(params)
    news.value = res.results || []
    total.value = res.count || 0
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const doSearch = () => { page.value = 1; loadNews() }
const goPage = (p: number) => { page.value = p; loadNews(); window.scrollTo({ top: 0, behavior: 'smooth' }) }
const openDetail = (id: string | number) => {
  window.open('/news/' + id, '_blank')
}

onMounted(() => {
  const urlSearch = route.query.search as string
  if (urlSearch) search.value = urlSearch
  loadNews()
})
</script>

<style lang="scss" scoped>
.breadcrumb { font-size: 13px; color: #999; margin-bottom: 16px;
  a { color: #1a237e; &:hover { text-decoration: underline; } }
}
.page-header { text-align: center; padding: 40px 20px 30px;
  h1 { font-size: 28px; color: #1a237e; margin-bottom: 8px; }
  p { font-size: 14px; color: #999; }
}
.search-bar {
  max-width: 500px; margin: -10px auto 30px; display: flex;
  input { flex: 1; padding: 10px 16px; border: 1px solid #ddd; border-radius: 8px 0 0 8px; font-size: 14px; outline: none;
    &:focus { border-color: #1a237e; }
  }
  button { padding: 10px 20px; background: #1a237e; color: #fff; border: none; border-radius: 0 8px 8px 0; font-size: 14px; }
}
.news-list { max-width: 900px; margin: 0 auto; }
.news-item {
  display: flex; gap: 20px; background: #fff; border-radius: 12px;
  padding: 20px; margin-bottom: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06); cursor: pointer; transition: .2s;
  &:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,.1); }
  .thumb {
    width: 180px; height: 120px; border-radius: 8px; overflow: hidden;
    flex-shrink: 0; background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    display: flex; align-items: center; justify-content: center; font-size: 36px;
    img { width: 100%; height: 100%; object-fit: cover; }
  }
  .info {
    flex: 1; display: flex; flex-direction: column; justify-content: space-between;
    h3 { font-size: 16px; font-weight: 600; margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.5;
      &:hover { color: #1a237e; }
    }
    .summary { font-size: 13px; color: #999; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.6; margin-bottom: 8px; }
    .meta { display: flex; gap: 16px; font-size: 12px; color: #bbb; }
  }
}
@media(max-width:768px) {
  .news-item { flex-direction: column;
    .thumb { width: 100%; height: 160px; }
  }
}
</style>
