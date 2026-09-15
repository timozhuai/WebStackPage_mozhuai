# 文章目录（Obsidian 库）使用说明

这个文件夹就是**本站文章板块的全部内容源**，同时也是一个 Obsidian 库。
往这里放一个 `.md` 文件，构建时就会生成一个 `/articles/<slug>` 静态页面，无需改任何代码。

---

## 每日写作流程

1. 打开 Obsidian → 「打开文件夹作为库」→ 选择 `D:\origin\daohang\articles\src`
2. 装好的 **Obsidian Git** 插件会在后台每 10 分钟自动 commit + push（默认已配置好）
3. 写文章 → 保存 → 提交推送 → 文章上线

> 插件已随库预装并配置完毕（`autoSaveInterval = 10`，停止编辑后触发 commit-and-sync）。
> 若插件未生效：设置 → 第三方插件 → 关闭安全模式 → 启用 **Git**。

**提交前会自动构建**：本仓库配置了 git `pre-commit` 钩子，提交时自动运行
`tools/build.py` 重新生成文章页、列表页、RSS 与 sitemap 并加入本次提交，
所以「推送」即「上线」，不需要手动跑构建命令。

手动构建（可选）：

```bash
C:\Users\pyc\.workbuddy\binaries\python\envs\default\Scripts\python.exe tools/build.py
```

---

## 文章格式（复制 `_template.md` 改名即可）

```yaml
---
title: 文章标题（15-30 字，含一个搜索关键词）
description: 150 字以内的摘要（会用作 meta description）
date: 2026-09-15
tags: [设计工具, 素材资源]
keywords: 关键词1,关键词2
slug: english-slug
draft: false        # true 则不发布
---
```

- **文件名建议**：`YYYY-MM-DD-english-slug.md`（日期前缀会被自动去掉，不进入网址）
- **slug** 决定文章地址 `/articles/<slug>`，发布后不要改（改了等于换地址，旧链接失效）
- 正文从 `##` 小节开始写，不要再写 `#` 一级标题

### 会被自动处理的写法

| 写法 | 效果 |
| --- | --- |
| `[[free-commercial-fonts\|字体清单]]` | 站内文章链接（库内其它文章自动识别） |
| `![[图片.png]]` / `![[图片.png\|300]]` | 插入图片，自动拷贝到站点并改写路径 |
| `==高亮==` | 高亮标记 |
| `%%注释%%` | 不发布（构建时删除） |
| `> [!tip] 标题` | callout，渲染为「**技巧**：标题」样式的引用块 |
| `#标签`（正文内） | 按普通文本保留 |

- `_` 开头的文件（如 `_template.md`）与 `README.md` 不参与生成
- 图片直接拖进 Obsidian 会落到 `attachments/`，构建时自动处理
- 每篇建议 **1200 字以上**、2-4 个 `##` 小节，正文至少包含一条站内链接
- 单篇文章解析失败只跳过并告警，**不会**导致整站构建失败

---

## 选题库（写完一篇删一行）

> 定位：设计师网址导航的配套观察笔记，与站内 27 个分类形成内链。

素材与资源清单：

1. 免费商用字体清单（已完成）
2. 免费图标库横向对比
3. 无版权图片站怎么选
4. 免费 Mockup 资源站整理
5. 开源 Figma 插件推荐

工具实测：

6. 在线配色工具怎么用才有效
7. 设计稿交付前必查清单
8. 网页动效工具对比

方法与规范：

9. 设计规范文档怎么写才有人看
10. 移动端适配的常见尺寸坑
11. 作品集怎么组织才不被跳过

灵感与趋势：

12. 界面设计趋势观察
13. 优秀设计站点怎么逛才有收获

---

## 与站点的关系

- 生成物：`articles/<slug>.html`、`articles/index.html`、`articles/rss.xml`、`sitemap.xml`
- 图片资源：构建时拷贝到 `assets/images/articles/`
- 入口：导航页顶栏「设计文章」、首页「设计文章」区块
