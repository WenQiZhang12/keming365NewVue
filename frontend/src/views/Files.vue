<template>
  <div class="files-page">
    <div class="container">
      <div class="breadcrumb">
        <router-link to="/">首页</router-link> &gt; 文件管理
      </div>
      <div class="page-header">
        <h1>📁 文件管理</h1>
        <p>上传和管理图片、视频、PDF、PPT等文件</p>
      </div>

      <!-- 上传区域 -->
      <div class="upload-area" :class="{ dragover: dragover }"
           @click="fileInput?.click()"
           @dragover.prevent="dragover = true"
           @dragleave="dragover = false"
           @drop.prevent="onDrop">
        <div class="icon">📤</div>
        <p>点击或拖拽文件到此处上传</p>
        <p class="hint">支持图片、视频、PDF、PPT，单个文件最大200MB</p>
        <input ref="fileInput" type="file" style="display:none" @change="onFileSelect" />
        <div class="progress-bar" :style="{ display: uploading ? 'block' : 'none' }">
          <div class="fill" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <!-- 类型切换 -->
      <div class="type-tabs">
        <span v-for="t in types" :key="t.key" class="type-tab" :class="{ active: currentType === t.key }" @click="currentType = t.key">
          {{ t.label }}
        </span>
      </div>

      <!-- 文件列表 -->
      <div v-if="filteredFiles.length === 0" class="empty-list">暂无文件，请上传</div>
      <div v-else class="file-grid">
        <div v-for="(f, i) in filteredFiles" :key="i" class="file-card" @click="previewFile(f)">
          <div class="preview">
            <img v-if="f.type === 'image' && f.url" :src="f.url" alt="" @error="($event.target as HTMLImageElement).style.display='none'">
            <span v-else>{{ iconFor(f.type) }}</span>
          </div>
          <div class="info">
            <div class="name">{{ f.name }}</div>
            <div class="meta">{{ f.size || '' }}</div>
          </div>
          <span class="badge">{{ badgeFor(f.type) }}</span>
        </div>
      </div>

      <!-- 预览弹窗 -->
      <div v-if="previewing" class="preview-overlay" @click.self="previewing = null">
        <div class="preview-box">
          <span class="close" @click="previewing = null">✕</span>
          <div v-if="previewing.type === 'image'">
            <img :src="previewing.url" :alt="previewing.name">
          </div>
          <div v-else-if="previewing.type === 'video'">
            <video :src="previewing.url" controls></video>
          </div>
          <div v-else class="other-preview">
            <div class="icon">📄</div>
            <p>{{ previewing.name }}</p>
            <p class="hint">{{ previewing.size }}</p>
            <a :href="previewing.url" target="_blank" class="download-btn">下载查看</a>
          </div>
          <div class="p-info">
            <h3>{{ previewing.name }}</h3>
            <p>{{ previewing.size }} | {{ previewing.time ? previewing.time.slice(0, 10) : '' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/api'
import { toast } from '@/utils'

interface UploadedFile { url: string; name: string; size: string; type: string; ext: string; time: string }

const fileInput = ref<HTMLInputElement | null>(null)
const allFiles = ref<UploadedFile[]>([])
const currentType = ref('all')
const dragover = ref(false)
const uploading = ref(false)
const progress = ref(0)
const previewing = ref<UploadedFile | null>(null)

const types = [
  { key: 'all', label: '📋 全部' },
  { key: 'image', label: '🖼️ 图片' },
  { key: 'video', label: '🎬 视频' },
  { key: 'pdf', label: '📄 PDF' },
  { key: 'ppt', label: '📊 PPT' }
]

const filteredFiles = computed(() =>
  currentType.value === 'all' ? allFiles.value : allFiles.value.filter(f => f.type === currentType.value)
)

const iconFor = (type: string) => {
  if (type === 'image') return '🖼️'
  if (type === 'video') return '🎬'
  if (type === 'pdf') return '📄'
  if (type === 'ppt') return '📊'
  return '📄'
}
const badgeFor = (type: string) => {
  if (type === 'image') return '图片'
  if (type === 'video') return '视频'
  if (type === 'pdf') return 'PDF'
  if (type === 'ppt') return 'PPT'
  return '文件'
}

const onDrop = (e: DragEvent) => {
  dragover.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) uploadFile(files[0])
}

const onFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    uploadFile(input.files[0])
    input.value = ''
  }
}

const requireLogin = () => {
  if (localStorage.getItem('token')) return true
  if (confirm('您尚未登录，是否前往登录？')) {
    location.href = '/login'
  }
  return false
}

const uploadFile = async (file: File) => {
  if (!requireLogin()) return

  const ext = (file.name.split('.').pop() || '').toLowerCase()
  const typeMap: Record<string, string> = {
    jpg: 'image', jpeg: 'image', png: 'image', gif: 'image', webp: 'image', bmp: 'image',
    mp4: 'video', avi: 'video', mov: 'video', wmv: 'video', flv: 'video', mkv: 'video', webm: 'video',
    pdf: 'pdf', pptx: 'ppt', ppt: 'ppt'
  }
  const fileType = typeMap[ext] || 'other'

  uploading.value = true
  progress.value = 0

  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('type', fileType)

    const result: any = await new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhr.open('POST', '/api/v1/files/upload/', true)
      const token = localStorage.getItem('token')
      if (token) xhr.setRequestHeader('Authorization', 'Bearer ' + token)
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) progress.value = (e.loaded / e.total) * 90
      }
      xhr.onload = () => {
        progress.value = 100
        if (xhr.status >= 200 && xhr.status < 300) {
          try { resolve(JSON.parse(xhr.responseText)) } catch { reject(new Error('解析响应失败')) }
        } else {
          try { const d = JSON.parse(xhr.responseText); reject(new Error(d.message || '上传失败')) } catch { reject(new Error('上传失败')) }
        }
      }
      xhr.onerror = () => reject(new Error('网络错误'))
      xhr.send(formData)
    })

    setTimeout(() => { uploading.value = false; progress.value = 0 }, 1000)

    if (result.code === 0 || result.url) {
      toast('上传成功：' + file.name, 'success')
      allFiles.value.push({
        url: result.data?.url || result.url,
        name: result.data?.fileName || file.name,
        size: result.data?.fileSize || '',
        type: result.data?.fileType || fileType,
        ext: result.data?.extension || '.' + ext,
        time: new Date().toISOString()
      })
      saveFiles()
    } else {
      throw new Error(result.message || '上传失败')
    }
  } catch (e: any) {
    uploading.value = false
    toast('上传失败：' + e.message, 'error')
  }
}

const previewFile = (f: UploadedFile) => {
  previewing.value = f
}

const saveFiles = () => {
  try { localStorage.setItem('uploaded_files', JSON.stringify(allFiles.value)) } catch { /* ignore */ }
}

onMounted(() => {
  try {
    const saved = localStorage.getItem('uploaded_files')
    if (saved) allFiles.value = JSON.parse(saved)
  } catch { /* ignore */ }
})
</script>

<style lang="scss" scoped>
.files-page { background: #f5f6fa; min-height: 60vh; }
.container { max-width: 1000px; margin: 0 auto; padding: 20px; }
.breadcrumb { font-size: 13px; color: #999; margin-bottom: 16px; a { color: #1a237e; } }
.page-header { text-align: center; padding: 30px 20px 20px;
  h1 { font-size: 26px; color: #1a237e; margin-bottom: 8px; }
  p { font-size: 14px; color: #999; }
}

.upload-area {
  border: 2px dashed #c5cae9; border-radius: 16px; padding: 40px; text-align: center;
  margin-bottom: 24px; background: #fff; cursor: pointer; transition: .2s;
  &:hover { border-color: #1a237e; background: #fafbff; }
  &.dragover { border-color: #1a237e; background: #e8eaf6; }
  .icon { font-size: 48px; margin-bottom: 12px; }
  p { font-size: 14px; color: #666; margin-bottom: 4px; }
  .hint { font-size: 12px; color: #bbb; }
}
.progress-bar { height: 6px; background: #e0e0e0; border-radius: 3px; overflow: hidden; margin-top: 12px;
  .fill { height: 100%; background: #1a237e; border-radius: 3px; transition: width .3s; }
}

.type-tabs { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap;
  .type-tab { padding: 8px 20px; border-radius: 20px; font-size: 13px; cursor: pointer; border: 1px solid #e8e8e8; background: #fff; transition: .2s; color: #555;
    &:hover { border-color: #1a237e; color: #1a237e; }
    &.active { background: #1a237e; color: #fff; border-color: #1a237e; }
  }
}

.empty-list { text-align: center; padding: 60px; color: #999; }

.file-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px;
  .file-card { background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.06); transition: .2s; cursor: pointer; position: relative;
    &:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.1); }
    .preview { height: 140px; background: #f5f5f5; display: flex; align-items: center; justify-content: center; font-size: 36px; overflow: hidden;
      img { width: 100%; height: 100%; object-fit: cover; }
    }
    .info { padding: 12px; .name { font-size: 13px; font-weight: 600; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; } .meta { font-size: 11px; color: #999; } }
    .badge { position: absolute; top: 8px; right: 8px; padding: 2px 8px; border-radius: 8px; font-size: 10px; background: rgba(26,35,126,.8); color: #fff; }
  }
}

.preview-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.7); z-index: 999; display: flex; align-items: center; justify-content: center; padding: 20px;
  .preview-box { background: #fff; border-radius: 12px; max-width: 90vw; max-height: 90vh; overflow: auto; position: relative;
    .close { position: absolute; right: 12px; top: 12px; width: 32px; height: 32px; border-radius: 50%; background: rgba(0,0,0,.1); display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 18px; z-index: 10;
      &:hover { background: rgba(0,0,0,.2); }
    }
    img, video { max-width: 100%; max-height: 80vh; display: block; }
    .other-preview { padding: 40px; text-align: center; min-width: 300px; .icon { font-size: 48px; margin-bottom: 12px; } .hint { font-size: 13px; color: #999; margin-top: 8px; } .download-btn { display: inline-block; margin-top: 16px; padding: 10px 24px; background: #1a237e; color: #fff; border-radius: 8px; text-decoration: none; } }
    .p-info { padding: 16px; h3 { margin-bottom: 4px; } p { font-size: 13px; color: #999; } }
  }
}

@media(max-width: 768px) { .file-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); } }
</style>