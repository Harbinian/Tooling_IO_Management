---
name: frontend-design
description: 创建独特、生产级的前端界面，具有高设计质量。当用户要求构建 Web 组件、页面或应用程序时使用。生成创意精致的代码，避免通用的 AI 美学。/ Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.
license: Complete terms in LICENSE.txt
---

# 前端设计技能 / Frontend Design Skill

本技能指导创建独特、生产级的前端界面，避免通用的"AI 垃圾"美学。实现真正可工作的代码，注重美学细节和创意选择。/ This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

用户提供前端需求：要构建的组件、页面、应用程序或界面。他们可能包括关于目的、受众或技术约束的上下文。/ The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## 设计思维 / Design Thinking

在编码之前，理解上下文并承诺一个大胆的美学方向：/ Before coding, understand the context and commit to a BOLD aesthetic direction:

- **目的 / Purpose**: 这个界面解决什么问题？谁使用它？
- **风格 / Tone**: 选择一个极端：极致简约、极繁主义、复古未来主义、有机/自然、奢华/精致、玩具般有趣、编辑/杂志、野蛮主义/原始、装饰艺术/几何、柔和/粉彩、工业/实用等。有很多风格可供选择。使用这些作为灵感，但设计一个符合美学方向的真正方案。
- **约束 / Constraints**: 技术要求（框架、性能、可访问性）。
- **差异化 / Differentiation**: 什么让这令人难忘？人们会记住的一件事是什么？

**关键 / CRITICAL**: 选择清晰的概念方向并精确执行。大胆的极繁主义和精致的极简主义都可以工作——关键是有意性，而不是强度。/ **CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

然后实现可工作的代码（HTML/CSS/JS、React、Vue 等）：/ Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:

- 生产级且功能正常 / Production-grade and functional
- 视觉上令人印象深刻且令人难忘 / Visually striking and memorable
- 具有清晰美学观点的一致性 / Cohesive with a clear aesthetic point-of-view
- 在每个细节上精炼 / Meticulously refined in every detail

## 前端美学指南 / Frontend Aesthetics Guidelines

关注：/ Focus on:

- **字体排版 / Typography**: 选择美丽、独特、有趣的字体。避免使用通用字体如 Arial 和 Inter；相反，选择能提升前端美学的独特选择；意想不到的、有特色的字体选择。将独特的展示字体与精致的正文字体配对。
- **颜色与主题 / Color & Theme**: 承诺一致的美学。使用 CSS 变量保持一致性。禁止使用硬编码颜色（如 `text-white`, `bg-slate-900`），必须使用语义化变量。/ Commit to a cohesive aesthetic. Use CSS variables for consistency. Hardcoded colors (e.g., `text-white`, `bg-slate-900`) are FORBIDDEN; semantic variables must be used.

### 主题配色规范 / Theme Color Specifications

为了确保在明暗主题下均具有极佳的可读性和一致性，必须遵循以下配色规则：/ To ensure excellent readability and consistency across light and dark themes, the following color rules must be followed:

#### 1. 首要颜色与对比色 / Primary & Contrast Colors
| 场景 / Scenario | 浅色模式 (Light) | 深色模式 (Dark) | 配合规则 / Contrast Rule |
| :--- | :--- | :--- | :--- |
| **Primary (品牌主色)** | `hsl(240 5.9% 10%)` | `hsl(240 5.9% 10%)` | 在此背景上必须使用 `text-primary-foreground` |
| **Background (基础背景)** | `hsl(0 0% 100%)` | `hsl(240 10% 3.9%)` | 承载正文文字 `text-foreground` |
| **Card (容器/卡片)** | `hsl(0 0% 100%)` | `hsl(240 10% 3.9%)` | 悬停态使用 `hover:bg-accent` |
| **Muted (次要文字)** | `hsl(240 3.8% 46.1%)` | `hsl(240 5% 84.9%)` | 用于标签、描述，确保深色模式下亮度足够 |

#### 2. 多元素配合原则 / Multi-element Coordination
- **Header / Hero 区域**: 通常使用 `bg-primary`。内部所有文字必须使用 `text-primary-foreground`（而非 `text-white`），边框使用 `border-primary-foreground/20`。
- **输入框与选择框 (Forms)**: 统一使用 `border-input` 和 `bg-background/50`。避免在页面调用处硬编码 `bg-background` 或 `bg-white` 覆盖组件默认样式。
- **状态标签 (Tags/Badges)**: 优先使用 `variant="outline"` 配合 `border-primary/20`。在深色背景上，使用 `text-primary-foreground`。

#### 3. 禁止行为 / Forbidden Actions
- **严禁**在全局或共享组件中使用 `text-white` 或 `text-black`。
- **严禁**在深色模式下将 `primary` 颜色反转为浅色（除非是纯文字点缀）。
- **严禁**在卡片容器内使用与卡片背景完全相同的背景色（如 `bg-background` 覆盖 `bg-card`），应使用透明度或 `bg-muted` 区分层级。
- **动效 / Motion**: 使用动画实现效果和微交互。优先为 HTML 使用纯 CSS 解决方案。使用 Motion 库为 React（如果可用）。专注于高影响时刻：一个编排良好的页面加载与交错揭示（animation-delay）比分散的微交互创造更多愉悦。使用滚动触发和悬停状态带来惊喜。
- **空间构图 / Spatial Composition**: 意想不到的布局。不对称。重叠。对角线流动。打破网格元素。慷慨的负空间或受控密度。
- **背景与视觉细节 / Backgrounds & Visual Details**: 创造氛围和深度，而不是默认为纯色。添加与整体美学匹配的上下文效果和纹理。应用创意形式，如渐变网格、噪点纹理、几何图案、分层透明度、戏剧性阴影、装饰边框、自定义光标和颗粒叠加。

永远不要使用通用的 AI 生成美学，如过度使用的字体系列（Inter、Roboto、Arial、系统字体）、老套的配色方案（尤其是白色背景上的紫色渐变）、可预测的布局和组件模式，以及缺乏上下文特性的cookie-cutter 设计。/ NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

创意地解释并做出与上下文真正设计的意想不到的选择。每个设计都应该是不同的。在浅色和深色主题、不同的字体、不同的美学之间变化。永远不要在多代中收敛于常见选择（例如 Space Grotesk）。/ Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**重要 / IMPORTANT**: 将实现复杂性与美学愿景匹配。极繁主义设计需要包含大量动画和效果的复杂代码。简约或精致的设计需要克制、精确，以及对间距、字体排版和微妙细节的精心关注。优雅来自于良好地执行愿景。/ **IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

记住：Claude 能够做出非凡的创意工作。不要保守，展示真正跳出框框并完全承诺独特愿景时能创造出什么。/ Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.
