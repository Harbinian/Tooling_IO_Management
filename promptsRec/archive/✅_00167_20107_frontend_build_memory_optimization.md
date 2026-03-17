# Prompt 20107: Frontend Build Memory Optimization

Primary Executor: Gemini
Task Type: Refactor
Priority: P2
Stage: 20107
Goal: Fix frontend build out-of-memory error and optimize build configuration
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

前端 Vite 构建时出现 JavaScript heap out of memory 错误：

```
FATAL ERROR: Zone Allocation failed - process out of memory
----- Native stack trace -----
FATAL ERROR: MarkCompactCollector: young object promotion failed Allocation failed - JavaScript heap out of memory
```

错误发生在 `vite build` 阶段。

---

## Required References / 必需参考

- `frontend/vite.config.js` 或 `frontend/vite.config.ts` - Vite 配置
- `frontend/package.json` - 依赖和构建脚本
- `frontend/src/` - 源代码结构

---

## Core Task / 核心任务

### 1. 诊断内存溢出原因

分析以下可能原因：
- 大型依赖包（如 element-plus、vue 等）未正确 tree-shaking
- 大量组件/页面导致构建时内存占用过高
- Vite 配置优化不足

### 2. 应用优化方案

根据诊断结果，实施以下优化：

#### Option A: Vite 配置优化
如果适用，修改 `vite.config.js`:
```javascript
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'element-plus': ['element-plus'],
        'vue-vendor': ['vue', 'vue-router', 'pinia'],
      }
    }
  },
  chunkSizeWarningLimit: 1500,
}
```

#### Option B: 增加 Node 内存限制
修改 `package.json` 的 build 脚本：
```json
"build": "node --max-old-space-size=4096 node_modules/vite/bin/vite.js build"
```

#### Option C: 分析并移除不必要的依赖
检查 `package.json` 中的依赖，移除未使用的包

### 3. 验证修复

运行构建命令验证：
```bash
cd frontend && npm run build
```

确保构建成功且产物大小合理。

---

## Constraints / 约束条件

1. 不得破坏现有功能
2. 保持 Element Plus 暗色主题支持
3. 构建产物大小优化（单 chunk 不超过 2MB）
4. 构建时间优化目标：不超过 5 分钟

---

## Completion Criteria / 完成标准

1. `npm run build` 在 4GB 内存限制下成功完成
2. 构建产物大小合理（vendor chunk 不超过 3MB）
3. 构建时间不超过 5 分钟
4. 暗色主题仍然正常工作

---

## Output / 输出

生成优化后的 `vite.config.js` 和 `package.json`（如需修改），并报告优化效果。
