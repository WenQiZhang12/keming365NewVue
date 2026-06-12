<template>
  <div class="page-wrap">
    <div class="breadcrumb"><router-link to="/">首页</router-link> &gt; <span>全部课程</span></div>
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="row">
        <span class="label">分类：</span>
        <span class="filter-tag" :class="{ active: !state.classifyId }" @click="filterByClassify(null, '')">全部</span>
        <span v-for="c in classifies" :key="c.id" class="filter-tag" :class="{ active: state.classifyId == c.id }"
          :data-id="c.id" @click="filterByClassify(c, c.id)">{{ c.className }}</span>
      </div>
      <div class="row" v-show="showSearch">
        <span class="label">搜索：</span>
        <div class="search-box">
          <input v-model="searchText" placeholder="搜索课程名称..." @keydown.enter="doSearch" />
          <button @click="doSearch">搜索</button>
        </div>
      </div>
    </div>
    <!-- 面包屑导航 -->
    <div class="breadcrumb nav-bc" v-if="navBreadcrumb" v-html="navBreadcrumb"></div>
    <!-- 实验类型切换标签 -->
    <div class="exp-type-tabs" v-if="showExpTypeTabs">
      <div class="resource-mode-btns">
        <button :class="['resource-mode-btn', { active: state.resourceMode === 'ai' }]" @click="switchResourceMode('ai')">AI+VR课程智能体</button>
        <button :class="['resource-mode-btn', { active: state.resourceMode === 'vr' }]" @click="switchResourceMode('vr')">VR资源库</button>
      </div>
      <template v-if="state.resourceMode === 'vr'">
        <div :class="['exp-type-tab', { active: state.expType === '0' }]" @click="switchExpType('0')">实验教学</div>
        <div :class="['exp-type-tab', { active: state.expType === '1' }]" @click="switchExpType('1')">课堂教学</div>
        <template v-if="state.classifyId == '3' || state.classifyId == 3">
          <div :class="['exp-type-tab', { active: state.expType === '4' }]" @click="switchExpType('4')">教学视频</div>
          <div :class="['exp-type-tab', { active: state.expType === '5' }]" @click="switchExpType('5')">典型实景资料</div>
        </template>
        <div v-if="state.classifyId != '50' && state.classifyId != 50"
          :class="['exp-type-tab', { active: state.expType === '3' }]" @click="switchExpType('3')">教学模型</div>
      </template>
    </div>
    <!-- 内容区域 -->
    <div class="course-grid" :class="{ 'ai-vr-layout': state.resourceMode === 'ai' && state.viewMode === 'experiments' && state.curriculumId }">
      <!-- 加载中 -->
      <div v-if="loading" class="loading"><div class="spinner"></div>加载中...</div>
      <!-- 空状态 -->
      <div v-else-if="isEmpty" class="empty"><div class="icon">📭</div><p>{{ emptyText }}</p></div>
      <!-- AI+VR模式 -->
      <template v-else-if="state.resourceMode === 'ai' && state.viewMode === 'experiments' && state.curriculumId">
        <AiVrView :curriculum-name="currentCurriculumName" />
      </template>
      <!-- 分类卡片 -->
      <template v-else-if="state.viewMode === 'allClassifies'">
        <div v-for="c in classifyCards" :key="c.id" class="classify-card" @click="onClassifyCardClick(c)">
          <div class="classify-header">
            <div class="classify-icon">📂</div>
            <h3>{{ c.className }}</h3>
          </div>
          <div class="classify-exps">
            <div v-for="item in c.previewItems" :key="item.id" class="classify-exp-item" @click.stop="onPreviewItemClick(c, item)">
              <span class="exp-dot">●</span>{{ item.label }}
            </div>
            <div class="classify-more" @click.stop="openClassify(c.id)">
              {{ c.isDirectExp ? '更多实验 →' : '更多课程 →' }}
            </div>
          </div>
        </div>
      </template>
      <!-- 课程卡片 -->
      <template v-else-if="state.viewMode === 'curricula'">
        <div v-for="c in curriculaCards" :key="c.id" class="classify-card" @click="showExperiments(c.id, c.curriculumName)">
          <div class="classify-header">
            <div class="classify-icon">🎓</div>
            <h3>{{ c.curriculumName }}</h3>
          </div>
          <div class="classify-exps">
            <div v-if="c.expsLoading" class="loading mini"><div class="spinner small"></div>加载中...</div>
            <template v-else>
              <div v-for="exp in c.exps" :key="exp.id" class="classify-exp-item"
                @click.stop="goExperiment(exp.id, c.curriculumName, 'curriculum')">
                <span class="exp-dot">●</span>{{ exp.title }}
              </div>
              <div class="classify-more" @click.stop="showExperiments(c.id, c.curriculumName)">
                {{ c.exps.length > 0 ? '更多实验 →' : '查看全部 →' }}
              </div>
            </template>
          </div>
        </div>
      </template>
      <!-- 实验卡片 -->
      <template v-else-if="state.viewMode === 'experiments'">
        <div v-for="exp in state.items" :key="exp.id" class="course-card" @click="goExperiment(exp.id, exp.fromName || '', exp.fromParam || '')">
          <div class="thumb">
            <img v-if="exp.imageUrl" :src="exp.imageUrl" @error="($event.target as HTMLImageElement).style.display='none'" />
            <span v-else class="fallback">🔬</span>
          </div>
          <div class="body">
            <h3>{{ exp.title }}</h3>
            <div class="meta"><span>{{ exp.publisher }}</span></div>
          </div>
        </div>
      </template>
    </div>
    <!-- 分页 -->
    <div class="courses-pagination" v-if="showPagination">
      <template v-if="totalPages <= 3">
        <button v-for="i in totalPages" :key="i" :class="{ active: i === state.page }" @click="goPage(i)">{{ i }}</button>
      </template>
      <template v-else>
        <div class="pagi-flex">
          <button :class="{ disabled: state.page <= 1 }" @click="goPage(1)">首页</button>
          <button :class="{ disabled: state.page <= 1 }" @click="goPage(state.page - 1)">上一页</button>
          <span v-if="pagiStart > 1" class="dots">...</span>
          <button v-for="i in pagiRange" :key="i" :class="{ active: i === state.page }" @click="goPage(i)">{{ i }}</button>
          <span v-if="pagiEnd < totalPages" class="dots">...</span>
          <button :class="{ disabled: state.page >= totalPages }" @click="goPage(state.page + 1)">下一页</button>
          <button :class="{ disabled: state.page >= totalPages }" @click="goPage(totalPages)">尾页</button>
          <div class="jump-box">
            <input type="number" v-model.number="jumpPage" :min="1" :max="totalPages" @keydown.enter="doJump" />
            <span>页</span>
            <button class="jump-btn" @click="doJump">跳转</button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCurriculumClassifies, getCurricula, getExperiments, getClassifyExperiments, getCurriculumDetail } from '@/api'
import { getImageUrl, getClassifyIcon } from '@/utils'
import type { Classify, Curriculum, Experiment } from '@/types'
import AiVrView from '@/components/AiVrView.vue'

const route = useRoute()
const router = useRouter()
const PAGE_SIZE = 12
const directExpClassifies = ['大学物理', '能源动力', '生物工程']
const CLASSIFY_ORDER: Record<string, number> = {
  '机械工程': 1, '工程训练': 2, '力学': 3, '土木工程': 4, '装配式建筑': 5,
  '大学物理': 6, '能源动力': 7, '水利工程': 8, '生物工程': 9, '文化艺术': 10, '航海类': 11, '学前教育/康养': 12
}

interface PreviewItem { id: string; label: string }
interface ClassifyCard extends Classify { previewItems: PreviewItem[]; isDirectExp: boolean }
interface CurriculumCard extends Curriculum { exps: { id: string | number; title: string }[]; expsLoading: boolean }
interface ExpItem extends Experiment { imageUrl?: string; fromName?: string; fromParam?: string }

const loading = ref(false)
const isEmpty = ref(false)
const emptyText = ref('')
const searchText = ref('')
const showSearch = ref(true)
const navBreadcrumb = ref('')
const showExpTypeTabs = ref(false)
const classifies = ref<Classify[]>([])
const classifyCards = ref<ClassifyCard[]>([])
const curriculaCards = ref<CurriculumCard[]>([])

const state = reactive({
  classifyId: '' as string | number,
  curriculumId: '' as string | number,
  viewMode: 'allClassifies' as 'allClassifies' | 'curricula' | 'experiments',
  page: 1, search: '', expType: '0', resourceMode: 'vr' as 'vr' | 'ai',
  items: [] as ExpItem[], total: 0, classifies: [] as Classify[]
})

let lastClassifyId: string | number = ''
let currentCurriculumName = ref('')
let currentCurriculumId: string | number = ''
let fromClassifyDirectly = false

const totalPages = computed(() => Math.ceil(state.total / PAGE_SIZE))
const pagiStart = computed(() => Math.max(1, state.page - 2))
const pagiEnd = computed(() => Math.min(totalPages.value, state.page + 2))
const pagiRange = computed(() => { const a: number[] = []; for (let i = pagiStart.value; i <= pagiEnd.value; i++) a.push(i); return a })
const jumpPage = ref(1)

const showPagination = computed(() => {
  if (totalPages.value <= 1) return false
  if (state.resourceMode === 'ai') return false
  if (state.viewMode === 'allClassifies') return false
  return true
})

// === 分类筛选 ===
function filterByClassify(c: Classify | null, id: string | number) {
  state.classifyId = id
  state.curriculumId = ''
  state.page = 1
  state.search = ''
  searchText.value = ''
  if (!id) {
    state.viewMode = 'allClassifies'
  } else {
    const name = c ? c.className : ''
    state.viewMode = directExpClassifies.includes(name) ? 'experiments' : 'curricula'
  }
  navBreadcrumb.value = ''
  showSearch.value = true
  showExpTypeTabs.value = false
  loadContent()
}

function openClassify(cid: string | number) {
  const c = classifies.value.find(x => x.id == cid)
  filterByClassify(c || null, cid)
}

function doSearch() {
  state.search = searchText.value.trim()
  state.page = 1
  state.curriculumId = ''
  state.viewMode = 'experiments'
  showExpTypeTabs.value = false
  loadContent()
}

// === 导航 ===
function showExperiments(curriculumId: string | number, curriculumName: string, fromDirectly = false) {
  lastClassifyId = state.classifyId
  state.curriculumId = curriculumId
  currentCurriculumId = curriculumId
  currentCurriculumName.value = curriculumName || '课程详情'
  state.viewMode = 'experiments'
  state.page = 1
  state.expType = '0'
  state.resourceMode = 'vr'
  fromClassifyDirectly = fromDirectly
  if (fromClassifyDirectly) {
    navBreadcrumb.value = `<a href="javascript:;" onclick="return false">← 返回分类</a> &gt; <span>${currentCurriculumName.value}</span>`
  } else {
    navBreadcrumb.value = `<a href="javascript:;" onclick="return false">返回课程列表</a> &gt; <span>${currentCurriculumName.value}</span>`
  }
  showSearch.value = false
  loadContent()
}

function backToClassifies() {
  state.classifyId = ''
  state.curriculumId = ''
  state.page = 1
  state.viewMode = 'allClassifies'
  state.search = ''
  searchText.value = ''
  navBreadcrumb.value = ''
  showSearch.value = true
  showExpTypeTabs.value = false
  loadContent()
}

function backToCurricula() {
  state.curriculumId = ''
  state.page = 1
  if (lastClassifyId) { state.classifyId = lastClassifyId; state.viewMode = 'curricula' }
  else { state.viewMode = 'allClassifies' }
  navBreadcrumb.value = ''
  showSearch.value = true
  showExpTypeTabs.value = false
  loadContent()
}

// === 模式切换 ===
function switchResourceMode(mode: 'vr' | 'ai') {
  state.resourceMode = mode
  loadContent()
}
function switchExpType(type: string) {
  state.expType = type
  state.page = 1
  loadContent()
}

// === 统一加载 ===
async function loadContent() {
  loading.value = true
  isEmpty.value = false
  if (state.search) { await loadExperiments(); return }
  if (state.viewMode === 'allClassifies') await loadAllClassifies()
  else if (state.curriculumId && state.viewMode === 'experiments') await loadExperiments()
  else if (state.classifyId && state.viewMode === 'experiments') await loadExperiments()
  else if (state.classifyId && state.viewMode === 'curricula') await loadCurricula()
  else { state.viewMode = 'allClassifies'; await loadAllClassifies() }
  loading.value = false
}

// === 加载全部分类卡片 ===
async function loadAllClassifies() {
  showExpTypeTabs.value = false
  try {
    const list = await getCurriculumClassifies()
    list.sort((a, b) => (CLASSIFY_ORDER[a.className] || 999) - (CLASSIFY_ORDER[b.className] || 999))
    classifies.value = list
    state.classifies = list
    const cards: ClassifyCard[] = []
    for (const c of list) {
      const isDirectExp = directExpClassifies.includes(c.className)
      let previewItems: PreviewItem[] = []
      try {
        if (isDirectExp) {
          const ed = await getClassifyExperiments(c.id, 3)
          previewItems = (ed.results || []).map(e => ({ id: String(e.id), label: e.title || '' }))
        } else {
          const cd = await getCurricula({ classifyId: c.id, page_size: 3 })
          previewItems = (cd.results || []).map(cur => ({ id: String(cur.id), label: cur.curriculumName || '' }))
        }
      } catch { /* ignore */ }
      cards.push({ ...c, previewItems, isDirectExp })
    }
    classifyCards.value = cards
    if (cards.length === 0) { isEmpty.value = true; emptyText.value = '暂无分类' }
  } catch (e: any) {
    isEmpty.value = true; emptyText.value = '加载失败：' + (e.message || '')
  }
}

// === 加载课程列表 ===
async function loadCurricula() {
  showExpTypeTabs.value = false
  try {
    const params: any = { page: state.page, page_size: PAGE_SIZE }
    if (state.classifyId) params.classifyId = state.classifyId
    if (state.search) params.search = state.search
    const d = await getCurricula(params)
    const items = d.results || []
    state.total = d.count || 0
    // 单课程自动跳过
    if (items.length === 1 && state.total === 1) {
      loading.value = false
      showExperiments(items[0].id, items[0].curriculumName, true)
      return
    }
    navBreadcrumb.value = '<a href="javascript:;" onclick="return false">← 返回分类</a>'
    const cards: CurriculumCard[] = items.map(c => reactive({ ...c, exps: [], expsLoading: true }))
    curriculaCards.value = cards
    // 异步加载每个课程的实验预览
    cards.forEach(async (card, idx) => {
      try {
        const ed = await getExperiments({ curriculumId: card.id, page_size: 3 })
        card.exps = (ed.results || []).map(e => ({ id: e.id, title: e.title || '' }))
      } catch { card.exps = [] }
      finally { card.expsLoading = false }
    })
  } catch (e: any) {
    isEmpty.value = true; emptyText.value = '加载失败：' + (e.message || '')
  }
}

// === 加载实验列表 ===
async function loadExperiments() {
  try {
    const params: any = { page: state.page, page_size: PAGE_SIZE }
    if (state.search) params.search = state.search
    if (state.classifyId && !state.curriculumId) params.classifyId = state.classifyId
    if (state.curriculumId) params.curriculumId = state.curriculumId
    if (state.expType !== undefined && state.expType !== '') params.type = state.expType
    const d = await getExperiments(params)
    const fromName = state.curriculumId ? currentCurriculumName.value : (state.classifyId ? '分类实验' : '全部课程')
    const fromParam = state.curriculumId ? 'curriculum' : (state.classifyId ? 'classify' : 'courses')
    state.items = (d.results || []).map(e => ({
      ...e, imageUrl: getImageUrl(e.image || ''),
      fromName, fromParam
    }))
    state.total = d.count || 0
    // 面包屑
    if (state.curriculumId) {
      navBreadcrumb.value = `<a href="javascript:;" onclick="return false">返回课程列表</a> &gt; <span>${currentCurriculumName.value}</span>`
    } else if (state.classifyId) {
      const cl = state.classifies.find(c => c.id == state.classifyId)
      const name = cl ? cl.className : ''
      navBreadcrumb.value = `<a href="javascript:;" onclick="return false">← 返回分类</a> &gt; <span>${name}</span>`
    }
    showSearch.value = false
    showExpTypeTabs.value = true
  } catch (e: any) {
    isEmpty.value = true; emptyText.value = '加载失败：' + (e.message || '')
  }
}

// === 点击事件 ===
function onClassifyCardClick(c: ClassifyCard) {
  if (c.isDirectExp) { openClassify(c.id) }
  else if (c.previewItems.length === 1 && !c.isDirectExp) {
    // 只有一个课程时直接进入
    showExperiments(c.previewItems[0].id, c.previewItems[0].label)
  } else { openClassify(c.id) }
}

function onPreviewItemClick(c: ClassifyCard, item: PreviewItem) {
  if (c.isDirectExp) {
    goExperiment(item.id, c.className, 'classify')
  } else {
    showExperiments(item.id, item.label)
  }
}

function goExperiment(id: string | number, fromName: string, fromParam: string) {
  router.push({ 
    path: '/experiment/' + id, 
    query: { 
      from: fromParam || 'curriculum', 
      fromName: encodeURIComponent(fromName || ''),
      classifyId: state.classifyId 
    } 
  })
}

function goPage(p: number) {
  if (p < 1 || p > totalPages.value) return
  state.page = p
  loadContent()
}
function doJump() {
  const p = Number(jumpPage.value)
  if (p >= 1 && p <= totalPages.value && p !== state.page) { state.page = p; loadContent() }
}

// 面包屑点击处理（通过事件委托）
function handleBreadcrumbClick(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (target.tagName === 'A') {
    e.preventDefault()
    const text = target.textContent || ''
    if (text.includes('返回分类')) backToClassifies()
    else if (text.includes('返回课程列表')) backToCurricula()
  }
}

onMounted(() => {
  // 监听面包屑点击
  document.addEventListener('click', (e) => {
    const bc = document.querySelector('.nav-bc')
    if (bc && bc.contains(e.target as Node)) handleBreadcrumbClick(e)
  })
  // URL参数处理
  const urlClassify = route.query.classifyId as string || ''
  const urlCurriculum = route.query.curriculumId as string || ''
  const urlSearch = route.query.search as string || ''
  if (urlSearch) {
    state.search = urlSearch; searchText.value = urlSearch
    state.viewMode = 'experiments'
    loadContent()
  } else if (urlCurriculum) {
    state.curriculumId = urlCurriculum
    state.viewMode = 'experiments'
    getCurriculumDetail(urlCurriculum).then(course => {
      currentCurriculumName.value = course.curriculumName || '课程'
      navBreadcrumb.value = `<a href="javascript:;" onclick="return false">返回课程列表</a> &gt; <span>${currentCurriculumName.value}</span>`
    }).catch(() => {})
    loadContent()
  } else if (urlClassify) {
    // 先检查分类下是否只有一个课程
    getCurricula({ classifyId: urlClassify, page_size: 2 }).then(d => {
      const curricula = d.results || []
      if (curricula.length === 1) {
        state.curriculumId = curricula[0].id
        state.viewMode = 'experiments'
        currentCurriculumName.value = curricula[0].curriculumName || '课程'
        navBreadcrumb.value = `<a href="javascript:;" onclick="return false">← 返回分类</a> &gt; <span>${currentCurriculumName.value}</span>`
        showSearch.value = false
        loadContent()
      } else {
        state.classifyId = urlClassify
        state.viewMode = 'curricula'
        lastClassifyId = urlClassify
        loadAllClassifies().then(() => loadContent())
      }
    }).catch(() => {
      state.classifyId = urlClassify; state.viewMode = 'curricula'; lastClassifyId = urlClassify
      loadContent()
    })
  } else {
    state.viewMode = 'allClassifies'
    loadContent()
  }
})
</script>

<style scoped lang="scss">
.page-wrap { flex: 1; padding: 24px 40px; max-width: 1200px; margin: 0 auto; width: 100%; }
.breadcrumb { font-size: 13px; color: #999; margin-bottom: 16px;
  a { color: #1a237e; text-decoration: none; &:hover { text-decoration: underline; } }
}
.nav-bc { margin-bottom: 12px; }
.filter-bar { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,.06);
  .row { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
  .label { font-size: 13px; color: #666; white-space: nowrap; }
}
.filter-tag { padding: 5px 14px; border-radius: 20px; font-size: 13px; cursor: pointer; border: 1px solid #e0e0e0; background: #fff; color: #666; transition: all .2s;
  &:hover { border-color: #1a237e; color: #1a237e; }
  &.active { background: #1a237e; color: #fff; border-color: #1a237e; }
}
.search-box { display: flex; max-width: 400px;
  input { flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px 0 0 6px; font-size: 13px; outline: none; &:focus { border-color: #1a237e; } }
  button { padding: 8px 14px; background: #1a237e; color: #fff; border: none; border-radius: 0 6px 6px 0; cursor: pointer; font-size: 13px; }
}
.exp-type-tabs { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-bottom: 16px; border-bottom: 2px solid #e0e0e0; padding-bottom: 0; }
.resource-mode-btns { display: flex; gap: 8px; margin-right: 20px; }
.resource-mode-btn { padding: 6px 16px; border-radius: 4px; border: 1px solid #1a237e; background: #fff; color: #1a237e; cursor: pointer; font-size: 13px; transition: all .2s;
  &.active { background: #1a237e; color: #fff; }
}
.exp-type-tab { padding: 10px 20px; cursor: pointer; font-size: 14px; color: #666; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all .2s;
  &.active { color: #1a237e; border-bottom-color: #1a237e; font-weight: 600; }
}
.course-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;
  &.ai-vr-layout { display: block; }
}
.classify-card { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.08); transition: transform .2s, box-shadow .2s; cursor: pointer; padding: 16px;
  &:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,.12); }
}
.classify-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px;
  h3 { font-size: 16px; color: #1a237e; margin: 0; }
}
.classify-icon { font-size: 28px; }
.classify-exps { padding: 4px 0; }
.classify-exp-item { padding: 6px 0; font-size: 13px; color: #555; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: .15s; border-bottom: 1px dashed #f0f0f0;
  &:last-of-type { border-bottom: none; }
  &:hover { color: #1a237e; }
}
.exp-dot { color: #64b5f6; font-size: 8px; }
.classify-more { text-align: right; font-size: 13px; color: #1a237e; margin-top: 8px; cursor: pointer; padding: 4px 0; &:hover { text-decoration: underline; } }
.course-card { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.08); transition: transform .2s, box-shadow .2s; cursor: pointer;
  &:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,.12); }
  .thumb { height: 180px; background: #f0f2f5; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative;
    img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .fallback { font-size: 36px; }
  }
  .body { padding: 14px 16px;
    h3 { font-size: 14px; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .meta { font-size: 12px; color: #999; }
  }
}
.loading { text-align: center; padding: 60px; color: #999; grid-column: 1 / -1;
  &.mini { padding: 10px; }
}
.spinner { display: inline-block; width: 32px; height: 32px; border: 3px solid #e0e0e0; border-top-color: #1a237e; border-radius: 50%; animation: spin .8s linear infinite; margin-bottom: 12px;
  &.small { width: 16px; height: 16px; border-width: 2px; margin-bottom: 0; }
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; padding: 60px; color: #999; font-size: 14px; grid-column: 1 / -1;
  .icon { font-size: 48px; margin-bottom: 12px; }
}
.courses-pagination { display: flex; justify-content: center; gap: 6px; margin: 24px 0;
  button { padding: 6px 12px; border: 1px solid #ddd; border-radius: 4px; background: #fff; cursor: pointer; font-size: 13px; transition: .2s;
    &:hover:not(.disabled) { background: #1a237e; color: #fff; border-color: #1a237e; }
    &.active { background: #1a237e; color: #fff; border-color: #1a237e; }
    &.disabled { opacity: .4; cursor: default; }
  }
  .dots { color: #999; padding: 6px 4px; }
  .pagi-flex { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; justify-content: center; }
  .jump-box { margin-left: 16px; display: flex; align-items: center; gap: 4px;
    input { width: 50px; height: 30px; padding: 0 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; outline: none; text-align: center; }
    span { font-size: 13px; color: #666; }
    .jump-btn { height: 30px; padding: 0 14px; border: 1px solid #1a237e; border-radius: 4px; background: #fff; color: #1a237e; font-size: 13px; cursor: pointer;
      &:hover { background: #1a237e; color: #fff; }
    }
  }
}
@media (max-width: 768px) {
  .page-wrap { padding: 16px; }
  .course-grid { grid-template-columns: 1fr; }
}
</style>
