/**
 * useTheme - Composable for theme management.
 *
 * This composable handles:
 * - Theme initialization from localStorage or system preference
 * - Theme toggle (light/dark)
 * - System theme change listener
 */

import { ref } from 'vue'

export function useTheme() {
  const isDarkMode = ref(false)
  let userManualOverride = false
  let mediaQuery = null
  let mediaQueryHandler = null

  function applyTheme(isDark) {
    document.documentElement.classList.toggle('dark', isDark)
  }

  function toggleTheme(value) {
    userManualOverride = true
    const theme = value ? 'dark' : 'light'
    localStorage.setItem('theme', theme)
    applyTheme(value)
  }

  function initTheme() {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      isDarkMode.value = savedTheme === 'dark'
      userManualOverride = true
    } else {
      isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    applyTheme(isDarkMode.value)
  }

  function bindSystemThemeListener() {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQueryHandler = (event) => {
      if (!userManualOverride) {
        isDarkMode.value = event.matches
        applyTheme(event.matches)
      }
    }
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', mediaQueryHandler)
    } else if (mediaQuery.addListener) {
      mediaQuery.addListener(mediaQueryHandler)
    }
  }

  function unbindSystemThemeListener() {
    if (mediaQuery && mediaQueryHandler) {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', mediaQueryHandler)
      } else if (mediaQuery.removeListener) {
        mediaQuery.removeListener(mediaQueryHandler)
      }
    }
  }

  return {
    isDarkMode,
    toggleTheme,
    initTheme,
    bindSystemThemeListener,
    unbindSystemThemeListener,
    applyTheme
  }
}
