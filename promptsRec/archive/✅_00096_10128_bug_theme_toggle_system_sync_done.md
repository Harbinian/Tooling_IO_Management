Primary Executor: Gemini
Task Type: Bug Fix
Priority: P2
Stage: 129
Goal: Add system theme detection for initial theme on SettingsPage.vue
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

During E2E testing, a UX issue was discovered in `frontend/src/pages/settings/SettingsPage.vue`. The theme toggle doesn't respect the system's color scheme preference on initial load, causing user confusion.

**Location of issue**: `frontend/src/pages/settings/SettingsPage.vue:354-357`

```javascript
function initTheme() {
  const savedTheme = localStorage.getItem('theme')
  isDarkMode.value = savedTheme === 'dark'
}
```

The code only checks localStorage but doesn't check `prefers-color-scheme` if no theme is saved. This means:
1. If no theme is saved, it defaults to light mode even if user prefers dark
2. No automatic sync with system theme changes after initial load

---

## Required References / 必需参考

- `frontend/src/pages/settings/SettingsPage.vue` - File with theme toggle
- MDN prefers-color-scheme documentation
- Vue 3 composition API for media queries

---

## Core Task / 核心任务

Enhance theme initialization to respect system color scheme preference when no saved theme exists.

---

## Required Work / 必需工作

1. **Inspect SettingsPage.vue** to find `initTheme` function (lines 354-357)

2. **Update initTheme to check system preference**:
```javascript
function initTheme() {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'dark'
  } else {
    // No saved preference, use system preference
    isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  applyTheme()
}
```

3. **Add applyTheme function** to apply the theme:
```javascript
function applyTheme() {
  document.documentElement.classList.toggle('dark', isDarkMode.value)
}
```

4. **Update toggleTheme to also sync system preference**:
   - Consider listening to system theme changes
   - Or at minimum, ensure the toggle properly sets the class

5. **Test the changes**:
   - Open in browser with dark mode system preference and no saved theme
   - Verify dark mode is applied by default

---

## Constraints / 约束条件

- Do NOT remove the localStorage persistence
- Preserve existing theme toggle functionality
- Do NOT auto-switch when system theme changes (only use on first load)
- Keep the existing toggle UI intact

---

## Completion Criteria / 完成标准

1. **Acceptance Test 1**: Dark mode is applied by default if system prefers dark and no saved theme
2. **Acceptance Test 2**: Light mode is applied by default if system prefers light and no saved theme
3. **Acceptance Test 3**: Saved theme takes precedence over system preference
4. **Acceptance Test 4**: Toggle still works correctly to switch themes
5. **Acceptance Test 5**: Theme persists after page refresh
