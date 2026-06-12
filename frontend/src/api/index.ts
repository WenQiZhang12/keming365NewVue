import axios from 'axios'
import type {
  Classify, Curriculum, Experiment, NewsItem,
  PaginatedResponse, LoginResponse, UserInfo
} from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// 请求拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
    const msg = error.response?.data?.message || error.response?.data?.detail || '请求失败'
    return Promise.reject(new Error(msg))
  }
)

// ====== 首页 ======
export async function getClassifies(): Promise<Classify[]> {
  const { data } = await api.get<Classify[] | PaginatedResponse<Classify>>('/home/classify/')
  return Array.isArray(data) ? data : data.results
}

export async function getClassifyExperiments(
  classifyId: number | string, pageSize = 5
): Promise<PaginatedResponse<Experiment>> {
  const { data } = await api.get('/courses/experiments/', {
    params: { classifyId, page_size: pageSize }
  })
  return data
}

// ====== 课程 ======
export async function getCurricula(params: {
  page?: number; page_size?: number;
  classifyId?: string | number; search?: string
}): Promise<PaginatedResponse<Curriculum>> {
  const { data } = await api.get('/courses/', { params })
  return data
}

export async function getCurriculumDetail(id: string | number): Promise<Curriculum> {
  const { data } = await api.get(`/courses/${id}/`)
  return data
}

export async function getExperiments(params: {
  page?: number; page_size?: number;
  curriculumId?: string | number; classifyId?: string | number;
  search?: string; type?: string
}): Promise<PaginatedResponse<Experiment>> {
  const { data } = await api.get('/courses/experiments/', { params })
  return data
}

export async function getCurriculumClassifies(): Promise<Classify[]> {
  const { data } = await api.get<Classify[] | PaginatedResponse<Classify>>('/courses/classifies/')
  return Array.isArray(data) ? data : data.results
}

// ====== 新闻 ======
export async function getNews(params: {
  page?: number; page_size?: number;
  search?: string; ordering?: string
}): Promise<PaginatedResponse<NewsItem>> {
  const { data } = await api.get('/news/', { params })
  return data
}

export async function getNewsDetail(id: string | number): Promise<NewsItem> {
  const { data } = await api.get(`/news/${id}/`)
  return data
}

// ====== 认证 ======
export async function login(username: string, password: string): Promise<LoginResponse> {
  const { data } = await api.post('/accounts/auth/login/', { username, password })
  return data
}

export async function register(params: {
  username: string; name: string; password: string; telephone?: string
}): Promise<void> {
  await api.post('/accounts/auth/register/', params)
}

export async function getProfile(): Promise<UserInfo> {
  const { data } = await api.get('/accounts/auth/profile/')
  return data
}

export async function logout(): Promise<void> {
  try { await api.post('/accounts/auth/logout/') } catch { /* ignore */ }
}

export default api
