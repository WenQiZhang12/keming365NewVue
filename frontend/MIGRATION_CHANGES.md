# Vue SPA 迁移变更文档（Phase 3 - 完整迁移）

## 〇、本次新增（Phase 4：HTML全部迁移）

### 新增 11 个页面组件

| 文件路径 | 对应原文件 | 路由 | 说明 |
|---------|-----------|------|------|
| `frontend/src/views/CourseDetail.vue` | `media/course-detail.html` | `/course/:id` | 课程详情，章节树+实验列表+价格侧边栏 |
| `frontend/src/views/Experiment.vue` | `media/experiment.html` | `/experiment/:id` | 实验操作页，Canvas图表+启动VR仿真 |
| `frontend/src/views/Profile.vue` | `media/profile.html` | `/profile` | 个人中心，统计+Tab（实验/成绩/订单） |
| `frontend/src/views/Lesson.vue` | `media/lesson.html` | `/lesson?id=...` | 课时播放页 |
| `frontend/src/views/Files.vue` | `media/files.html` | `/files` | 文件管理，拖拽上传+预览 |
| `frontend/src/views/Admin.vue` | `media/admin.html` | `/admin` | 管理后台，用户/课程管理+系统监控 |
| `frontend/src/views/ReviewReport.vue` | `media/review-report.html` | `/review-report` | 评阅报告，通过/驳回 |
| `frontend/src/views/StudentReports.vue` | `media/student-reports.html` | `/student-reports` | 学生报告列表 |
| `frontend/src/views/TeacherReports.vue` | `media/teacher-reports.html` | `/teacher-reports` | 教师报告管理 |
| `frontend/src/views/ApiTest.vue` | `media/api_test.html` | `/api-test` | API调试工具（开发用） |
| `frontend/src/views/CreateAdmin.vue` | `media/create_admin.html` | `/create-admin` | 创建管理员（独立布局） |

### 路由新增 12 条

`/course/:id`、`/experiment/:id`、`/lesson`、`/profile`、`/files`、`/admin`、`/review-report`、`/student-reports`、`/teacher-reports`、`/api-test`、`/create-admin`

### Header.vue 修改

- `goProfile` 改为 `router.push('/profile')`（之前是 `window.location.href = '/media/profile.html'`）
- `openAdmin` 改为 `router.push('/admin')`（之前是 `window.open` 到外部URL）

---

## 一、新建文件

### 1. 页面组件（6个）

| 文件路径 | 对应原文件 | 路由 | 说明 |
|---------|-----------|------|------|
| `frontend/src/views/Login.vue` | `media/login.html` | `/login` | 登录页，独立布局（无Header/Footer），使用Pinia用户状态 |
| `frontend/src/views/Register.vue` | `media/register.html` | `/register` | 注册页，独立布局，字段验证+API调用 |
| `frontend/src/views/NewsDetail.vue` | `media/news-detail.html` | `/news/:id` | 新闻详情页，调用 getNewsDetail API，v-html 渲染内容 |
| `frontend/src/views/Platform.vue` | `media/platform.html` | `/platform` | 平台简介，纯静态展示，6个背景图section |
| `frontend/src/views/About.vue` | `media/about.html` | `/about` | 关于我们，hero区域+统计卡片+联系方式 |
| `frontend/src/views/Video.vue` | `media/video.html` | `/video` | 职教出海，国家选择+课程菜单+课程网格+分页 |

### 2. 数据文件（1个）

| 文件路径 | 说明 |
|---------|------|
| `frontend/src/data/videoCourses.ts` | 职教出海课程数据：5个国家、15门课程分类、完整课程卡片数据（标题/封面/链接） |

---

## 二、修改文件

### 1. 路由配置 `frontend/src/router/index.ts`

**新增6条路由：**
```typescript
{ path: '/news/:id', name: 'NewsDetail', component: () => import('@/views/NewsDetail.vue') },
{ path: '/platform', name: 'Platform', component: () => import('@/views/Platform.vue') },
{ path: '/about', name: 'About', component: () => import('@/views/About.vue') },
{ path: '/video', name: 'Video', component: () => import('@/views/Video.vue') },
{ path: '/login', name: 'Login', component: () => import('@/views/Login.vue'), meta: { hideLayout: true } },
{ path: '/register', name: 'Register', component: () => import('@/views/Register.vue'), meta: { hideLayout: true } },
```
- Login/Register 使用 `meta: { hideLayout: true }` 隐藏全局Header/Footer

### 2. API层 `frontend/src/api/index.ts`

**新增 register 函数：**
```typescript
export async function register(params: {
  username: string; name: string; password: string; telephone?: string
}): Promise<void> {
  await api.post('/accounts/auth/register/', params)
}
```

### 3. 根组件 `frontend/src/App.vue`

**条件渲染Header/Footer：**
```vue
<template v-if="!route.meta.hideLayout">
  <Header />
  <main class="main-content"><router-view /></main>
  <Footer />
</template>
<router-view v-else />
```
- 登录/注册页面不显示Header和Footer

### 4. 头部导航 `frontend/src/components/Header.vue`

**导航链接改为Vue路由：**
```typescript
// 之前
{ path: '/media/platform.html', name: '平台简介' },
{ path: '/media/video.html', name: '职教出海' },
{ path: '/media/about.html', name: '关于我们' },

// 之后
{ path: '/platform', name: '平台简介' },
{ path: '/video', name: '职教出海' },
{ path: '/about', name: '关于我们' },
```

**登录/注册链接改为router-link：**
```vue
<router-link to="/login" class="btn btn-login">登录</router-link>
<router-link to="/register" class="btn btn-reg">注册</router-link>
```

### 5. 新闻列表 `frontend/src/views/News.vue`

**新闻详情链接：**
```javascript
// 之前
window.open('/media/news-detail.html?id=' + id, '_blank')
// 之后
window.open('/news/' + id, '_blank')
```

### 6. 首页 `frontend/src/views/Home.vue`

**6a. 新闻详情链接：**
```javascript
// 之前
window.open('/media/news-detail.html?id=' + id, '_blank')
// 之后
window.open('/news/' + id, '_blank')
```

**6b. 实验卡片缩略图 - 移除渐变背景：**
```scss
// 之前
.experiment-thumb {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
}
// 之后
.experiment-thumb {
  background: #f0f2f5;
}
```

**6c. 实验卡片布局 - flex滚动改为grid等宽：**
```scss
// 之前
.experiment-scroll {
  display: flex; gap: 20px; overflow-x: auto;
  padding-bottom: 8px; height: 220px;
}
.experiment-card { flex: 0 0 200px; }

// 之后
.experiment-scroll {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 24px;
}
.experiment-card { /* 无需固定宽度 */ }
```
- 卡片自动填满容器宽度，与"更多 →"右对齐
- 间距从20px加宽到24px

### 7. 课程页 `frontend/src/views/Courses.vue`

**实验卡片缩略图 - 移除渐变背景+增大高度：**
```scss
// 之前
.course-card {
  &:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,.12); }
  .thumb { height: 140px; background: linear-gradient(135deg, #e3f2fd, #bbdefb); }
}

// 之后
.course-card {
  &:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,.12); }
  .thumb { height: 180px; background: #f0f2f5; position: relative; }
}
```
- 移除蓝色渐变"透明层"遮挡
- 缩略图高度140px→180px，展示更多图片
- hover位移减小，避免视觉残影

---

## 三、路由总览

| 路由路径 | 页面名称 | 布局 |
|---------|---------|------|
| `/` | 首页 Home | 有Header/Footer |
| `/courses` | 全部课程 Courses | 有Header/Footer |
| `/news` | 新闻资讯 News | 有Header/Footer |
| `/news/:id` | 新闻详情 NewsDetail | 有Header/Footer |
| `/platform` | 平台简介 Platform | 有Header/Footer |
| `/about` | 关于我们 About | 有Header/Footer |
| `/video` | 职教出海 Video | 有Header/Footer |
| `/course/:id` | 课程详情 CourseDetail | 有Header/Footer |
| `/experiment/:id` | 实验操作 Experiment | 有Header/Footer |
| `/lesson` | 课时播放 Lesson | 有Header/Footer |
| `/profile` | 个人中心 Profile | 有Header/Footer |
| `/files` | 文件管理 Files | 有Header/Footer |
| `/admin` | 管理后台 Admin | 有Header/Footer |
| `/review-report` | 评阅报告 ReviewReport | 有Header/Footer |
| `/student-reports` | 我的报告 StudentReports | 有Header/Footer |
| `/teacher-reports` | 教师报告 TeacherReports | 有Header/Footer |
| `/api-test` | API测试 ApiTest | 有Header/Footer |
| `/login` | 登录 Login | **无**Header/Footer |
| `/register` | 注册 Register | **无**Header/Footer |
| `/create-admin` | 创建管理员 CreateAdmin | **无**Header/Footer |

---

## 四、构建验证

- `npm run build` 通过，无TypeScript错误
- 开发服务器 `http://localhost:5173/` 正常运行
- Django后端 `http://localhost:8000/` 正常运行
