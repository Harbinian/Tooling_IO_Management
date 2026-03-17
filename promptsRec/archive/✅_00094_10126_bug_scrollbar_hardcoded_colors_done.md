Primary Executor: Gemini
Task Type: Bug Fix
Priority: P2
Stage: 127
Goal: Fix dark mode scrollbar hardcoded colors in MainLayout.vue
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

During E2E testing, a dark mode CSS issue was discovered in `frontend/src/layouts/MainLayout.vue`. The scrollbar styles use hardcoded color values (#e2e8f0, #cbd5e1) instead of CSS variables, causing poor dark mode experience.

**Location of issue**: `frontend/src/layouts/MainLayout.vue:217-232`

```css
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
```

These hardcoded light-mode colors (#e2e8f0 is slate-200, #cbd5e1 is slate-300) don't adapt to dark mode.

---

## Required References / 必需参考

- `frontend/src/layouts/MainLayout.vue` - File with scrollbar styles
- `frontend/src/assets/main.css` or similar - CSS variables definitions
- `frontend/tailwind.config.js` - Tailwind theme configuration
- Check existing CSS variables usage in the codebase

---

## Core Task / 核心任务

Replace hardcoded scrollbar colors with CSS variables that support both light and dark modes.

---

## Required Work / 必需工作

1. **Inspect MainLayout.vue** to find scrollbar CSS (lines 217-232)

2. **Find CSS variables** being used in the project:
   - Look for `--background`, `--foreground`, `--border`, `--muted`, etc.
   - Check `main.css` or Tailwind config for the color scheme

3. **Replace hardcoded colors** with appropriate CSS variables:
   - Use `--muted` or `--border` for the scrollbar track/thumb
   - Use `--muted-foreground` for the hover state

4. **Example fix**:
```css
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--muted);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--muted-foreground);
}
```

5. **Verify dark mode works** by toggling theme in Settings

---

## Constraints / 约束条件

- Do NOT remove the scrollbar styling entirely
- Maintain the 6px width
- Keep the rounded corners
- Ensure scrollbar is still visible in both light and dark modes

---

## Completion Criteria / 完成标准

1. **Acceptance Test 1**: Scrollbar uses CSS variables instead of hardcoded #e2e8f0
2. **Acceptance Test 2**: Scrollbar uses CSS variables instead of hardcoded #cbd5e1
3. **Acceptance Test 3**: Scrollbar is visible in light mode
4. **Acceptance Test 4**: Scrollbar is visible in dark mode (with appropriate contrast)
5. **Acceptance Test 5**: Hover state works in both modes
