Primary Executor: Gemini
Task Type: Feature Development
Priority: P2
Stage: 060
Goal: Implement dark mode CSS theme support
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

前端 Settings 页面已实现主题切换开关，但深色模式仅通过 Element Plus 的 `dark` 类切换，未实现完整的 CSS 变量支持。需要为系统添加完整的深色/浅色主题切换。

## Required References / 必需参考

- `frontend/src/pages/settings/SettingsPage.vue` - 设置页面
- `frontend/src/main.js` - 应用入口
- `frontend/src/App.vue` - 根组件
- `frontend/index.html` - HTML 模板
- Tailwind CSS 配置（如有）

## Core Task / 核心任务

实现完整的深色/浅色主题切换功能：
1. 定义 CSS 变量
2. 实现主题切换逻辑
3. 确保所有组件适配深色模式

## Required Work / 必需工作

1. **定义主题 CSS 变量**
   - 在 `frontend/src/styles/` 创建 `theme.css` 或在现有样式文件中添加
   - 定义颜色变量：background, surface, text, border 等
   - 同时定义 light 和 dark 两套变量

2. **实现主题切换逻辑**
   - 修改 `SettingsPage.vue` 中的 `toggleTheme` 函数
   - 将主题保存到 localStorage (`theme: 'light' | 'dark'`)
   - 应用到 `document.documentElement` 或根元素

3. **确保主题初始化**
   - 在 `main.js` 或 `App.vue` 中初始化主题
   - 从 localStorage 读取或使用系统偏好

4. **适配深色模式**
   - 确保所有 UI 组件在深色模式下可读
   - 特别注意：Cards, Inputs, Tables, Dialogs
   - 可使用 Element Plus 的 `dark` 模式或自定义 CSS

## Constraints / 约束条件

- 不得破坏现有浅色模式
- 遵循项目 UI 规范（深色主题也应该美观）
- 主题切换应流畅，无闪烁

## Completion Criteria / 完成标准

1. 切换主题后所有页面元素正确显示
2. 刷新页面后主题保持不变
3. 首次访问时使用系统偏好或默认浅色
4. 前端构建通过：`cd frontend && npm run build`
5. 手动验证：切换主题后刷新页面，主题保持
