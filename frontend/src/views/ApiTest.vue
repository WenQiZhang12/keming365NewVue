<template>
  <div class="api-test-page">
    <div class="container">
      <div class="page-header">
        <h1>🔧 API 测试工具</h1>
        <p>开发调试用，生产环境请勿部署</p>
      </div>

      <div class="api-form">
        <div class="form-group">
          <label>API 地址：</label>
          <input v-model="apiUrl" class="url-input" placeholder="/api/v1/..." />
        </div>
        <div class="form-group">
          <label>请求方法：</label>
          <select v-model="method" class="method-select">
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
        </div>
        <div class="form-group">
          <label>请求参数 (JSON)：</label>
          <textarea v-model="params" class="params-area" rows="6" placeholder='{"key": "value"}'></textarea>
        </div>
        <button class="send-btn" @click="sendRequest" :disabled="sending">
          {{ sending ? '⏳ 请求中...' : '🚀 发送请求' }}
        </button>
      </div>

      <div class="result-box">
        <h3>📤 响应结果</h3>
        <div v-if="response" class="result-content">
          <div class="result-header">
            <span>状态：<b :class="response.ok ? 'ok' : 'fail'">{{ response.status }} {{ response.statusText }}</b></span>
            <span>耗时：<b>{{ response.time }}ms</b></span>
          </div>
          <pre>{{ response.data }}</pre>
        </div>
        <div v-else class="no-response">点击"发送请求"开始测试</div>
      </div>

      <div class="history-box">
        <h3>🕐 测试历史</h3>
        <div v-if="history.length === 0" class="no-history">暂无历史</div>
        <div v-else>
          <div v-for="(h, i) in history" :key="i" class="history-item" @click="reuseHistory(h)">
            <span class="method" :class="`m-${h.method.toLowerCase()}`">{{ h.method }}</span>
            <span class="url">{{ h.url }}</span>
            <span class="time">{{ h.time }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'
import { toast } from '@/utils'

const apiUrl = ref('/')
const method = ref('GET')
const params = ref('{}')
const sending = ref(false)
const response = ref<any>(null)
const history = ref<any[]>([])

const sendRequest = async () => {
  if (!apiUrl.value) { toast('请输入API地址', 'error'); return }

  sending.value = true
  const startTime = Date.now()
  try {
    let body: any = undefined
    if (method.value !== 'GET' && params.value.trim()) {
      try { body = JSON.parse(params.value) } catch { toast('参数JSON格式错误', 'error'); sending.value = false; return }
    }

    const res: any = await api.request({
      url: apiUrl.value,
      method: method.value,
      data: body
    })

    const time = Date.now() - startTime
    response.value = { status: 200, statusText: 'OK', data: JSON.stringify(res, null, 2), time, ok: true }
    saveHistory()
  } catch (e: any) {
    const time = Date.now() - startTime
    response.value = { status: e.response?.status || 500, statusText: e.response?.statusText || 'Error', data: JSON.stringify(e.response?.data || { message: e.message }, null, 2), time, ok: false }
  } finally {
    sending.value = false
  }
}

const saveHistory = () => {
  const item = { url: apiUrl.value, method: method.value, time: new Date().toLocaleTimeString() }
  history.value.unshift(item)
  if (history.value.length > 20) history.value = history.value.slice(0, 20)
  try { localStorage.setItem('api_test_history', JSON.stringify(history.value)) } catch { /* ignore */ }
}

const reuseHistory = (h: any) => {
  apiUrl.value = h.url
  method.value = h.method
}

onMounted(() => {
  try {
    const saved = localStorage.getItem('api_test_history')
    if (saved) history.value = JSON.parse(saved)
  } catch { /* ignore */ }
})
</script>

<style lang="scss" scoped>
.api-test-page { background: #f5f6fa; min-height: 60vh; }
.container { max-width: 1000px; margin: 0 auto; padding: 20px; }
.page-header { text-align: center; padding: 20px;
  h1 { font-size: 24px; color: #1a237e; margin-bottom: 6px; }
  p { font-size: 13px; color: #e53935; }
}

.api-form { background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,.06); margin-bottom: 16px;
  .form-group { margin-bottom: 16px;
    label { display: block; font-size: 13px; color: #666; margin-bottom: 6px; }
    .url-input, .method-select, .params-area { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; outline: none; font-family: 'Courier New', monospace;
      &:focus { border-color: #1a237e; }
    }
    .params-area { resize: vertical; }
  }
  .send-btn { padding: 12px 32px; background: #1a237e; color: #fff; border: none; border-radius: 8px; font-size: 15px; cursor: pointer;
    &:hover { background: #283593; }
    &:disabled { opacity: 0.6; cursor: not-allowed; }
  }
}

.result-box { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.06); margin-bottom: 16px;
  h3 { font-size: 16px; color: #1a237e; margin-bottom: 12px; }
  .result-content { .result-header { display: flex; gap: 16px; padding-bottom: 8px; border-bottom: 1px solid #eef0f4; margin-bottom: 8px; font-size: 13px;
    .ok { color: #2e7d32; } .fail { color: #c62828; }
  }
    pre { background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 6px; overflow: auto; max-height: 400px; font-size: 12px; line-height: 1.5; }
  }
  .no-response { text-align: center; padding: 40px; color: #999; }
}

.history-box { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.06);
  h3 { font-size: 16px; color: #1a237e; margin-bottom: 12px; }
  .no-history { text-align: center; padding: 20px; color: #999; }
  .history-item { display: flex; gap: 12px; padding: 8px 12px; border-bottom: 1px solid #eef0f4; cursor: pointer; font-size: 13px; transition: .2s;
    &:hover { background: #fafbff; }
    .method { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; color: #fff;
      &.m-get { background: #67c23a; }
      &.m-post { background: #e6a23c; }
      &.m-put { background: #409eff; }
      &.m-delete { background: #f56c6c; }
    }
    .url { flex: 1; color: #555; font-family: monospace; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .time { color: #999; font-size: 12px; }
  }
}
</style>
</content>
</invoke>