# Vue SPA迁移方案

## 一、项目概述

当前项目采用**传统多页网站架构**，每个导航按钮对应独立的HTML文件。为提升用户体验、便于维护和后续功能扩展，计划迁移至**Vue 3 + TypeScript + Vue Router**单页应用架构。

### 当前架构问题

| 问题 | 影响 |
|------|------|
| 页面切换需重新加载 | 用户体验差，加载慢 |
| 代码重复率高 | 维护成本高 |
| 无组件化复用 | 开发效率低 |
| 无状态管理 | 数据共享困难 |

---

## 二、迁移目标

1. ✅ 渐进式迁移，不影响现有业务
2. ✅ 保持原有功能和界面风格
3. ✅ 提升页面切换流畅度
4. ✅ 降低代码重复率
5. ✅ 便于后续HTTPS改造

---

## 三、技术栈选择

| 分类 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 框架 | Vue | 3.x | 渐进式JavaScript框架 |
| 路由 | Vue Router | 4.x | Vue官方路由管理器 |
| 状态管理 | Pinia | 2.x | Vue官方状态管理库 |
| 构建工具 | Vite | 6.x | 新一代前端构建工具 |
| 语言 | TypeScript | 5.x | 类型安全的JavaScript |
| HTTP客户端 | Axios | 1.x | Promise-based HTTP客户端 |
| 样式 | SCSS | - | CSS预处理器 |

---

## 四、项目结构

```
frontend/                              # 前端Vue项目目录
├── src/
│   ├── components/                    # 公共组件
│   │   ├── Header.vue               # 导航栏
│   │   ├── Footer.vue               # 页脚
│   │   ├── Toast.vue                # 提示组件
│   │   ├── Loading.vue              # 加载组件
│   │   └── Card.vue                 # 卡片组件
│   ├── views/                        # 页面视图
│   │   ├── Home.vue                 # 首页
│   │   ├── Courses.vue              # 全部课程
│   │   ├── News.vue                 # 新闻资讯
│   │   ├── Platform.vue             # 平台简介
│   │   ├── Video.vue                # 职教出海
│   │   ├── About.vue                # 关于我们
│   │   ├── Profile.vue              # 个人中心
│   │   ├── Experiment.vue           # 实验页面
│   │   ├── CourseDetail.vue         # 课程详情
│   │   ├── Login.vue                # 登录页
│   │   └── Register.vue             # 注册页
│   ├── router/                      # 路由配置
│   │   └── index.ts
│   ├── stores/                      # 状态管理
│   │   └── user.ts
│   ├── api/                         # API接口封装
│   │   └── index.ts
│   ├── utils/                       # 工具函数
│   │   └── index.ts
│   ├── types/                       # TypeScript类型定义
│   │   └── index.ts
│   ├── App.vue                      # 根组件
│   └── main.ts                      # 入口文件
├── public/                           # 静态资源
├── index.html
├── vite.config.ts                   # Vite配置
├── tsconfig.json                    # TypeScript配置
└── package.json
```

---

## 五、路由配置

### 路由表设计

| 路径 | 名称 | 组件 | 说明 |
|------|------|------|------|
| `/` | Home | Home.vue | 首页 |
| `/courses` | Courses | Courses.vue | 全部课程 |
| `/news` | News | News.vue | 新闻资讯 |
| `/platform` | Platform | Platform.vue | 平台简介 |
| `/video` | Video | Video.vue | 职教出海 |
| `/about` | About | About.vue | 关于我们 |
| `/profile` | Profile | Profile.vue | 个人中心 |
| `/experiment/:id` | Experiment | Experiment.vue | 实验页面 |
| `/course/:id` | CourseDetail | CourseDetail.vue | 课程详情 |
| `/login` | Login | Login.vue | 登录 |
| `/register` | Register | Register.vue | 注册 |

### 路由配置代码

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/courses', name: 'Courses', component: () => import('../views/Courses.vue') },
  { path: '/news', name: 'News', component: () => import('../views/News.vue') },
  { path: '/platform', name: 'Platform', component: () => import('../views/Platform.vue') },
  { path: '/video', name: 'Video', component: () => import('../views/Video.vue') },
  { path: '/about', name: 'About', component: () => import('../views/About.vue') },
  { path: '/profile', name: 'Profile', component: () => import('../views/Profile.vue') },
  { path: '/experiment/:id', name: 'Experiment', component: () => import('../views/Experiment.vue') },
  { path: '/course/:id', name: 'CourseDetail', component: () => import('../views/CourseDetail.vue') },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  }
})

export default router
```

---

## 六、渐进式迁移计划

### Phase 1: 框架搭建（1-2天）

**目标**：搭建Vue项目基础框架

| 任务 | 描述 |
|------|------|
| 初始化项目 | 使用Vite创建Vue + TypeScript项目 |
| 安装依赖 | Vue Router、Pinia、Axios、Sass |
| 配置路由 | 创建路由配置文件 |
| 创建公共组件 | Header、Footer、Toast、Loading |

**执行命令**：
```bash
# 初始化Vue项目
npm create vite@6.5.0 frontend -- --template vue-ts

# 进入项目目录
cd frontend

# 安装依赖
npm install
npm install vue-router@4 axios pinia
npm install -D sass
```

### Phase 2: 核心页面迁移（3-5天）

**目标**：迁移首页和课程页面

| 任务 | 描述 |
|------|------|
| 首页迁移 | 将index.html内容迁移至Home.vue |
| 课程列表迁移 | 将courses.html内容迁移至Courses.vue |
| 新闻页面迁移 | 将news.html内容迁移至News.vue |
| API集成 | 封装API接口，替换原有的fetch调用 |

### Phase 3: 详情页迁移（5-7天）

**目标**：迁移详情页和实验页面

| 任务 | 描述 |
|------|------|
| 课程详情迁移 | 创建CourseDetail.vue |
| 实验页面迁移 | 将experiment.html内容迁移至Experiment.vue |
| 职教出海迁移 | 将video.html内容迁移至Video.vue |

### Phase 4: 用户中心迁移（3-4天）

**目标**：迁移用户认证和个人中心

| 任务 | 描述 |
|------|------|
| 登录页面迁移 | 创建Login.vue |
| 注册页面迁移 | 创建Register.vue |
| 个人中心迁移 | 将profile.html内容迁移至Profile.vue |
| 状态管理 | 配置Pinia管理用户状态 |

### Phase 5: 测试优化（3-5天）

**目标**：功能测试和性能优化

| 任务 | 描述 |
|------|------|
| 功能测试 | 验证所有页面功能正常 |
| 样式统一 | 使用SCSS变量统一管理样式 |
| 性能优化 | 代码分割、懒加载、缓存优化 |
| 清理遗留 | 删除旧的HTML文件 |

---

## 七、核心代码示例

### 7.1 API封装

```typescript
// src/api/index.ts
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 首页分类
export const getClassifies = () => api.get('/home/classify/')

// 课程列表
export const getCourses = (params?: Record<string, any>) => 
  api.get('/courses/', { params })

// 新闻列表
export const getNews = (params?: Record<string, any>) => 
  api.get('/news/', { params })

// 用户登录
export const login = (data: { username: string; password: string }) => 
  api.post('/accounts/auth/login/', data)

// 用户注册
export const register = (data: { username: string; password: string; email?: string }) => 
  api.post('/accounts/auth/register/', data)

// 获取用户信息
export const getProfile = () => api.get('/accounts/auth/profile/')

// 更新用户信息
export const updateProfile = (data: Record<string, any>) => 
  api.put('/accounts/auth/profile/', data)

export default api
```

### 7.2 用户状态管理

```typescript
// src/stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, getProfile, register as apiRegister } from '../api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const user = ref<Record<string, any> | null>(null)
  const isLoggedIn = computed(() => !!token.value && !!user.value)

  const login = async (username: string, password: string) => {
    const response = await apiLogin({ username, password })
    token.value = response.data.access
    localStorage.setItem('access_token', token.value)
    await fetchUser()
  }

  const register = async (username: string, password: string, email?: string) => {
    await apiRegister({ username, password, email })
  }

  const fetchUser = async () => {
    try {
      const response = await getProfile()
      user.value = response.data
    } catch {
      logout()
    }
  }

  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('access_token')
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    register,
    fetchUser,
    logout
  }
})
```

### 7.3 公共Header组件

```vue
<!-- src/components/Header.vue -->
<template>
  <header class="header">
    <div class="logo" @click="$router.push('/')">
      📘科明365VR教学云平台
    </div>
    <nav class="nav">
      <button
        v-for="item in navItems"
        :key="item.path"
        :class="{ active: $route.path === item.path }"
        @click="$router.push(item.path)"
      >
        {{ item.name }}
      </button>
    </nav>
    <div class="user">
      <template v-if="userStore.isLoggedIn">
        <div class="avatar" @click="toggleDropdown">
          {{ userStore.user?.name?.charAt(0) || 'U' }}
        </div>
        <div class="dropdown-menu" :class="{ show: showDropdown }">
          <button @click="$router.push('/profile'); showDropdown = false">个人中心</button>
          <button @click="handleLogout">退出登录</button>
        </div>
      </template>
      <template v-else>
        <button class="btn btn-login" @click="$router.push('/login')">登录</button>
        <button class="btn btn-reg" @click="$router.push('/register')">注册</button>
      </template>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const showDropdown = ref(false)

const navItems = [
  { path: '/', name: '首页' },
  { path: '/courses', name: '全部课程' },
  { path: '/news', name: '新闻资讯' },
  { path: '/platform', name: '平台简介' },
  { path: '/video', name: '职教出海' },
  { path: '/about', name: '关于我们' },
]

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const handleLogout = () => {
  userStore.logout()
  showDropdown.value = false
  window.location.href = '/'
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.user')) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  if (userStore.token) {
    userStore.fetchUser()
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style lang="scss" scoped>
.header {
  background: linear-gradient(135deg, #1a237e, #283593);
  color: #fff;
  padding: 0 40px;
  height: 64px;
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.logo {
  font-size: 20px;
  font-weight: 700;
  cursor: pointer;
  margin-right: 40px;
}

.nav {
  display: flex;
  gap: 24px;
}

.nav button {
  background: none;
  border: none;
  color: #fff;
  font-size: 14px;
  padding: 6px 0;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;

  &:hover, &.active {
    border-bottom-color: #64b5f6;
    color: #64b5f6;
  }
}

.user {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
}

.btn {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-login {
  background: #64b5f6;
  color: #fff;

  &:hover {
    background: #42a5f5;
  }
}

.btn-reg {
  background: transparent;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.6);

  &:hover {
    border-color: #fff;
  }
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #64b5f6;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #42a5f5;
    transform: scale(1.05);
  }
}

.dropdown-menu {
  position: absolute;
  top: 48px;
  right: 0;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 120px;
  padding: 8px 0;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-6px);
  transition: all 0.2s;
  z-index: 200;

  &.show {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
  }

  button {
    display: block;
    width: 100%;
    padding: 10px 16px;
    background: none;
    border: none;
    text-align: left;
    font-size: 13px;
    color: #333;
    cursor: pointer;
    transition: all 0.15s;

    &:hover {
      background: #f5f6fa;
      color: #1a237e;
    }
  }
}
</style>
```

---

## 八、后端配置调整

### 8.1 Django配置修改

```python
# settings.py

# 添加前端静态文件目录
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend', 'dist'),
]

# 配置CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8000",
    "https://your-domain.com",
]

# 配置CSRF（如果需要）
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://your-domain.com",
]
```

### 8.2 URL配置修改

```python
# urls.py
from django.urls import path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    # API路由
    path('api/', include('api.urls')),
    
    # SPA入口（必须放在最后）
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
```

---

## 九、开发与部署

### 9.1 开发环境

```bash
# 启动Vue开发服务器
cd frontend
npm run dev

# 启动Django后端
cd ..
python manage.py runserver 0.0.0.0:8000
```

### 9.2 生产构建

```bash
# 构建Vue项目
cd frontend
npm run build

# 收集静态文件（Django）
cd ..
python manage.py collectstatic --noinput
```

### 9.3 Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    # SSL证书配置
    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    
    # 静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 十、迁移注意事项

### 10.1 样式迁移
- 将现有CSS复制到Vue组件的`<style>`中
- 使用SCSS变量统一管理颜色、字体等
- 删除重复的样式代码

### 10.2 事件绑定转换
| 旧方式 | 新方式 |
|--------|--------|
| `onclick="func()"` | `@click="func"` |
| `onload="func()"` | `onMounted(() => func())` |
| `onchange="func()"` | `@change="func"` |

### 10.3 DOM操作转换
- 使用Vue的响应式数据替代`document.getElementById`
- 使用`v-if`/`v-show`替代`style.display`
- 使用`v-for`替代手动循环创建DOM

### 10.4 SEO优化
- 使用`vue-meta`或`vite-plugin-vue-meta`管理页面meta信息
- 考虑使用Prerender或SSR提升搜索引擎收录

---

## 十一、风险评估

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| API兼容性 | 前端迁移后API调用失败 | 先验证API接口，确保返回数据格式一致 |
| 数据丢失 | 用户登录状态丢失 | 使用localStorage持久化token |
| 样式不一致 | 新页面与旧页面样式差异 | 复用现有CSS，逐步统一 |
| 时间延误 | 迁移周期过长 | 分阶段迁移，每个阶段设置明确目标 |

---

## 十二、后续维护

1. **代码审查**：建立代码审查流程，确保代码质量
2. **测试覆盖**：添加单元测试和集成测试
3. **文档更新**：维护API文档和组件文档
4. **性能监控**：添加性能监控和错误追踪

---

## 附录：现有HTML文件映射

| 原文件 | 目标组件 | 状态 |
|--------|----------|------|
| index.html | Home.vue | ✅ |
| courses.html | Courses.vue | ✅ |
| news.html | News.vue | ✅ |
| platform.html | Platform.vue | ✅ |
| video.html | Video.vue | ✅ |
| about.html | About.vue | ✅ |
| profile.html | Profile.vue | ✅ |
| experiment.html | Experiment.vue | ✅ |
| course-detail.html | CourseDetail.vue | ✅ |
| login.html | Login.vue | ✅ |
| register.html | Register.vue | ✅ |