<template>
  <div class="home">
    <!-- Banner 轮播 -->
    <div class="banner" @mouseenter="hovering = true" @mouseleave="hovering = false">
      <div v-for="(img, idx) in bannerImages" :key="idx"
           class="slide" :class="{ active: idx === bannerIdx }">
        <img :src="img" alt="">
      </div>
      <!-- 搜索框 -->
      <div class="banner-search">
        <input v-model="searchQuery" placeholder="请输入学习资源名称"
               @keydown.enter="doSearch" autocomplete="off">
        <button @click="doSearch">搜索</button>
      </div>
      <div class="dots">
        <span v-for="(_, idx) in bannerImages" :key="idx"
              :class="{ active: idx === bannerIdx }" @click="bannerIdx = idx" />
      </div>
    </div>

    <div class="container">
      <!-- 分类实验展示 -->
      <div v-if="loading" class="loading"><div class="spinner"></div>加载中...</div>
      <div v-else-if="classifyError" class="empty"><div class="icon">😵</div><p>{{ classifyError }}</p></div>
      <div v-else>
        <div v-for="section in classifyData" :key="section.classify.id" class="classify-section">
          <div class="classify-header">
            <div class="classify-header-left">
              <span class="classify-icon">{{ section.icon }}</span>
              <span class="classify-name">{{ section.classify.className }}</span>
            </div>
            <router-link class="classify-more"
              :to="{ path: '/qbkc', query: { classifyId: section.classify.id } }">更多 →</router-link>
          </div>
          <div v-if="section.experiments.length === 0" class="classify-empty">暂无实验</div>
          <div v-else class="experiment-scroll">
            <div v-for="exp in section.experiments" :key="exp.id"
                 class="experiment-card" @click="openExperiment(exp.id)">
              <div class="experiment-thumb">
                <img v-if="getImageUrl(exp.image || '')" :src="getImageUrl(exp.image || '')" loading="lazy"
                     @error="($event.target as HTMLImageElement).style.display='none'">
                <span v-else style="font-size:36px">🔬</span>
              </div>
              <p class="experiment-title" :title="exp.title">{{ exp.title }}</p>
              <p class="experiment-publisher">{{ exp.publisher || '' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 新闻动态 -->
      <div class="section-title">
        <h2>📢 新闻动态</h2>
        <router-link to="/xwzx">更多 →</router-link>
      </div>
      <div class="grid">
        <div v-for="n in newsList" :key="n.id" class="card news-card"
             @click="openNewsDetail(n.id)">
          <div class="thumb">
            <img v-if="n.coverImg || n.image" :src="getImageUrl(n.coverImg || n.image || '')"
                 alt="" @error="($event.target as HTMLImageElement).style.display='none'; ($event.target as HTMLImageElement).parentElement!.innerHTML='📰'">
            <span v-else>📰</span>
            <span class="tag">资讯</span>
          </div>
          <div class="body">
            <h3>{{ n.title }}</h3>
            <div class="summary">{{ stripHtml(n.content || '').slice(0, 60) || '暂无内容' }}</div>
            <div class="meta">
              <span>📅 {{ formatDate(n.createTime || n.time || '') }}</span>
              <span>👁️ {{ n.browsetimes || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-if="newsList.length === 0 && !loading" class="empty"><div class="icon">📭</div><p>暂无新闻</p></div>
    </div>

    <!-- 友情链接 -->
    <div class="friend-link">
      <div class="container">
        <h3 class="link-title">友情链接</h3>
        <div class="link-row">
          <a href="http://www.moe.gov.cn" target="_blank" class="link-item">
            <img src="https://www.keming365.com/images/jyb01.png" alt="教育部">
          </a>
          <a href="http://www.hit.edu.cn" target="_blank" class="link-item">
            <img src="https://www.keming365.com/images/hgd02.png" alt="哈尔滨工业大学">
          </a>
          <a href="http://www.hust.edu.cn" target="_blank" class="link-item">
            <img src="https://www.keming365.com/images/hzkd03.png" alt="华中科技大学">
          </a>
          <a href="http://www.tongji.edu.cn" target="_blank" class="link-item">
            <img src="https://www.keming365.com/images/tjdx04.png" alt="同济大学">
          </a>
          <a href="http://www.hnu.edu.cn" target="_blank" class="link-item">
            <img src="https://www.keming365.com/images/hndx05.png" alt="湖南大学">
          </a>
          <a href="http://www.jlu.edu.cn" target="_blank" class="link-item">
            <img src="https://www.keming365.com/images/jldx06.png" alt="吉林大学">
          </a>
        </div>
        <div class="link-row">
          <a href="http://www.tju.edu.cn" target="_blank" class="link-item">
            <img src="https://www.keming365.com/images/tjdx07.png" alt="天津大学">
          </a>
          <a href="http://www.sdjzu.edu.cn" target="_blank" class="link-item">
            <img src="https://www.keming365.com/images/jd08.png" alt="山东建筑大学">
          </a>
          <a href="http://www.zju.edu.cn" target="_blank" class="link-item">
            <img src="https://www.keming365.com/images/zjdx09.png" alt="浙江大学">
          </a>
          <a href="http://www.csu.edu.cn" target="_blank" class="link-item">
            <img src="https://www.keming365.com/images/zndx10.png" alt="中南大学">
          </a>
          <a href="http://www.sdu.edu.cn" target="_blank" class="link-item">
            <img src="https://www.keming365.com/images/sddx11.png" alt="山东大学">
          </a>
        </div>
      </div>
    </div>

    <!-- 底部 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-left">
          <div class="footer-logo">
            <img src="https://www.keming365.com/images/footer_logo.png" alt="科明 365">
          </div>
        </div>
        <div class="footer-right">
          <div class="qrcode-item">
            <img src="https://keming365.com/images/二维码.png" alt="公众号二维码">
          </div>
        </div>
      </div>
      <div class="footer-copyright">
        <p>© 2015-2026 济南科明数码技术股份有限公司版权所有</p>
        <p>鲁 ICP 备 14017714 号 -1 | 🛡️ 鲁公网安备 37010202000872 号</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getClassifies, getClassifyExperiments, getNews } from '@/api'
import { getImageUrl, getClassifyIcon, stripHtml, formatDate } from '@/utils'
import type { Classify, Experiment, NewsItem } from '@/types'

const router = useRouter()

// Banner
const bannerImages = [
  'https://www.keming365.com/img/001.png',
  'https://www.keming365.com/img/002.png',
  'https://www.keming365.com/img/003.png',
]
const bannerIdx = ref(0)
const hovering = ref(false)
let bannerTimer: ReturnType<typeof setInterval> | null = null

// Search
const searchQuery = ref('')
const doSearch = () => {
  if (!searchQuery.value.trim()) return
  router.push({ path: '/courses', query: { search: searchQuery.value.trim() } })
}

// Classify data
interface ClassifySection {
  classify: Classify
  experiments: Experiment[]
  icon: string
}
const classifyData = ref<ClassifySection[]>([])
const loading = ref(true)
const classifyError = ref('')

// News
const newsList = ref<NewsItem[]>([])

const openExperiment = (id: string | number) => {
  router.push('/experiment/' + id)
}
const openNewsDetail = (id: string | number) => {
  window.open('/news/' + id, '_blank')
}

onMounted(async () => {
  // Start banner timer
  bannerTimer = setInterval(() => {
    if (!hovering.value) bannerIdx.value = (bannerIdx.value + 1) % bannerImages.length
  }, 4000)

  // Load data in parallel
  try {
    const [classifies, newsRes] = await Promise.all([
      getClassifies(),
      getNews({ page: 1, page_size: 6 })
    ])
    newsList.value = newsRes.results || []

    // Load experiments for each classify
    const sections = await Promise.all(
      classifies.map(async (c) => {
        try {
          const res = await getClassifyExperiments(c.id, 5)
          return { classify: c, experiments: res.results || [], icon: getClassifyIcon(c.className) }
        } catch {
          return { classify: c, experiments: [], icon: getClassifyIcon(c.className) }
        }
      })
    )
    classifyData.value = sections
  } catch (e: any) {
    classifyError.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
})

onUnmounted(() => { if (bannerTimer) clearInterval(bannerTimer) })
</script>

<style lang="scss" scoped>
.banner {
  position: relative; height: 549px; overflow: hidden; background: #1a237e;
  .slide { position: absolute; inset: 0; opacity: 0; transition: opacity .8s;
    &.active { opacity: 1; }
    img { width: 100%; height: 100%; object-fit: cover; display: block; }
  }
  .banner-search {
    position: absolute; bottom: 80px; left: 50%; transform: translateX(-50%);
    display: flex; max-width: 700px; width: 90%;
    input {
      flex: 1; padding: 14px 24px; border: none;
      border-radius: 30px 0 0 30px; font-size: 15px; outline: none;
      box-shadow: 0 4px 20px rgba(0,0,0,.15);
    }
    button {
      padding: 14px 32px; background: #1a237e; color: #fff;
      border: none; border-radius: 0 30px 30px 0; font-size: 15px;
      &:hover { background: #283593; }
    }
  }
  .dots {
    position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 8px;
    span {
      width: 10px; height: 10px; border-radius: 50%;
      background: rgba(255,255,255,.4); cursor: pointer;
      &.active { background: #fff; width: 28px; border-radius: 5px; }
    }
  }
}
.search-bar { display: none; }
.classify-section { margin-bottom: 28px; }
.classify-header {
  display: flex; align-items: center; justify-content: space-between;
  height: 36px; margin-bottom: 14px;
}
.classify-header-left { display: flex; align-items: center; gap: 10px; }
.classify-icon { font-size: 22px; }
.classify-name { font-size: 20px; font-weight: bold; color: #111; }
.classify-more { font-size: 13px; color: #1a237e; white-space: nowrap; &:hover { text-decoration: underline; } }
.classify-empty { color: #ccc; font-size: 13px; padding: 20px 0; text-align: center; }
.experiment-scroll {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 24px;
}
.experiment-card {
  background: #fff; border-radius: 8px; overflow: hidden;
  box-shadow: 0 1px 6px rgba(0,0,0,.08); cursor: pointer; transition: .2s;
  &:hover { transform: translateY(-3px); box-shadow: 0 4px 16px rgba(0,0,0,.12); }
}
.experiment-thumb {
  width: 100%; height: 130px; overflow: hidden;
  background: #f0f2f5;
  display: flex; align-items: center; justify-content: center;
  img { width: 100%; height: 100%; object-fit: cover; display: block; }
}
.experiment-title {
  font-size: 14px; color: #111; padding: 8px 10px 2px;
  overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
}
.experiment-publisher {
  font-size: 12px; color: #999; padding: 0 10px 8px;
  overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
}
.section-title {
  display: flex; justify-content: space-between; align-items: center; margin: 24px 0 16px;
  h2 { font-size: 20px; color: #1a237e; }
  a { font-size: 13px; color: #999; }
}
.grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px; margin-bottom: 40px;
}
.card {
  background: #fff; border-radius: 12px; overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,.08); cursor: pointer; transition: .2s;
  &:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,.12); }
  .thumb {
    height: 150px; background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    display: flex; align-items: center; justify-content: center;
    font-size: 42px; position: relative;
    img { width: 100%; height: 100%; object-fit: cover; }
    .tag { position: absolute; top: 10px; left: 10px; background: rgba(26,35,126,.8); color: #fff; font-size: 11px; padding: 3px 10px; border-radius: 4px; }
  }
  .body {
    padding: 14px 16px 16px;
    h3 { font-size: 15px; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.4; min-height: 42px; }
    .summary { font-size: 13px; color: #999; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-top: 4px; line-height: 1.5; }
    .meta { font-size: 12px; color: #999; display: flex; gap: 12px; margin-top: 4px; }
  }
}
@media(max-width:768px) {
  .banner { height: 340px; }
  .grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); }
  .experiment-scroll { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .classify-name { font-size: 16px; }
}

.friend-link {
  background: linear-gradient(135deg, #e8f4fd, #f0f8ff);
  padding: 30px 0;
  position: relative;
  overflow: hidden;
  &::before {
    content: 'FRIENDLY LINK';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 80px;
    font-weight: 700;
    color: rgba(0,0,0,.03);
    white-space: nowrap;
    pointer-events: none;
    letter-spacing: 8px;
    z-index: 0;
  }
  .container { position: relative; z-index: 1; }
  .link-title {
    text-align: center;
    font-size: 20px;
    color: #1a237e;
    font-weight: 600;
    margin-bottom: 24px;
    position: relative;
    &::after {
      content: '';
      position: absolute;
      bottom: -8px;
      left: 50%;
      transform: translateX(-50%);
      width: 40px;
      height: 3px;
      background: #1a237e;
      border-radius: 2px;
    }
  }
  .link-row {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-bottom: 16px;
    @media(max-width: 992px) { flex-wrap: wrap; }
  }
  .link-item {
    background: #fff;
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
    transition: .2s;
    &:hover { transform: translateY(-2px); box-shadow: 0 2px 8px rgba(0,0,0,.1); }
    img { width: auto; height: 95px; object-fit: contain; }
  }
}

.footer {
  background: #1a237e;
  padding: 40px 30px 0;
  .footer-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    max-width: 1200px;
    margin: 0 auto;
    padding-bottom: 30px;
    @media(max-width: 768px) { flex-direction: column; align-items: center; gap: 20px; text-align: center; }
  }
  .footer-left {
    .footer-logo {
      display: flex;
      align-items: flex-end;
      margin-top: 27px;
      img { width: auto; height: 80px; }
    }
  }
  .footer-right {
    display: flex;
    gap: 40px;
    .qrcode-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      img { width: auto; height: 140px; border-radius: 0; }
      span { font-size: 13px; color: rgba(255,255,255,.8); }
    }
  }
  .footer-copyright {
    border-top: 1px solid rgba(255,255,255,.15);
    text-align: center;
    padding: 16px 0;
    margin-top: 20px;
    p { font-size: 12px; color: rgba(255,255,255,.6); line-height: 1.8; }
  }
}
</style>
