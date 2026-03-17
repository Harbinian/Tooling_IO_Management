Primary Executor: Codex
Task Type: Bug Fix
Stage: 113
Goal: Fix frontend English locale issue - Element Plus and hardcoded English messages
Execution: RUNPROMPT

## 上下文 / Context

执行 052 任务后，前端出现了大量英文显示问题。主要原因：
1. Element Plus 组件没有配置中文语言包 (zhCn)
2. 新增的管理页面代码中使用了硬编码英文字符串

## 必需参考 / Required References

1. `frontend/src/main.js` - 应用入口文件
2. `frontend/src/pages/admin/UserAdminPage.vue` - 包含英文消息的页面
3. Element Plus 官方文档: 使用 `import zhCn from 'element-plus/dist/locale/zh-cn.mjs'`

## 核心任务 / Core Task

修复前端英文显示问题，确保所有 Element Plus 组件和业务消息显示中文。

## 必需工作 / Required Work

1. **配置 Element Plus 中文语言** (`main.js`)
   - 导入 `zhCn` from `element-plus/dist/locale/zh-cn.mjs`
   - 使用 `ElementPlusLocale` 配置全局 locale

2. **修复硬编码英文字符串** (`UserAdminPage.vue`)
   - `'Account created'` → `'账户创建成功'`
   - `'Account updated'` → `'账户更新成功'`
   - `'Password reset'` → `'密码重置成功'`
   - 检查并修复其他可能的英文消息

## 约束条件 / Constraints

1. 只修改必要的文件，不要改动其他业务逻辑
2. 确保 Element Plus 的 ElMessage, ElMessageBox, ElNotification 等组件显示中文
3. 保持代码风格与项目一致

## 完成标准 / Completion Criteria

1. Element Plus 组件（对话框、提示消息、日期选择器等）显示中文
2. UserAdminPage 中的操作反馈消息显示中文
3. 前端构建无错误：`cd frontend && npm run build`
