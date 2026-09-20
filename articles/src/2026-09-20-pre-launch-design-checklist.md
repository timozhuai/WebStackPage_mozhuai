---
title: 上线前的设计自检：6 个工具 + 一份 30 分钟清单
description: 交稿前哪些问题机器能替你查？Lighthouse、axe DevTools、WAVE、Squoosh、SVGOMG 等工具，加上 Baseline 特性查询，组成一套 30 分钟就能跑完的上线自检流程。
date: 2026-09-20
tags: [设计工具, 工作流]
keywords: 上线前检查,可访问性检测,Lighthouse,axe DevTools,WAVE,对比度检查,Baseline
draft: false
---

设计稿通过、页面写完，最后一步常常是「凭感觉点一遍」：点点按钮、看看有没有错位，然后就交付了。出问题的地方恰恰不在眼睛能看到的部分——某个灰字对比度差了那么一点，某张图漏了替代文本，首屏图片有 2MB。这些都不是审美问题，而是**可以用规则判定的问题**，也就意味着可以交给工具。

下面这套流程大约 30 分钟能跑完，涉及 6 个可以直接上手的工具，外加 3 个查询入口，全部给出官方地址、全部免费可用。

## 先分清：哪些事该交给机器

人眼能判断「好不好看」，判断不了「够不够标准」。适合自动化的部分大致是四类：

- **结构与语义**：图片缺少替代文本、按钮没有可读名称、标题层级跳跃；
- **对比度**：文字与界面组件是否达到 WCAG 规定的阈值；
- **资源体积**：首屏图片、SVG 图标是否超出合理范围；
- **特性兼容**：用到的 CSS 属性在目标浏览器里到底能不能用。

但工具的结论不能替代人的判断。MDN 关于 Baseline 的术语页里有一句写得很直白：Baseline 只是浏览器支持的摘要，**不能替代可访问性、可用性、性能和安全等其他测试**。把它当成「过滤器」而不是「验收员」，心态就对了。

## 可访问性与结构：三个工具分工跑

- **Lighthouse**（[developer.chrome.com/docs/lighthouse](https://developer.chrome.com/docs/lighthouse/overview)）：Google 维护的开源审计工具，采用 **Apache-2.0** 授权，已内置在 Chrome DevTools 的 Lighthouse 面板中，同时提供 Node CLI 与 Node 模块，便于接进自动化流程。跑一次会得到一份分类报告，适合当作总览，先看出问题集中在哪一块。
- **axe DevTools**（[deque.com/axe/devtools](https://www.deque.com/axe/devtools/)）：Deque 出品的可访问性检测工具，核心引擎 **axe-core 是开源的（MPL-2.0）**，可以直接嵌入自动化测试。浏览器扩展会逐条指出问题元素并给出修复方向。按官网页面列出的数据，axe-core 累计下载量超过 50 亿次、Chrome 扩展安装量超过 80 万，官方给自己的定位是「零误报」。付费档与试用政策以官网说明为准。
- **WAVE**（[wave.webaim.org](https://wave.webaim.org/)）：WebAIM 的老牌检测工具，输入网址即可在线出结果，另有 Chrome、Firefox、Edge 扩展。官方特别说明扩展适合检查**需要登录、存放在本地或高度动态的页面**——而这几种恰恰是在线版查不到的。

这三者不是三选一：Lighthouse 看全局，axe 与 WAVE 用来定位具体元素，拿不准的地方再回到浏览器里手动确认。

## 对比度：把三个数字记牢

对比度最容易被「感觉」掩盖。WebAIM 的对比度检查器页面上写着官方阈值，值得直接记住：

- WCAG 2.0 **AA**：正文至少 **4.5:1**，大号文字至少 **3:1**
- WCAG 2.1 补充：**图形与界面组件**（例如表单输入框边框）至少 **3:1**
- WCAG **AAA**：正文至少 **7:1**，大号文字至少 **4.5:1**

这里的「大号文字」有明确定义：**14pt（约 18.66px）加粗及以上，或者 18pt（约 24px）及以上**。也就是说，一个 20px 的非加粗标题，并不享受 3:1 的宽松标准。

工具方面，[WebAIM 对比度检查器](https://webaim.org/resources/contrastchecker/)除网页版外，还提供书签小工具（bookmarklet）与取色器，可以在任意页面上吸色检查；在结果的链接后追加 `&api` 还能直接拿到 JSON 数据。WAVE 则能一次分析整页所有文字的对比度，适合批量过一遍。另外记住一点：**AA 是底线而不是目标**，正文尽量留出余量，深色模式要单独再算一次。

## 体积与兼容：补充入口与 30 分钟顺序

**图片体积**：[Squoosh](https://squoosh.app/) 是 Chrome 团队开源的图片压缩 Web 应用（Apache-2.0），官方 README 明确说明**压缩全部在浏览器本地完成，图片不会被上传到服务器**（仅采集基础访问数据）。需要在格式之间做取舍时它最好用。[TinyPNG](https://tinypng.com/) 胜在省事，官方 FAQ 的说法是体积最多可减少约 80%，批量处理与 API 属于付费档，额度以官网为准。

**SVG 体积**：[SVGOMG](https://jakearchibald.github.io/svgomg/) 是 SVGO（**MIT** 授权）的图形界面，把压缩选项做成一个个开关；导出前记得核对 `viewBox` 有没有被改坏。图标来源一多，这一步能省下可观的体积，[[open-source-icon-libraries|6 套开源图标库]]那篇里也提到过同类问题。

**特性兼容**：[Baseline](https://developer.mozilla.org/en-US/docs/Glossary/Baseline/Compatibility) 用两个词回答「这个特性现在能不能用」——**widely available** 表示在所有主流浏览器中已有至少 **2.5 年**的稳定支持历史，**newly available** 表示只在各浏览器最新稳定版里可用。它覆盖的浏览器是 Safari（iOS/macOS）、Chrome（Android/桌面）、Edge（桌面）与 Firefox（Android/桌面）。需要查具体版本时，[Can I Use](https://caniuse.com/) 的 HTML / CSS 特性支持表更细。

最后，把这套流程固定成顺序，30 分钟内可以跑完：

1. 在 Chrome DevTools 里跑一次 Lighthouse，先判断问题集中在哪一类；
2. 用 axe DevTools 或 WAVE 逐条处理结构与语义问题；
3. 把浅色与深色两套配色各过一遍对比度检查；
4. 走一遍图片与 SVG 压缩，记录压缩前后的体积差异；
5. 用 Baseline / Can I Use 确认关键特性在目标浏览器中可用；
6. 剩下的问题写进清单，标注「机器判定」还是「需要人判断」，再分工。

---

导航站的[「在线工具」分类](https://dh.mozhuai.site/#%E5%9C%A8%E7%BA%BF%E5%B7%A5%E5%85%B7)里已经收录了 SVGOMG 与 TinyPNG，[「Chrome插件」分类](https://dh.mozhuai.site/#Chrome%E6%8F%92%E4%BB%B6)能找到一批顺手的浏览器检查插件，标准与规范相关的内容则在[「设计规范」](https://dh.mozhuai.site/#%E8%AE%BE%E8%AE%A1%E8%A7%84%E8%8C%83)分类里。如果这一轮自检卡在素材上，可以接着看 [[free-stock-photos|免费商用图库怎么选]]。
