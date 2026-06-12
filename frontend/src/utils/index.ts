const IMG_BASE = 'https://www.keming365.com/images'

export function getImageUrl(path: string): string {
  if (!path) return ''
  if (path.startsWith('http')) return path
  try { path = decodeURIComponent(path) } catch { /* ignore */ }
  return IMG_BASE + (path.startsWith('/') ? '' : '/') + path
}

export function escapeHtml(str: string): string {
  if (!str) return ''
  return String(str).replace(/[&<>"']/g, (m) => {
    const map: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }
    return map[m] || m
  })
}

export function stripHtml(html: string): string {
  return (html || '').replace(/<[^>]+>/g, '')
}

export function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  return dateStr.slice(0, 10)
}

// 机械工程课程排序
const ME_ORDER: string[] = [
  '工程制图', '机械制图', '理论力学', '材料力学',
  '机械原理', '机械设计', '互换性与测量技术', '机械制造技术基础',
  '工程材料', '材料成型技术基础', '现代制造技术', '数控技术',
  '液压与气压传动', '机电传动控制', '机械工程测试技术',
  'CAD/CAM技术及应用', '有限元分析', '模具设计',
  '机械制造装备设计', '先进制造技术'
]
const ME_ORDER_MAP: Record<string, number> = {}
ME_ORDER.forEach((name, i) => { ME_ORDER_MAP[name] = i })

export function sortMechanicalEngineering(a: { curriculumName: string }, b: { curriculumName: string }): number {
  const ai = ME_ORDER_MAP[a.curriculumName] ?? 999
  const bi = ME_ORDER_MAP[b.curriculumName] ?? 999
  return ai - bi
}

// 分类图标映射
export const CLASSIFY_ICONS: Record<string, string> = {
  '机械工程': '⚙️', '工程训练': '🔧', '力学': '📐', '土木工程': '🏗️',
  '大学物理': '🔭', '能源动力': '🔥', '水利工程': '💧', '生物工程': '🧬',
  '文化艺术': '🎨', '装配式建筑': '🏠', '航海类': '⛵'
}

export function getClassifyIcon(name: string): string {
  return CLASSIFY_ICONS[name] || '📚'
}

// Toast 工具
export function toast(msg: string, type: 'success' | 'error' | 'info' = 'info') {
  const el = document.createElement('div')
  el.className = 'toast ' + type
  el.textContent = msg
  document.body.appendChild(el)
  setTimeout(() => el.remove(), 2500)
}
