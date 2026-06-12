<template>
  <div class="video-page">
    <div class="main-content">
      <!-- 国家选择区域 -->
      <div class="country-section">
        <div class="country-inner">
          <div class="country-container">
            <button class="country-nav-btn" @click="scrollCountries(-1)">&#8249;</button>
            <div class="country-scroll" ref="countryScrollRef">
              <div class="country-grid">
                <div
                  v-for="c in countries" :key="c.code"
                  class="country-item" :class="{ active: currentCountry === c.code }"
                  @click="selectCountry(c.code)"
                >
                  <div class="country-flag"><img :src="c.flag" :alt="c.name" /></div>
                  <div class="country-name">{{ c.name }}</div>
                </div>
              </div>
            </div>
            <button class="country-nav-btn" @click="scrollCountries(1)">&#8250;</button>
          </div>
        </div>
      </div>

      <!-- 课程菜单区域 -->
      <div class="course-menu-section">
        <div class="course-menu-inner">
          <div class="course-menu">
            <div
              v-for="cat in currentCategories" :key="cat"
              class="course-menu-item" :class="{ active: currentCourse === cat }"
              @click="selectCourse(cat)"
            >{{ cat }}</div>
          </div>
        </div>
      </div>

      <!-- 课程展示区域 -->
      <div class="course-section">
        <div class="section-title">{{ currentCourse || '请选择课程分类' }}</div>
        <div class="course-grid">
          <template v-if="pageCourses.length">
            <div v-for="(c, i) in pageCourses" :key="i" class="course-item" @click="openCourse(c.url)">
              <div class="course-image"><img :src="c.cover" :alt="c.title" /></div>
              <div class="course-name">{{ c.title }}</div>
            </div>
          </template>
          <div v-else class="empty-tip">{{ currentCourse ? '暂无课程内容' : '请选择课程分类' }}</div>
        </div>
        <div class="pagination" v-if="totalPages > 1">
          <button :disabled="currentPage <= 1" @click="goPage(currentPage - 1)">&#8249;</button>
          <button :disabled="currentPage <= 1" @click="goPage(currentPage - 1)">上一页</button>
          <button
            v-for="p in totalPages" :key="p"
            :class="{ active: p === currentPage }"
            @click="goPage(p)"
          >{{ p }}</button>
          <button :disabled="currentPage >= totalPages" @click="goPage(currentPage + 1)">下一页</button>
          <button :disabled="currentPage >= totalPages" @click="goPage(totalPages)">&#8250;</button>
          <span>10条/页</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { countries, courseCategories, getCourses } from '@/data/videoCourses'
import type { VideoCourse } from '@/data/videoCourses'

const countryScrollRef = ref<HTMLElement | null>(null)
const currentCountry = ref('vietnam')
const currentCourse = ref('')
const currentPage = ref(1)
const PAGE_SIZE = 10

const currentCategories = computed(() => courseCategories[currentCountry.value] || [])

const allCourses = computed<VideoCourse[]>(() => {
  if (!currentCourse.value) return []
  return getCourses(currentCourse.value)
})

const totalPages = computed(() => Math.ceil(allCourses.value.length / PAGE_SIZE) || 1)

const pageCourses = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return allCourses.value.slice(start, start + PAGE_SIZE)
})

const selectCountry = (code: string) => {
  currentCountry.value = code
  currentCourse.value = ''
  currentPage.value = 1
}

const selectCourse = (name: string) => {
  currentCourse.value = name
  currentPage.value = 1
}

const goPage = (page: number) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
}

const openCourse = (url: string) => {
  if (url && url !== '#') window.open(url, '_blank')
}

const scrollCountries = (direction: number) => {
  countryScrollRef.value?.scrollBy({ left: direction * 176, behavior: 'smooth' })
}
</script>

<style lang="scss" scoped>
.video-page { background: #f5f6fa; }
.main-content { width: 1200px; margin: 20px auto; }

.country-section {
  background: white; padding: 15px; border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 24px;
  position: relative; overflow: hidden;
  &::before {
    content: "国家"; position: absolute; left: 0; top: 0;
    width: 40px; height: 100%; background: #e6f3ff; z-index: 1;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; color: #1a237e; font-weight: 600;
  }
}
.country-inner { position: relative; z-index: 10; margin-left: 50px; }
.country-container { display: flex; align-items: center; width: 100%; }
.country-nav-btn {
  background: none; border: none; cursor: pointer;
  padding: 0 8px; color: #666; font-size: 20px;
  &:hover { color: #1a237e; }
}
.country-scroll { flex: 1; overflow: hidden; scroll-behavior: smooth; margin: 0 10px; }
.country-grid { display: flex; width: max-content; gap: 16px; padding: 8px 0; }
.country-item {
  flex: 0 0 160px; text-align: center; cursor: pointer;
  transition: 0.3s; padding: 10px; border-radius: 8px; border: 2px solid transparent;
  &:hover { transform: translateY(-2px); background: #f7fbff; }
  &.active { background: #e6f3ff; border-color: #1a237e; }
}
.country-flag {
  width: 90px; height: 50px; margin: 0 auto 8px;
  border-radius: 6px; overflow: hidden; border: 1px solid #eee;
  img { width: 100%; height: 100%; object-fit: cover; }
}
.country-name { font-size: 14px; color: #333; font-weight: 500; }

.course-menu-section {
  background: white; padding: 20px; border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 24px;
  position: relative; overflow: hidden;
  &::before {
    content: "课程"; position: absolute; left: 0; top: 0;
    width: 40px; height: 100%; background: #fff3e0; z-index: 1;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; color: #1a237e; font-weight: 600;
  }
}
.course-menu-inner { position: relative; z-index: 10; margin-left: 50px; }
.course-menu { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.course-menu-item {
  font-size: 15px; color: #333; padding: 8px 20px; border-radius: 20px;
  cursor: pointer; transition: 0.3s; white-space: nowrap; background: #f5f6fa;
  &:hover { background: #e8eaf6; color: #1a237e; }
  &.active { background: #1a237e; color: #fff; }
}

.course-section {
  background: white; padding: 24px; border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.section-title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 20px; }
.course-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-top: 20px; }
.course-item {
  text-align: center; cursor: pointer; transition: 0.3s;
  &:hover { transform: translateY(-4px); }
}
.course-image {
  width: 100%; height: 120px; background: #f5f6fa; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden; margin-bottom: 10px;
  img { width: 100%; height: 100%; object-fit: cover; }
}
.course-name {
  font-size: 13px; color: #666; line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
}
.empty-tip {
  font-size: 16px; color: #999; padding: 60px 0;
  text-align: center; width: 100%; grid-column: 1/-1;
}

.pagination {
  display: flex; justify-content: center; align-items: center;
  margin: 30px 0; gap: 8px;
  button {
    background: #f5f6fa; border: 1px solid #ddd; padding: 6px 12px;
    border-radius: 4px; cursor: pointer; font-size: 14px; color: #666;
    &:hover:not(:disabled) { background: #e8eaf6; color: #1a237e; }
    &.active { background: #1a237e; color: #fff; border-color: #1a237e; }
    &:disabled { opacity: 0.5; cursor: not-allowed; }
  }
  span { font-size: 13px; color: #999; margin-left: 8px; }
}

@media(max-width:1200px) {
  .main-content { width: 95%; }
  .course-grid { grid-template-columns: repeat(3, 1fr); }
}
@media(max-width:768px) {
  .course-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
