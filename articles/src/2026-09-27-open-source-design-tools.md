---
title: 设计工具的开源替代：8 个项目的实际定位、授权与自托管
description: 从白板协作到界面设计、矢量绘图、字体与图标分发，8 个开源项目各自能接住哪个环节，授权和自托管要注意什么，一次讲清。
date: 2026-09-27
tags: [开源工具, 效率工具]
keywords: 开源设计工具,Penpot,Excalidraw,diagrams.net,Inkscape,Krita,Fontsource,Iconify,自托管
---

订阅制设计工具用久了会有一种错觉：好像离开它，整个流程就转不动。实际上在每个环节里都至少有开源项目可以接住——只是它们很少被拿来做正面比较。

先说清一件事：**开源替代品不是"功能一样但免费"**，它的真实优势是另外三条——文件格式开放（数据是自己的）、能离线或自托管（不受服务条款变动影响）、授权明确（交付时不用回头查能不能商用）。真正的短板通常是协作生态、团队资产管理和与上下游格式的无损对接。

这篇挑 8 个项目，按环节讲清它们各自适合站在哪里。

## 一、白板与流程图：最容易被开源接住的一块

这类工具的需求本质是"画得快、改得快、别人打得开"，对功能深度要求不高，所以替换成本最低。

- **Excalidraw**（[excalidraw.com](https://excalidraw.com)，源码在 [github.com/excalidraw/excalidraw](https://github.com/excalidraw/excalidraw)，MIT）：手绘风格白板。打开就能画，不用注册；导出支持 PNG、SVG，也支持保留源文件 `.excalidraw`（JSON），以后还能继续改。它还有一个很实用的特性：官方提供 npm 包，可以把画布嵌进自己的后台页面里。
- **diagrams.net / draw.io**（[app.diagrams.net](https://app.diagrams.net)，官网 [drawio.com](https://www.drawio.com)，源码在 [github.com/jgraph/drawio](https://github.com/jgraph/drawio)，Apache-2.0）：流程图、架构图、UML 的主力工具。它最大的好处是**存储位置由你选**——本地文件、Google Drive、OneDrive、GitHub 都行，不强制上传到某个专有云。另外有桌面版和 VS Code 插件，画架构图时不用切浏览器。
- **tldraw**（[tldraw.dev](https://tldraw.dev)）：无限画布 SDK，适合把"可嵌入的协作画布"做进产品。要特别提醒的是，它用的是**自定义授权协议**（名为 tldraw license），不是 MIT 这类标准开源协议，商用前务必先读官方授权页，别按"开源=随便用"来理解。

选型上一句话：个人和各处救急用 Excalidraw，要长期维护、需要复杂连线的图用 diagrams.net，要在自己产品里嵌画布再看 tldraw。

## 二、界面设计与原型：Penpot 是唯一值得认真评估的

界面设计这一环一直是开源最难啃的骨头，因为协作、组件库、标注交付都绑得很深。

- **Penpot**（[penpot.app](https://penpot.app)，源码在 [github.com/penpot/penpot](https://github.com/penpot/penpot)，MPL-2.0）：浏览器里的界面设计与原型工具，设计稿和原型在同一个文件里维护，不用在两个工具间同步。自托管部署文档在 [help.penpot.app](https://help.penpot.app/)，官方提供 Docker 方式，这点对内部资料不能出网的团队很关键。

需要注意两点：一是**它开源的是软件本身，官方提供的托管服务属于商业产品**，云版与自托管版在部分功能上的差异请以官方说明为准；二是从 Figma 迁过来时，字体、组件变体、原型连线这些最贵的东西往往需要人工重建，先拿一个真实项目试，别拿设计系统当试验品。

## 三、矢量、位图与三维：功能不缺，缺的是工程对接

桌面端开源工具的历史比大多数人想的长，短板不在"能不能画"，而在"能不能接住别人的文件"。

- **Inkscape**（[inkscape.org](https://inkscape.org)，GPL）：SVG 原生编辑器。节点编辑、路径布尔运算、文本沿路径、位图描摹这些基础功能够用，最适合做图标、标识、矢量插画，以及把设计师给的效果图重绘成可以在代码里维护的 SVG。
- **Krita**（[krita.org](https://krita.org)，GPL-3.0）：面向数字绘画，笔刷引擎和绘画手感是它的主场，还带动画帧与漫画分镜功能，插画、概念图这类工作流最合适。
- **GIMP**（[gimp.org](https://www.gimp.org)，GPL）：位图修图与合成，插件生态成熟，适合做批量的图片处理。
- **Blender**（[blender.org](https://www.blender.org)，GPL）：建模、渲染、动画一体，站内[「图形创意」分类](https://dh.mozhuai.site/#%E5%9B%BE%E5%BD%A2%E5%88%9B%E6%84%8F)里也收了它，做 3D 视觉稿时基本没有对手。

这类工具最需要提前想清楚的是**往返编辑**：`.psd`、`.ai` 这类分层专有格式的互导会有真实损耗，同一份稿子反复在两个软件之间来回改，几乎必然出问题。稳妥做法是把它们用在"链路末端"——上游定稿、下游产出，而不是两边交替改。

关于 GPL 还有个常见误解值得澄清：**GPL 约束的是软件本身的复制与再分发，不改变你用软件产出的作品著作权**。你画的图、导出的 SVG，版权归属和授权方式仍由你自己决定。当然，涉及具体项目时还是要按官方许可说明判断，这里只能给出方向。

## 四、字体与图标：把分发环节握在自己手里

这两类"基础设施"平时不起眼，但一旦依赖外部 CDN，就成了性能和隐私上的隐形变量。

- **Fontsource**（[fontsource.org](https://fontsource.org)，源码在 [github.com/fontsource/fontsource](https://github.com/fontsource/fontsource)，MIT）：把开源字体打包成 npm 包，用 `@fontsource/` 前缀直接安装，字体文件随项目一起走，不必再调外部字体服务。适合需要严格控制首屏加载和隐私合规的站点。要提醒的是，**它只是分发渠道，字体本身的授权仍然跟着那款字体走**，装之前看一眼字体自带的授权文件。
- **Iconify**（[iconify.design](https://iconify.design)，源码在 [github.com/iconify/iconify](https://github.com/iconify/iconify)，MIT）：用一套接口统一取用多套开源图标集，避免项目里为了几个图标挂三四个不同的 CDN。同样的要留意：**图标集的授权各自独立**，Iconify 作为聚合层不代表所有图标都能随便商用，取用前要回到该图标集自己的授权页确认。
- **FontForge**（[fontforge.org](https://fontforge.org)，GPL）：字体编辑器，用来改字形、做字体子集化、修 hinting。做中文字体子集化时它依然是最省事的开源选择之一，和站内[「字体资源」分类](https://dh.mozhuai.site/#%E5%AD%97%E4%BD%93%E8%B5%84%E6%BA%90)里那些字库站搭配用刚好。

| 环节 | 首选项目 | 授权 | 需要提前确认的事 |
| --- | --- | --- | --- |
| 白板、讨论用草图 | Excalidraw | MIT | 团队是否需要统一的自托管入口 |
| 流程图、架构图 | diagrams.net | Apache-2.0 | 存储位置与访问权限 |
| 嵌入产品的协作画布 | tldraw | 自定义协议 | 商用条款 |
| 界面设计与原型 | Penpot | MPL-2.0 | 迁移成本、自托管运维 |
| 矢量图形、图标 | Inkscape | GPL | 与 `.ai` 的往返损耗 |
| 插画、概念图 | Krita | GPL-3.0 | 是否要交付可编辑分层文件 |
| 位图修图 | GIMP | GPL | 批量处理脚本的迁移 |
| 字体与图标分发 | Fontsource / Iconify | MIT | 字体与图标集自身的授权 |

> [!tip] 换工具的正确顺序
> 不要一次性全换。先挑一个**不影响交付物的环节**替换，比如把讨论用的白板换成 Excalidraw、把字体分发换成 Fontsource——这两个环节换了没人会察觉，但能立刻减少对外部服务的依赖。等团队习惯了这种"数据在自己手里"的模式，再考虑动界面设计这种核心环节。授权细节务必以各项目官方页面和字体、图标集自带的许可文件为准，这篇只做方向性梳理。

最后回到使用习惯上：这些项目大多不需要你放弃现有工具，更现实的做法是把它们放在流程的特定位置——**讨论、内部分享、离线环境、以及需要长期可维护的交付物**。如果还没找到固定入口，站内的[「在线工具」](https://dh.mozhuai.site/#%E5%9C%A8%E7%BA%BF%E5%B7%A5%E5%85%B7)和[「图标素材」](https://dh.mozhuai.site/#%E5%9B%BE%E6%A0%87%E7%B4%A0%E6%9D%90)两个分类里已经收了一批同类站点，和之前写过的 [[open-source-icon-libraries|开源图标库清单]]、[[free-commercial-fonts|免费商用字体清单]] 一起用，基本能覆盖从选题到交付的素材需求。
