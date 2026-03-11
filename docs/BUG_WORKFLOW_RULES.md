# Bug 工作流规则 / BUG WORKFLOW RULES

本文档定义 AI 辅助开发管道中使用的 bug 工作流。

This document defines the bug workflow used by the AI-assisted development pipeline.

目标是防止提示词泛滥，并确保单个缺陷作为受控的修复链处理。

The goal is to prevent prompt explosion and ensure that a single defect is handled as a controlled repair chain.

---

# 1 核心原则 / 1 Core Principle

一个 bug 必须只有一个主要的 bug 提示词。

One bug must have only one primary bug prompt.

调试期间发现的所有子问题必须记录在同一个 bug 文档中，而不是创建新的提示词。

All sub-issues discovered during debugging must be recorded in the same bug document instead of creating new prompts.

这确保调试保持为单一的持续调查。

This ensures that debugging remains a single continuous investigation.

---

# 2 Bug 提示词结构 / 2 Bug Prompt Structure

每个 bug 都从一个完全主要的提示词开始。

Every bug begins with exactly one primary prompt.

示例：

Example:

promptsRec/103_bug_order_list_api_500.md

此提示词负责整个 bug 的调查和修复。

This prompt is responsible for the entire investigation and fix of the bug.

它必须保持该缺陷的唯一真实来源。

It must remain the single source of truth for that defect.

---

# 3 Bug 文档 / 3 Bug Documentation

每个 bug 必须有一个文档文件：

Each bug must have a documentation file:

docs/BUG_<NAME>.md

示例：

Example:

docs/BUG_ORDER_LIST_API_500.md

此文档记录完整的调试过程。

This document records the full debugging process.

必需章节：

Required sections:

## 症状 / Symptom

观察到的运行时行为。 / Observed runtime behavior.

## 根本原因 / Root Cause

确认的缺陷原因。 / Confirmed cause of the defect.

## 子问题 / Sub-Issues

调查期间发现的额外问题。

Additional problems discovered during investigation.

这些不得创建新的 bug 提示词，除非满足升级规则。

These must not create new bug prompts unless they satisfy escalation rules.

## 修复 / Fix

最终的代码或配置更改。 / Final code or configuration changes.

## 验证 / Verification

问题已解决的证明。 / Proof that the issue is resolved.

---

# 4 子问题处理 / 4 Sub-Issue Handling

调试期间出现额外问题时：

When additional issues appear during debugging:

不要立即创建新提示词。

DO NOT create a new prompt immediately.

相反，将它们追加到：

Instead append them under:

子问题 / Sub-Issues

示例：

Example:

子问题 1：分页查询不匹配 / Sub-Issue 1: pagination query mismatch
子问题 2：日期时间序列化失败 / Sub-Issue 2: datetime serialization failure

这些被视为同一 bug 链的一部分。

These are considered part of the same bug chain.

---

# 5 升级规则 / 5 Escalation Rule

只有满足所有条件才能创建新的 bug 提示词：

A new bug prompt may be created only if ALL conditions are satisfied:

1. 根本原因与原始 bug 无关 / The root cause is unrelated to the original bug
2. 问题属于不同的子系统 / The issue belongs to a different subsystem
3. 修复无法在当前 bug 范围内安全完成 / The fix cannot be safely completed inside the current bug scope

示例升级：

Example escalation:

Bug 103: 订单列表 API 失败 / Bug 103: order list API failure

发现的根本原因：

Root cause discovered:

跨模块的数据库架构不匹配 / database schema mismatch across modules

这可能会升级为：

This may escalate into:

104_bug_database_schema_alignment.md

---

# 6 Bug 生命周期 / 6 Bug Lifecycle

Bug 生命周期：

Bug lifecycle:

检测到事件 / Incident detected
→ 事件捕获 / incident-capture
→ Bug 分类 / bug-triage
→ 创建主要 bug 提示词 / create primary bug prompt
→ 调查和修复 / investigation and fixes
→ 验证 / verification
→ 归档 bug 提示词 / archive bug prompt

子问题保留在同一 bug 文档中。

Sub-issues remain within the same bug documentation.

---

# 7 提示词编号 / 7 Prompt Numbering

Bug 提示词必须遵循此编号方案。

Bug prompts must follow this numbering scheme.

100–199 = Bug 修复 / Bug Fix

示例：

Examples:

101_bug_tool_search_request_routing
102_bug_vite_entry_compile_failure
103_bug_order_list_api_500

功能提示词保持在 000–099 范围内。

Feature prompts remain in the 000–099 range.

---

# 8 自动化目标 / 8 Automation Goal

Bug 工作流最终必须由自动化技能驱动：

The bug workflow must eventually be driven by automated skills:

- 事件监控 / incident-monitor
- 事件捕获 / incident-capture
- Bug 分类 / bug-triage
- Bug 后续管理器 / bug-followup-manager

后续管理器决定是否需要新的 bug 提示词。

The followup manager decides whether a new bug prompt is required.

---

# 9 预期收益 / 9 Expected Benefits

此工作流确保：

This workflow ensures:

可预测的 bug 范围 / Predictable bug scope
受控的调试链 / Controlled debugging chains
无提示词泛滥 / No prompt explosion
清晰的调查文档 / Clear investigation documentation
更好的自动化支持 / Better automation support
