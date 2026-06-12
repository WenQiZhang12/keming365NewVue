<script setup lang="ts">
import { useRoute } from 'vue-router'
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'

const route = useRoute()
</script>

<template>
  <template v-if="!route.meta.hideLayout">
    <Header />
    <main class="main-content">
      <router-view />
    </main>
    <Footer />
  </template>
  <router-view v-else />
</template>

<style lang="scss">
.main-content {
  min-height: calc(100vh - 64px - 100px);
  display: flex;
  flex-direction: column;
}
</style>
