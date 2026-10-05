---
title: 设计师的 Chrome 插件清单：7 个官网都核实过的日常提效工具
description: 浏览器是设计师待得最久的工作环境之一。这篇整理了取色、字体识别、样式检查、页面编辑、截图与多屏预览共 7 个 Chrome 插件，官网逐一核实过，并附安装与权限注意事项。
date: 2026-10-05
tags: [Chrome插件, 效率工具, 设计师工作流]
keywords: Chrome插件, 设计师工具, 取色, 字体识别, 截图工具, 响应式预览, VisBug, ColorZilla
---

做设计的人，一天里待得最久的软件多半不是设计工具，而是浏览器：看参考、查规范、对还原度、截图沟通，全在这里发生。与其反复切换工具，不如把浏览器本身武装起来。这篇整理了 7 个我逐一核实过官网的 Chrome 插件，按"看样式—改页面—留证据"三个环节分组，你可以对照自己的工作流挑着装。

## 看样式：取色与字体识别

这类插件解决的是"这个颜色/字体是什么"的瞬间问题，用得最频繁。

- **ColorZilla**（[colorzilla.com](https://colorzilla.com)）：老牌取色器。吸管取页面任意像素的颜色、自动记录取色历史、页面配色分析，还有渐变生成器。做视觉走查或者从参考站"借"一组色值时，它比截图后再开取色工具快得多。
- **WhatFont**（[chengyinliu.com/whatfont.html](https://chengyinliu.com/whatfont.html)）：开启后悬停在任意文字上，直接显示字体家族、字号、字重和颜色，点击可展开完整字体栈。识别参考站字体时，它省去了开 DevTools 翻 Computed 面板的步骤。
- **Fonts Ninja**（[fonts.ninja](https://fonts.ninja)）：同样是悬停识别字体，但多了书签和字体信息管理，适合把识别结果攒起来做选型对比。
- **CSS Peeper**（[csspeeper.com](https://csspeeper.com)）：面向设计师的样式检查器。不开 DevTools 也能看到元素的尺寸、字体、阴影，还能把整页用到的颜色和图片素材一键拉出来，做规范梳理时特别顺手。

这四个里，ColorZilla 和 WhatFont 几乎是"装完就忘、用时不觉"的类型——它们没有存在感，但缺了会立刻觉得慢。

## 直接在页面上改：VisBug

只"看"还不够。评审页面时经常想"这个标题小两号会不会更好"，以前要么截图标注，要么丢回设计软件改一版，**VisBug**（[github.com/GoogleChromeLabs/ProjectVisBug](https://github.com/GoogleChromeLabs/ProjectVisBug)）把这一步缩短到几秒钟。

它是 Google Chrome Labs 出品的开源项目（Apache 2.0 协议），自称"设计师的 FireBug"：像在 Sketch/Figma 里那样直接拖拽移动元素、改文字、替换图片、调间距和颜色，还能检查对齐与可访问性信息。修改只发生在你本地的 DOM 上，刷新即还原，不会影响线上页面。除了 Chrome，它也提供了 Firefox、Safari、Edge 的安装入口，快捷键在项目的 Wiki 里有完整列表。

另一个小工具顺带一提：**Pesticide**（[github.com/mrmrs/pesticide](https://github.com/mrmrs/pesticide)，MIT 协议）给页面上所有元素加上彩色描边，排查布局错位时一眼就能看出是哪个容器的问题。本质上它只是一段 CSS，项目本身已多年未更新，如果介意，直接把它的样式文件在本地调试时引入即可，不必装扩展。

## 留证据：截图与多屏预览

- **Awesome Screenshot**（[awesomescreenshot.com](https://awesomescreenshot.com)）：截可视区域或整页长图，然后直接在图上标注箭头、文字和打码，录屏功能也集成在内。评审反馈、bug 单里贴图，一个插件够了。
- **Responsive Viewer**（[responsiveviewer.org](https://responsiveviewer.org)）：在同一个窗口里并排显示多个设备尺寸下的页面，做响应式走查时不用来回拖浏览器窗口。对需要同时交付桌面端和移动端的设计师来说，这是省时间最明显的一个。

## 装插件的两条原则

第一，**只从官方渠道装**。上面这些插件都能在 Chrome 网上应用店搜到，认准开发者名称与官网一致再装；同名的仿冒插件是浏览器最常见的坑。第二，**留意权限**。这类工具大多需要"读取和更改您访问的网站上的数据"权限——这是功能所必需的，但意味着插件能接触你浏览的页面内容。装之前看一眼申请的权限是否与功能匹配，不用的时候可以在扩展面板里临时关掉。

如果还想按需扩充工具箱，本站的[「Chrome插件」分类](https://dh.mozhuai.site/#Chrome%E6%8F%92%E4%BB%B6)里收录了一批同类插件，[「在线工具」分类](https://dh.mozhuai.site/#%E5%9C%A8%E7%BA%BF%E5%B7%A5%E5%85%B7)里也有不少不用安装的网页版工具，可以和插件互为补充。

插件的意义不在于多，而在于把高频动作的摩擦降为零。先从取色和截图这两件最常见的事装起，用顺了再考虑下一步。
