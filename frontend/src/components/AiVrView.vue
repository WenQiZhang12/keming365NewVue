<template>
  <div class="ai-vr-container">
    <!-- 无数据 -->
    <div v-if="!courseData" class="no-data">
      <div class="icon">🏗️</div>
      <h2>AI+VR课程智能体</h2>
      <p>该课程的AI+VR内容正在建设中，敬请期待...</p>
    </div>
    <!-- 有数据 -->
    <template v-else>
      <div class="ai-vr-left">
        <div class="tree-header">
          <div class="tree-title">📑 目录</div>
          <span class="badge">免费试用</span>
        </div>
        <div class="tree-divider"></div>
        <div class="ai-tree">
          <div v-for="(chapter, ci) in courseData.chapters" :key="ci"
            :class="['ai-tree-chapter', { open: openChapters.has(ci) }]">
            <div class="ai-tree-chapter-title" :style="chapterHasContent(chapter) ? 'font-weight:600' : ''"
              @click="toggleChapter(ci)">{{ chapter.title }}</div>
            <div class="ai-tree-children">
              <div v-for="(section, si) in chapter.children" :key="si"
                :class="['ai-tree-section', { open: openSections.has(ci + '-' + si) }]">
                <div class="ai-tree-section-title" :style="hasContent(section) ? 'font-weight:600' : ''"
                  @click="toggleSection(ci, si)">{{ section.title }}</div>
                <div class="ai-tree-modules">
                  <div v-for="mod in itemModules" :key="mod.name" class="ai-tree-module">
                    <div class="ai-tree-module-title">{{ mod.name }}</div>
                    <div class="ai-tree-items">
                      <div v-for="fun in mod.children" :key="fun.type"
                        :class="['ai-tree-item', { active: activeResource?.ci === ci && activeResource?.si === si && activeResource?.type === fun.type }]"
                        @click="loadResource(fun.type, section.title, ci, si)">{{ fun.name }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="ai-vr-right">
        <!-- 课程简介 -->
        <div v-show="showIntro">
          <div class="intro-title">{{ courseData.intro.title }}</div>
          <div class="intro-content" v-html="courseData.intro.content"></div>
          <div class="intro-subtitle">授课目标</div>
          <ul class="intro-list"><li v-for="(g, i) in courseData.intro.goals" :key="i">{{ g }}</li></ul>
          <div class="intro-subtitle">参考资料</div>
          <ul class="intro-list"><li v-for="(r, i) in courseData.intro.references" :key="i">{{ r }}</li></ul>
        </div>
        <!-- 资源展示 -->
        <div v-show="!showIntro" class="resource-area">
          <div class="resource-title">{{ resourceTitle }}</div>
          <!-- VR资源卡片 -->
          <div v-if="vrUrls.length > 0" class="vr-cards">
            <div v-for="(url, idx) in vrUrls" :key="idx" class="vr-card" @click="openVr(url)">
              <div class="vr-icon">🥽</div>
              <div class="vr-label">VR资源 {{ idx + 1 }}</div>
            </div>
          </div>
          <!-- iframe -->
          <iframe v-else-if="iframeUrl" :src="iframeUrl" class="resource-iframe"></iframe>
          <!-- 建设中 -->
          <div v-else class="build-tip">该内容正在建设中</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { aiVrCourseData, itemModules, hasContent, RESOURCE_TYPE_NAMES } from '@/data/aiVrCourses'
import type { AiVrChapter } from '@/data/aiVrCourses'

const props = defineProps<{ curriculumName: string }>()

const courseData = computed(() => aiVrCourseData[props.curriculumName] || null)
const showIntro = ref(true)
const resourceTitle = ref('')
const iframeUrl = ref('')
const vrUrls = ref<string[]>([])
const openChapters = ref(new Set<number>())
const openSections = ref(new Set<string>())
const activeResource = ref<{ ci: number; si: number; type: string } | null>(null)

function chapterHasContent(chapter: AiVrChapter): boolean {
  return chapter.children.some(s => hasContent(s))
}

function toggleChapter(ci: number) {
  const s = new Set(openChapters.value)
  s.has(ci) ? s.delete(ci) : s.add(ci)
  openChapters.value = s
}

function toggleSection(ci: number, si: number) {
  const key = ci + '-' + si
  const s = new Set(openSections.value)
  s.has(key) ? s.delete(key) : s.add(key)
  openSections.value = s
  showIntro.value = true
  iframeUrl.value = ''
  vrUrls.value = []
}

function loadResource(type: string, sectionTitle: string, ci: number, si: number) {
  if (!courseData.value) return
  const section = courseData.value.chapters[ci].children[si]
  showIntro.value = false
  activeResource.value = { ci, si, type }
  resourceTitle.value = sectionTitle + ' - ' + (RESOURCE_TYPE_NAMES[type] || type)
  iframeUrl.value = ''
  vrUrls.value = []

  if (type === 'vr') {
    if (section.vrUrl && section.vrUrl.trim()) {
      vrUrls.value = section.vrUrl.split(';').filter(u => u.trim())
    }
  } else if (type === 'ppt') {
    if (section.pptUrl && section.pptUrl.trim()) {
      iframeUrl.value = 'https://view.officeapps.live.com/op/embed.aspx?src=' + encodeURIComponent(section.pptUrl)
    }
  } else if (type === 'correct') {
    iframeUrl.value = location.protocol + '//' + location.host + '/sdxx/correct.html'
  } else if (type === 'ai') {
    iframeUrl.value = 'https://www.keming365.com/ai/index.html#/chapter?lessonId=2'
  } else {
    const url = (section as any)[type + 'Url']
    if (url && url.trim()) iframeUrl.value = url
  }
}

function openVr(url: string) { window.open(url.trim(), '_blank') }

onMounted(() => {
  if (courseData.value) {
    courseData.value.chapters.forEach((ch, ci) => {
      if (ch.defaultOpen) openChapters.value.add(ci)
      ch.children.forEach((sec, si) => {
        if (sec.defaultOpen) openSections.value.add(ci + '-' + si)
      })
    })
  }
})
</script>

<style scoped>
.ai-vr-container { display: flex; gap: 20px; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.08); min-height: 800px; width: 100%; }
.no-data { padding: 80px 20px; text-align: center; width: 100%; }
.no-data .icon { font-size: 48px; margin-bottom: 20px; }
.no-data h2 { color: #1a237e; margin-bottom: 16px; }
.no-data p { color: #999; font-size: 16px; }
.ai-vr-left { width: 320px; flex-shrink: 0; border-right: 1px solid #e8e8e8; overflow-y: auto; max-height: 800px; background: #fafbfc; }
.ai-vr-right { flex: 1; padding: 24px; overflow-y: auto; max-height: 800px; min-width: 0; word-wrap: break-word; }
.tree-header { padding: 12px 15px; display: flex; align-items: center; justify-content: space-between; }
.tree-title { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: bold; }
.badge { background: #1a237e; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.tree-divider { height: 1px; background: #eee; margin: 0 12px 10px; }
.ai-tree-chapter { margin-bottom: 4px; }
.ai-tree-chapter-title { padding: 10px 15px; cursor: pointer; font-size: 14px; color: #333; transition: .2s; border-radius: 4px; margin: 0 8px; white-space: normal; line-height: 1.4; }
.ai-tree-chapter-title:hover { background: #f5f6fa; color: #1a237e; }
.ai-tree-chapter.open > .ai-tree-chapter-title { background: #e8eaf6; color: #1a237e; }
.ai-tree-children { display: none; padding-left: 8px; }
.ai-tree-chapter.open > .ai-tree-children { display: block; }
.ai-tree-section { margin-bottom: 2px; }
.ai-tree-section-title { padding: 8px 15px 8px 24px; cursor: pointer; font-size: 13px; color: #555; transition: .2s; border-radius: 4px; margin: 0 8px; white-space: normal; line-height: 1.4; }
.ai-tree-section-title:hover { background: #f5f6fa; color: #1a237e; }
.ai-tree-section.open > .ai-tree-section-title { background: #e3f2fd; color: #1565c0; }
.ai-tree-modules { display: none; padding-left: 16px; }
.ai-tree-section.open > .ai-tree-modules { display: block; }
.ai-tree-module { margin-bottom: 4px; }
.ai-tree-module-title { padding: 6px 15px 6px 32px; font-size: 12px; color: #888; font-weight: 600; }
.ai-tree-items { padding-left: 40px; }
.ai-tree-item { padding: 5px 12px; cursor: pointer; font-size: 12px; color: #666; transition: .2s; border-radius: 4px; margin: 2px 0; }
.ai-tree-item:hover { background: #f5f6fa; color: #1a237e; }
.ai-tree-item.active { background: #1a237e; color: #fff; }
.intro-title { font-size: 20px; font-weight: bold; color: #1a237e; margin-bottom: 16px; }
.intro-content { line-height: 1.8; font-size: 15px; color: #333; margin-bottom: 24px; }
.intro-subtitle { font-size: 18px; font-weight: bold; color: #1a237e; margin: 30px 0 12px; }
.intro-list { line-height: 1.8; font-size: 15px; color: #333; padding-left: 20px; margin-bottom: 24px; }
.resource-area { }
.resource-title { font-size: 18px; font-weight: bold; margin-bottom: 15px; }
.resource-iframe { width: 100%; height: 650px; border: none; }
.build-tip { width: 100%; height: 650px; display: flex; align-items: center; justify-content: center; font-size: 20px; color: #999; }
.vr-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }
.vr-card { background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,.08); cursor: pointer; transition: .2s; text-align: center; }
.vr-card:hover { transform: translateY(-4px); box-shadow: 0 4px 16px rgba(0,0,0,.12); }
.vr-icon { font-size: 36px; margin-bottom: 8px; }
.vr-label { font-size: 14px; color: #333; }
</style>
