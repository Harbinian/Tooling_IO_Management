<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'

function initTheme() {
  const savedTheme = localStorage.getItem('theme')
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const isDark = savedTheme === 'dark' || (!savedTheme && systemDark)
  
  document.documentElement.classList.toggle('dark', isDark)
  if (!savedTheme) {
    localStorage.setItem('theme', isDark ? 'dark' : 'light')
  }
}

onMounted(() => {
  initTheme()
})
</script>

<style>
/* Global styles can stay here or in index.css */
</style>
