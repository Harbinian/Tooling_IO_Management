Primary Executor: Gemini
Task Type: Bug Fix
Priority: P0
Stage: 131
Goal: Fix OrderCreate.vue Chinese character encoding corruption causing build failure
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

**问题现象**:
- Vite 构建失败: `error: Element is missing end tag. (line 9, col 11)` in `OrderCreate.vue`
- 访问 `/order-create` 路由时返回 500 错误
- 浏览器控制台显示: `TypeError: Failed to fetch dynamically imported module: http://localhost:8150/src/pages/tool-io/OrderCreate.vue`

**根本原因**:
`frontend/src/pages/tool-io/OrderCreate.vue` 文件中的中文字符全部损坏为乱码（如 `鍒涘缓鍗曟嵁` 而非 `创建单据`）。文件从 GBK/GB2312 编码被错误转换为 UTF-8 时，字符未被正确映射，导致字节序列被破坏。

**损坏示例**:
| 行号 | 损坏内容 | 正确内容 |
|------|---------|---------|
| 7 | `鍒涘缓鍗曟嵁` | `创建单据` |
| 9 | `宸ヨ璁灞晓數鍑哄叆搴撶敵璇?/h1>` | `工装出入库申请</h1>` |
| 11 | 整段损坏 | `先从工装主表选择工装，再填写用途、目的位置和计划时间，最终生成并提交流出炉单。` |
| 21 | `阅嶇疆琛ㄥ崟` | `重置表格` |
| 29 | `鎼滅储骞舵坊鍔犲伐瑁?` | `搜索并添加工装` |

**影响范围**:
- 唯一受影响文件: `frontend/src/pages/tool-io/OrderCreate.vue`
- 前端 `npm run build` 失败
- 订单创建页面完全不可用

---

## Required References / 必需参考

1. `frontend/src/pages/tool-io/OrderCreate.vue` - 损坏的文件
2. `.claude/rules/00_global.md` - 全局规则，需添加编码强制规范
3. `frontend/vite.config.js` - Vite 配置
4. `docs/API_SPEC.md` - API 规范（参考字段映射）

---

## Core Task / 核心任务

修复 `OrderCreate.vue` 的编码问题，确保:
1. 所有中文字符正确显示
2. Vue 编译器能正确解析 `.vue` 文件
3. 前端构建成功
4. 在 `.claude/rules/00_global.md` 中添加编码强制规则防止复发

---

## Required Work / 必需工作

### Phase 1: 修复损坏的 Vue 文件

**步骤 1.1**: 从 Git 恢复原始文件（如果之前有正常版本）
```bash
git checkout HEAD -- frontend/src/pages/tool-io/OrderCreate.vue
```

**步骤 1.2**: 验证恢复后的文件
```bash
head -20 frontend/src/pages/tool-io/OrderCreate.vue | grep -E "创建单据|工装出入库|搜索并添加"
```
如果中文仍显示乱码，执行步骤 1.3。

**步骤 1.3**: 手动修复损坏的中文字符串
根据上下文还原以下损坏字符串:
- 第7行: `鍒涘缓鍗曟嵁` → `创建单据`
- 第9行: `宸ヨ璁灞晓數鍑哄叆搴撶敵璇?/h1>` → `工装出入库申请</h1>`
- 第11行: 整段描述文字 → `先从工装主表选择工装，再填写用途、目的位置和计划时间，最终生成并提交流出炉单。`
- 第21行: `阅嶇疆琛ㄥ崟` → `重置表格`
- 第29行: `鎼滅储骞舵坊鍔犲伐瑁?` → `搜索并添加工装`
- 第43行: `鍩烘湰淇℃伅` → `基本信息`
- 第49行: `鍗曟嵁绫诲瀷` → `单据类型`
- 以及文件中所有其他损坏的中文字符

**步骤 1.4**: 修复文件编码
- 确保文件以 UTF-8 (无 BOM) 编码保存
- 统一行结束符为 LF（Unix 风格）

### Phase 2: 更新全局规则

在 `.claude/rules/00_global.md` 中添加编码强制规范:

```markdown
## 编码强制检查 / Encoding Enforcement

所有 `.vue`、`.js`、`.ts`、`.py` 文件必须以 UTF-8 (无 BOM) 编码保存。

**禁止**: 使用非 UTF-8 编码保存任何源代码文件。

中文乱码特征字符（检测到立即报警）:
- `鍒涘缓` (应为"创建")
- `宸ヨ` (应为"工装")
- `鎼滅储` (应为"搜索")
- `鍗曟` (应为"单据")
```

### Phase 3: 验证修复

```bash
# 1. 前端构建验证
cd frontend && npm run build

# 2. 确认构建成功无错误
# 输出应为 "Build completed"

# 3. 检查无乱码字符残留
grep -r "鍒涘缓\|宸ヨ\|鎼滅储\|鍗曟" frontend/src/
```

---

## Constraints / 约束条件

1. **禁止重新设计**: 不得修改组件的业务逻辑或结构，只修复编码问题
2. **保留所有功能**: 所有现有的 `<script setup>` 逻辑、`v-model` 绑定、`@click` 处理器必须保持不变
3. **样式一致性**: 不得修改 `<style scoped>` 中的任何 CSS
4. **UTF-8 纯度**: 修复后文件必须是无 BOM 的纯 UTF-8
5. **行结束符**: 统一使用 LF (`\n`)

---

## Completion Criteria / 完成标准

1. ✅ `npm run build` 成功完成，无错误输出
2. ✅ 文件中无乱码字符（`鍒涘缓`、`宸ヨ`、`鎼滅储` 等）
3. ✅ 所有中文字符正确显示
4. ✅ `.claude/rules/00_global.md` 已添加编码强制规范
5. ✅ Vite 开发服务器能正确加载 `/order-create` 页面
6. ✅ 页面上的"创建单据"、"工装出入库申请"、"搜索并添加工装"等文字正确显示
