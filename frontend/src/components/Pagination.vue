<template>
  <div class="pagination" v-if="totalPages > 1">
    <span :class="{ disabled: page <= 1 }" @click="page > 1 && emit('update:page', page - 1)">‹</span>
    <span v-if="startPage > 1" @click="emit('update:page', 1)">1</span>
    <span v-if="startPage > 1" class="disabled">…</span>
    <span v-for="i in pages" :key="i" :class="{ active: i === page }" @click="emit('update:page', i)">{{ i }}</span>
    <span v-if="endPage < totalPages" class="disabled">…</span>
    <span v-if="endPage < totalPages" @click="emit('update:page', totalPages)">{{ totalPages }}</span>
    <span :class="{ disabled: page >= totalPages }" @click="page < totalPages && emit('update:page', page + 1)">›</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ page: number; total: number; pageSize: number }>()
const emit = defineEmits<{ 'update:page': [value: number] }>()

const totalPages = computed(() => Math.ceil(props.total / props.pageSize))
const startPage = computed(() => Math.max(1, props.page - 2))
const endPage = computed(() => Math.min(totalPages.value, props.page + 2))
const pages = computed(() => {
  const arr: number[] = []
  for (let i = startPage.value; i <= endPage.value; i++) arr.push(i)
  return arr
})
</script>

<style scoped>
.pagination {
  display: flex; justify-content: center; gap: 6px; margin: 32px 0;
}
.pagination span {
  width: 36px; height: 36px; display: flex;
  align-items: center; justify-content: center;
  border-radius: 8px; font-size: 14px; cursor: pointer;
  background: #fff; border: 1px solid #e8e8e8;
  transition: .2s; color: #555;
}
.pagination span:hover:not(.disabled) { border-color: #1a237e; color: #1a237e; }
.pagination span.active { background: #1a237e; color: #fff; border-color: #1a237e; }
.pagination span.disabled { opacity: .4; cursor: default; }
</style>
