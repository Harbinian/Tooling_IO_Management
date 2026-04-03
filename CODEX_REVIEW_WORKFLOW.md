# Codex 审查后标准操作清单

适用场景：你在 `https://chatgpt.com/codex` 完成一轮代码审查后，需要决定下一步是修复、提交、同步远端还是继续审查。

---

## 1. 先检查本地状态

先执行：

```powershell
git status --short --branch
```

目标：

- 确认当前分支
- 确认工作区是否干净
- 确认本地相对远端是 `ahead`、`behind` 还是分叉

规则：

- 工作区不干净时，不要直接 `git pull`
- 如果当前就在 `main` 上，优先考虑先切修复分支再继续

---

## 2. 判断审查结果是否需要改代码

分两类处理：

### A. 审查无阻断问题

如果 review 结论是补丁正确，通常只需要：

1. 整理当前改动
2. 提交或推送
3. 再同步远端

### B. 审查发现问题需要修复

如果 review 有 findings：

1. 先固定当前状态
2. 再进入修复
3. 修复后重新验证
4. 再做一轮审查闭环

---

## 3. 如果工作区不干净，先处理现场

### 情况 A：这些改动就是你要保留的

继续在当前分支修复，或者先提交一个中间版本。

### 情况 B：这些改动暂时不想处理

先暂存：

```powershell
git stash push
```

### 情况 C：改动很多而且混杂

先做分组，不要急着拉取远端：

- 代码修复
- 文档同步
- 提示词归档
- 日志/测试产物

---

## 4. 修复问题时的推荐顺序

1. 根据审查结论修代码
2. 补测试或更新测试
3. 跑最小必要验证
4. 再做一次审查闭环

常用验证：

```powershell
python -m py_compile <files>
python -m pytest <tests> -q
cd frontend
npm run build
```

---

## 5. 修复完成后再同步远端

不要在“未整理工作区”的情况下直接拉取。

推荐顺序：

```powershell
git fetch origin
git status --short --branch
```

然后判断：

- 如果本地只 `ahead` 不 `behind`：可以直接提交/推送
- 如果本地 `behind`：先 `git pull --rebase`
- 如果既有本地改动又有远端更新：先提交或 stash，再 `pull --rebase`

---

## 6. 推荐使用 `pull --rebase`

优先使用：

```powershell
git pull --rebase
```

原因：

- 历史更干净
- 不容易产生无意义 merge commit
- 更适合代码审查后的小步修复流程

前提：

- 你的工作区已经干净，或改动已被提交 / stash

---

## 7. 不建议直接在这些情况下 pull

以下情况先不要 `pull`：

- 工作区有未处理改动
- 审查刚发现问题，还没修
- 你还没决定哪些文件要提交
- 仓库里同时有提示词归档、日志、测试产物等流程文件改动

---

## 8. 最稳妥的固定流程

每次审查后都按这个顺序：

1. `git status --short --branch`
2. 判断是否需要修复
3. 如需修复，先修代码并验证
4. 再做审查闭环
5. 提交当前改动
6. `git fetch origin`
7. 如有需要，`git pull --rebase`
8. `git push`

---

## 9. 一句话原则

- 工作区不干净：先别 pull
- 审查有问题：先修再同步
- 准备同步远端：先提交或 stash
- 想保持历史干净：优先 `pull --rebase`
