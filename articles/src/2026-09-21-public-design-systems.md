---
title: 公开设计系统清单：10 套官方规范的定位、授权与取用方式
description: 从 Apple HIG、Material Design 到 IBM Carbon、GOV.UK、USWDS，整理 10 套公开设计系统的官方入口、适用场景与授权情况，并给出一套把规范落进团队日常评审的做法。
date: 2026-09-21
tags: [设计规范, 资源清单]
keywords: 设计系统,design system,Material Design,Human Interface Guidelines,Carbon,Ant Design,GOV.UK Design System,USWDS,Primer,设计规范
draft: false
---

做界面时最省时间的做法，往往不是从零制定规范，而是找一套已经被大量真实用户用过的公开规范作参照：它替你回答过「按钮该多高」「报错文案该放哪」这类反复争论的问题。

但「公开」不等于「随便用」。这些规范里，有的只是文档，有的是连组件代码和设计令牌一起开源，授权范围差别很大。下面按使用场景分三类，列出 10 套确认仍在线、且有明确官方入口的设计系统。

## 一、先分清三类「规范」，别拿错档

- **平台型指南**：Apple、Google 为自己的操作系统写的规范。它回答的是「在这套系统里怎么做才不违和」，通常**不提供可直接商用的组件代码**。
- **开源设计系统**：企业把自己产品的设计语言、组件库、设计令牌一起开源，授权写在仓库里，可以直接拿来改。
- **索引与清单**：别人整理好的设计系统目录。它**不是规范本身**，价值在于帮你快速找到更多来源。

分清这三类能避免一个常见错误：把平台型指南当组件库用。它给的是原则、尺寸与交互逻辑，不是按钮的现成代码。

## 二、平台型：Apple HIG 与 Material Design

**Apple Human Interface Guidelines**（[developer.apple.com/design/human-interface-guidelines](https://developer.apple.com/design/human-interface-guidelines)）：覆盖 iOS、iPadOS、macOS、watchOS、tvOS 与 visionOS，按「组件 + 交互模式」组织，配套的设计资源与模板在 [developer.apple.com/design/resources](https://developer.apple.com/design/resources)。它的价值不只是排版细节，而是解释「为什么在这个平台要这么做」。注意一点：**Apple 的字体（SF 系列等）与官方设计资源有单独授权条款**，做商用项目之前，以 Apple 官方说明为准。

**Material Design 3**（[m3.material.io](https://m3.material.io/)）：Google 的跨平台规范，M3 这一代把**动态配色（dynamic color）**、自适应布局和组件的状态设计讲得最细，每个组件页都同时给设计指引与交互说明。与之配套的官方图标资源 **Material Symbols / Material Icons** 放在 [github.com/google/material-design-icons](https://github.com/google/material-design-icons)，以 **Apache-2.0** 释出——这是少数能放心直接商用的官方图标源。

## 三、可复用的开源设计系统：六套

这一类才是「能直接落进项目」的部分。下表里的代码授权，是写这篇文章时逐条到对应 GitHub 仓库核对的：

| 系统 | 官方入口 | 适合什么产品 | 代码授权 |
| --- | --- | --- | --- |
| IBM Carbon | [carbondesignsystem.com](https://carbondesignsystem.com/) | 企业级后台、数据密集界面 | Apache-2.0 |
| Ant Design | [ant.design](https://ant.design/) | 中后台产品，官方文档提供简体中文版本 | MIT |
| Adobe Spectrum | [spectrum.adobe.com](https://spectrum.adobe.com/) | 创意工具类产品，令牌体系分层细致 | Apache-2.0（React Spectrum） |
| GitHub Primer | [primer.style](https://primer.style/) | 内容与代码平台，变量优先 | MIT（primer/css） |
| Uber Base Web | [baseweb.design](https://baseweb.design/) | 需要高覆盖度组件的产品 | MIT |
| Shopify Polaris | [polaris.shopify.com](https://polaris.shopify.com/) | 电商与商家后台 | 文档在线，React 实现仓库已归档 |

几点使用提醒：

- **表格里给的是代码授权**。设计资源（Figma / Sketch 文件）、品牌图标、内置字体往往另有约定，落地前请以各仓库的 LICENSE 与官方说明为准。
- **Carbon 值得单独看一眼**。它把设计令牌按颜色、字体、间距、动效分层，组件文档里每个状态都配了使用场景，适合当成「后台系统怎么排信息」的模板。
- **Polaris 这一条要留意时间**。它的 React 实现仓库（Shopify/polaris-react-archive）已被官方标注为 Deprecated 并归档，文档站仍在正常维护。接入前先看官方文档给出的当前建议，**不要直接照抄归档仓库里的旧代码**。
- **Base Web 与 Primer 都属于「克制型」**：组件不多，但变量与主题机制清楚，适合想自建一层封装、又不想从零造轮子的团队。

## 四、公共服务场景的两套样板，以及怎么真正用起来

**GOV.UK Design System**（[design-system.service.gov.uk](https://design-system.service.gov.uk/)）和 **U.S. Web Design System**（[designsystem.digital.gov](https://designsystem.digital.gov/)）是另一类样板：服务对象是需要「所有人都能用明白」的公共事务页面，因此把可读性、容错和流程完整度放在很前面的位置。

- GOV.UK 的代码包 `govuk-frontend` 为 **MIT** 授权，它把**文案写作规范**和组件放在同一套系统里，做表单、多步流程与错误提示时参考价值很高。
- USWDS 由美国 GSA 维护，其原创修改部分以 **CC0** 释出；但仓库的 `LICENSE.md` 明确写着「有一部分不属于公有领域」——内含字体适用 SIL OFL 1.1，部分图标适用 Apache-2.0。要用就照 `LICENSE.md` 逐项核对，别只看仓库首页那一个标签。

规范收进收藏夹不难，难的是让它在团队里真正生效。可以试这套顺序：

1. **只选一套作主参照**，不要三套混着抄——最先崩的是间距与圆角。
2. **先偷令牌层**：把颜色、字号、间距、圆角抽成变量，统一变量再谈组件。
3. **把规范里的 Do / Don't 摘成评审问题清单**，每次评审照着问一遍。
4. **拿不准的交互，用两套不同来源的规范交叉验证**；如果两边结论一致，基本可以放心采用。

如果只是想把同类来源一次性收全，站内[「设计规范」分类](https://dh.mozhuai.site/#%E8%AE%BE%E8%AE%A1%E8%A7%84%E8%8C%83)里收录的 alexpate/awesome-design-systems 是一个长期维护的清单仓库，可以顺着它往外翻；想看看各家团队怎么讲自己的设计语言，可以逛[「UED团队」](https://dh.mozhuai.site/#UED%E5%9B%A2%E9%98%9F)。规范之外，图标与素材的选择可以接着看 [[open-source-icon-libraries|6 套开源图标库的规格与授权]]，交稿前的检查项则整理在 [[pre-launch-design-checklist|上线前的设计自检清单]]。
