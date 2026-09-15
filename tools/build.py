# -*- coding: utf-8 -*-
"""
WebStack 设计师网址导航 - 静态站构建脚本
==========================================

本站部署在 Cloudflare Pages（git push master 自动部署），纯静态无服务端。
导航内容与文章全部由本脚本从数据源生成，**不要手改生成的区域**。

目录约定：
  data/sites.json          导航唯一数据源（分类 + 站点 + 侧栏结构）
  articles/src/*.md        文章源（Markdown + frontmatter）
  cn/index.html, en/index.html   导航页（含 BUILD 标记区，脚本重建标记区内容）
  index.html               首页落地页（分类列表区由脚本重建）
  articles/index.html      文章列表页（脚本生成）
  articles/<slug>.html     文章页（脚本生成）
  sitemap.xml              站点地图（脚本生成）

加一个网站：编辑 data/sites.json，在对应分类 sites 数组里加一条：
    {"url": "https://example.com/", "logo": "example.png",
     "name": {"cn": "例子", "en": "Example"},
     "desc": {"cn": "一句话介绍。", "en": "One line intro."}}
  logo 图片放到 assets/images/logos/ 下；en 可省略（自动回退中文）。
加一个分类：categories 数组新增一条（id 用中文，如 "AI工具"），并在 sidebar
  对应分组的 children 里加 {"category": "AI工具"}。
加一篇文章：articles/src/ 下新建 YYYYMMDD-slug.md，文件头 frontmatter：
  ---
  title: 文章标题
  description: 一句话摘要（用于列表页与 SEO description）
  date: 2026-09-15
  ---
  正文为 Markdown。

然后运行：python tools/build.py && git add -A && git commit -m "..." && git push
（python 需已安装 markdown、无其他第三方依赖；bs4 仅抽取数据时用过，本脚本不依赖）
"""
import html
import json
import os
import re
import sys
from urllib.parse import quote

try:
    import markdown as md_lib
except ImportError:
    print('缺少 markdown 库：pip install markdown', file=sys.stderr)
    sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://dh.mozhuai.site'

# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------

def load_sites():
    with open(os.path.join(ROOT, 'data', 'sites.json'), encoding='utf-8') as f:
        return json.load(f)

def site_name(s, lang):
    return (s['name'].get(lang) or s['name']['cn'] or '').strip()

def site_desc(s, lang):
    return (s['desc'].get(lang) or s['desc']['cn'] or '').strip()

def cat_name(c, lang):
    return (c['name'].get(lang) or c['name']['cn'] or '').strip()

def cat_anchor(c, lang):
    a = c['anchor'].get(lang) or c['anchor'].get('cn')
    return a or c['id']

# ---------------------------------------------------------------------------
# 片段渲染
# ---------------------------------------------------------------------------

CARD_T = '''                <div class="col-sm-3">
                    <div class="xe-widget xe-conversations box2 label-info" onclick="window.open('{url}', '_blank')" data-toggle="tooltip" data-placement="bottom" title="" data-original-title="{url}">
                        <div class="xe-comment-entry">
                            <a class="xe-user-img">
                                <img data-src="../assets/images/logos/{logo}" class="lozad img-circle" width="40">
                            </a>
                            <div class="xe-comment">
                                <a href="#" class="xe-user-name overflowClip_1">
                                    <strong>{name}</strong>
                                </a>
                                <p class="overflowClip_2">{desc}</p>
                            </div>
                        </div>
                    </div>
                </div>'''

def render_rows(sites, lang):
    out = []
    for i in range(0, len(sites), 4):
        chunk = sites[i:i + 4]
        cards = '\n'.join(
            CARD_T.format(
                url=html.escape(s['url'], quote=True),
                logo=s['logo'],
                name=html.escape(site_name(s, lang)),
                desc=html.escape(site_desc(s, lang)),
            ) for s in chunk)
        out.append('            <div class="row">\n%s\n            </div>' % cards)
    return '\n'.join(out)

def render_categories(categories, lang):
    out = []
    for c in categories:
        head = ('            <!-- %s -->\n'
                '            <h4 class="text-gray"><i class="linecons-tag" style="margin-right: 7px;" id="%s"></i>%s</h4>'
                % (c['id'], cat_anchor(c, lang), html.escape(cat_name(c, lang))))
        rows = render_rows(c['sites'], lang)
        out.append('%s\n%s\n            <!--END %s -->' % (head, rows, c['id']))
    return '\n'.join(out)

def render_sidebar_link(cat, icon, lang):
    return ('                    <li>\n'
            '                        <a href="#%s" class="smooth">\n'
            '                            <i class="%s"></i>\n'
            '                            <span class="title">%s</span>\n'
            '                        </a>\n'
            '                    </li>'
            % (cat_anchor(cat, lang), icon, html.escape(cat_name(cat, lang))))

def render_sidebar_group(item, cats_by_id, lang):
    lines = [
        '                    <li>',
        '                        <a>',
        '                            <i class="%s"></i>' % item['icon'],
        '                            <span class="title">%s</span>' % html.escape(item['title'][lang]),
        '                        </a>',
        '                        <ul>',
    ]
    for ch in item['children']:
        cat = cats_by_id[ch['category']]
        hot = ('\n                                    <span class="label label-pink pull-right hidden-collapsed">Hot</span>'
               if ch.get('hot') else '')
        lines += [
            '                            <li>',
            '                                <a href="#%s" class="smooth">' % cat_anchor(cat, lang),
            '                                    <span class="title">%s</span>' % html.escape(cat_name(cat, lang)) + hot,
            '                                </a>',
            '                            </li>',
        ]
    lines += ['                        </ul>', '                    </li>']
    return '\n'.join(lines)

def render_sidebar(sidebar, cats_by_id, lang):
    parts = []
    for item in sidebar:
        if item['kind'] == 'link':
            parts.append(render_sidebar_link(cats_by_id[item['category']], item['icon'], lang))
        elif item['kind'] == 'group':
            parts.append(render_sidebar_group(item, cats_by_id, lang))
        elif item['kind'] == 'about' and lang == 'cn':
            parts.append(
                '                    <li>\n'
                '                        <a href="about">\n'
                '                            <i class="linecons-heart"></i>\n'
                '                            <span class="tooltip-blue">关于本站</span>\n'
                '                            <span class="label label-Primary pull-right hidden-collapsed">♥︎</span>\n'
                '                        </a>\n'
                '                    </li>')
    return '\n'.join(parts)

def render_home_catlist(sidebar, cats_by_id):
    """首页落地页的分类索引（排除推广位），锚点指向中文版。"""
    parts = []
    for item in sidebar:
        cats = ([cats_by_id[item['category']]] if item['kind'] == 'link'
                else [cats_by_id[ch['category']] for ch in item.get('children', [])])
        for cat in cats:
            if cat['id'] == '推广':
                continue
            parts.append('                        <li><a href="./cn/#%s">%s</a></li>'
                         % (quote(cat_anchor(cat, 'cn'), safe=''), html.escape(cat_name(cat, 'cn'))))
    return '\n'.join(parts)

# ---------------------------------------------------------------------------
# 标记区替换
# ---------------------------------------------------------------------------

def replace_block(text, begin, end, content):
    """把 begin/end 标记之间的内容替换为 content（content 自带缩进，原样写入）。"""
    m = re.search(re.escape(begin) + r'.*?' + re.escape(end), text, re.S)
    if not m:
        raise SystemExit('标记未找到：%s' % begin)
    lead_start = text.rfind('\n', 0, m.end() - len(end)) + 1
    lead = text[lead_start:m.end() - len(end)]  # end 标记行原有的缩进
    return text[:m.start()] + begin + '\n' + content + '\n' + lead + end + text[m.end():]

# ---------------------------------------------------------------------------
# 文章系统
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.S)

def parse_article(path):
    raw = open(path, encoding='utf-8').read()
    m = FRONTMATTER_RE.match(raw)
    if not m:
        raise SystemExit('文章缺少 frontmatter：%s' % path)
    meta = {}
    for line in m.group(1).split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            meta[k.strip()] = v.strip()
    for key in ('title', 'description', 'date'):
        if key not in meta:
            raise SystemExit('文章 frontmatter 缺少 %s：%s' % (key, path))
    body = raw[m.end():]
    slug = os.path.splitext(os.path.basename(path))[0]
    if not re.fullmatch(r'[a-z0-9-]+', slug):
        raise SystemExit('文章文件名只能包含小写字母/数字/连字符：%s' % path)
    return {'slug': slug, 'meta': meta, 'body': body}

def md_to_html(body):
    return md_lib.markdown(body, extensions=['tables', 'fenced_code', 'nl2br'])

def json_ld(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

def article_page_html(art):
    slug, meta = art['slug'], art['meta']
    url = '%s/articles/%s' % (BASE, slug)
    body = md_to_html(art['body'])
    # Markdown 渲染出的内容整体缩进 4 格，嵌进模板
    body = '\n'.join('    ' + l if l else l for l in body.split('\n'))
    y, m, d = meta['date'].split('-')
    date_cn = '%s 年 %s 月 %s 日' % (int(y), int(m), int(d))
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 设计师网址导航</title>
    <meta name="description" content="{desc}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{url}">
    <link rel="shortcut icon" href="../assets/images/favicon.png">
    <link rel="stylesheet" href="../assets/css/article.css">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:site_name" content="WebStack 设计师网址导航">
    <meta name="twitter:card" content="summary">
    <script type="application/ld+json">
    {ld}
    </script>
</head>
<body>
    <header class="art-head">
        <div class="wrap">
            <a class="brand" href="../cn/">设计师网址导航</a>
            <nav class="art-nav">
                <a href="../cn/">导航</a>
                <a href="./" aria-current="page">文章</a>
            </nav>
        </div>
    </header>
    <main class="art-main">
        <article>
            <p class="art-meta"><time datetime="{date}">{date_cn}</time></p>
            <h1>{title}</h1>
            <p class="art-lead">{desc}</p>
            <div class="art-body">
{body}
            </div>
        </article>
        <p class="art-back"><a href="./">&larr; 返回文章列表</a> &middot; <a href="../cn/">去逛逛导航 &rarr;</a></p>
    </main>
    <footer class="art-foot">
        <div class="wrap">
            <p>&copy; 2017-2026 <a href="../cn/about"><strong>WebStack</strong></a> &middot; 每日更新设计资源观察</p>
        </div>
    </footer>
</body>
</html>
'''.format(title=html.escape(meta['title']), desc=html.escape(meta['description']), url=url,
           date=meta['date'], date_cn=date_cn, body=body,
           ld=json_ld({
               '@context': 'https://schema.org',
               '@type': 'Article',
               'headline': meta['title'],
               'description': meta['description'],
               'datePublished': meta['date'],
               'dateModified': meta['date'],
               'mainEntityOfPage': url,
               'url': url,
               'author': {'@type': 'Organization', 'name': 'WebStack 设计师网址导航', 'url': BASE + '/'},
               'publisher': {'@type': 'Organization', 'name': 'WebStack 设计师网址导航', 'url': BASE + '/'},
               'inLanguage': 'zh-CN',
           }))

def articles_list_html(articles):
    articles = sorted(articles, key=lambda a: a['meta']['date'], reverse=True)
    items = []
    for a in articles:
        y, m, d = a['meta']['date'].split('-')
        items.append(
            '            <a class="art-item" href="./%s">\n'
            '                <h2>%s</h2>\n'
            '                <p>%s</p>\n'
            '                <p class="art-item-date"><time datetime="%s">%s 年 %s 月 %s 日</time></p>\n'
            '            </a>'
            % (a['slug'], html.escape(a['meta']['title']), html.escape(a['meta']['description']),
               a['meta']['date'], int(y), int(m), int(d)))
    list_body = '\n'.join(items) if items else '            <p class="art-empty">第一篇文章即将上线。</p>'
    latest = articles[0]['meta']['date'] if articles else ''
    ld_items = ',\n'.join(
        '        {"@type": "ListItem", "position": %d, "url": "%s/articles/%s", "name": %s}'
        % (i + 1, BASE, a['slug'], json.dumps(a['meta']['title'], ensure_ascii=False))
        for i, a in enumerate(articles[:30]))
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>设计文章 - 每日更新的设计工具与资源观察 - 设计师网址导航</title>
    <meta name="description" content="每日一篇设计工具评测、资源清单与灵感趋势观察，配合站内 240+ 设计站点导航持续更新。">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{base}/articles/">
    <link rel="shortcut icon" href="../assets/images/favicon.png">
    <link rel="stylesheet" href="../assets/css/article.css">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{base}/articles/">
    <meta property="og:title" content="设计文章 - 每日更新的设计工具与资源观察">
    <meta property="og:description" content="每日一篇设计工具评测、资源清单与灵感趋势观察。">
    <meta property="og:site_name" content="WebStack 设计师网址导航">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Blog",
      "name": "设计文章",
      "url": "{base}/articles/",
      "inLanguage": "zh-CN",
      "publisher": {{"@type": "Organization", "name": "WebStack 设计师网址导航", "url": "{base}/"}},
      "blogPost": [
{ld_items}
      ]
    }}
    </script>
</head>
<body>
    <header class="art-head">
        <div class="wrap">
            <a class="brand" href="../cn/">设计师网址导航</a>
            <nav class="art-nav">
                <a href="../cn/">导航</a>
                <a href="./" aria-current="page">文章</a>
            </nav>
        </div>
    </header>
    <main class="art-main art-main-list">
        <h1>设计文章</h1>
        <p class="art-lead">每日一篇：设计工具、素材资源与灵感趋势的观察笔记。</p>
        <div class="art-list">
{list_body}
        </div>
    </main>
    <footer class="art-foot">
        <div class="wrap">
            <p>&copy; 2017-2026 <a href="../cn/about"><strong>WebStack</strong></a> &middot; 每日更新设计资源观察</p>
        </div>
    </footer>
</body>
</html>
'''.format(base=BASE, list_body=list_body, ld_items=ld_items, latest=latest)

# ---------------------------------------------------------------------------
# sitemap
# ---------------------------------------------------------------------------

def build_sitemap(articles):
    latest = max((a['meta']['date'] for a in articles), default=None)
    urls = []

    def entry(loc, lastmod=None, changefreq=None, priority=None, alternates=None):
        s = '  <url>\n    <loc>%s</loc>\n' % loc
        if lastmod:
            s += '    <lastmod>%s</lastmod>\n' % lastmod
        if changefreq:
            s += '    <changefreq>%s</changefreq>\n' % changefreq
        if priority:
            s += '    <priority>%s</priority>\n' % priority
        for hreflang, href in (alternates or []):
            s += '    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>\n' % (hreflang, href)
        s += '  </url>'
        urls.append(s)

    alts_full = [('x-default', BASE + '/'), ('zh-CN', BASE + '/cn/'), ('en', BASE + '/en/')]
    entry(BASE + '/', '2026-09-14', 'daily', '1.0', alts_full)
    entry(BASE + '/cn/', '2026-09-14', 'daily', '0.9', alts_full)
    entry(BASE + '/en/', '2026-09-14', 'daily', '0.8', alts_full)
    entry(BASE + '/cn/about', '2026-09-14', 'monthly', '0.4')
    entry(BASE + '/en/about', '2026-09-14', 'monthly', '0.3')
    entry(BASE + '/articles/', latest, 'daily', '0.7')
    for a in articles:
        entry('%s/articles/%s' % (BASE, a['slug']), a['meta']['date'], 'monthly', '0.6')

    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!-- 本文件由 tools/build.py 生成：导航或文章更新后重新运行构建即可。 -->\n'
            '<!-- 注意：本站在托管平台启用净 URL（.html 会被 308 跳转），\n'
            '     因此 sitemap / canonical / hreflang 一律使用无跳转的最终地址。 -->\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n\n'
            + '\n\n'.join(urls) + '\n\n</urlset>\n')

# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    data = load_sites()
    categories = data['categories']
    sidebar = data['sidebar']
    cats_by_id = {c['id']: c for c in categories}

    # 校验 sidebar 引用
    for it in sidebar:
        refs = [it['category']] if it['kind'] == 'link' else [ch['category'] for ch in it.get('children', [])]
        for r in refs:
            if r not in cats_by_id:
                raise SystemExit('sidebar 引用了不存在的分类：%s' % r)

    # ---- 导航页 cn / en ----
    for lang, rel in (('cn', os.path.join('cn', 'index.html')), ('en', os.path.join('en', 'index.html'))):
        path = os.path.join(ROOT, rel)
        text = open(path, encoding='utf-8').read()
        text = replace_block(text, '<!-- BUILD:SIDEBAR:BEGIN -->', '<!-- BUILD:SIDEBAR:END -->',
                             render_sidebar(sidebar, cats_by_id, lang))
        text = replace_block(text, '<!-- BUILD:CATEGORIES:BEGIN -->', '<!-- BUILD:CATEGORIES:END -->',
                             render_categories(categories, lang))
        open(path, 'w', encoding='utf-8', newline='\n').write(text)
        print('built %s' % rel)

    # ---- 首页分类索引与数量 ----
    home_path = os.path.join(ROOT, 'index.html')
    text = open(home_path, encoding='utf-8').read()
    n_cats = len([c for c in categories if c['id'] != '推广'])
    text = replace_block(text, '<!-- BUILD:CATLIST:BEGIN -->', '<!-- BUILD:CATLIST:END -->',
                         render_home_catlist(sidebar, cats_by_id))
    text = re.sub(r'目前收录 \d+ 个分类', '目前收录 %d 个分类' % n_cats, text)
    open(home_path, 'w', encoding='utf-8', newline='\n').write(text)
    print('built index.html (categories: %d)' % n_cats)

    # ---- 文章 ----
    src_dir = os.path.join(ROOT, 'articles', 'src')
    out_dir = os.path.join(ROOT, 'articles')
    os.makedirs(src_dir, exist_ok=True)
    articles = []
    for fn in sorted(os.listdir(src_dir)):
        if fn.endswith('.md'):
            articles.append(parse_article(os.path.join(src_dir, fn)))
    for a in articles:
        with open(os.path.join(out_dir, a['slug'] + '.html'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(article_page_html(a))
        print('built articles/%s.html' % a['slug'])
    with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(articles_list_html(articles))
    print('built articles/index.html (%d articles)' % len(articles))

    # ---- sitemap ----
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(build_sitemap(articles))
    print('built sitemap.xml')

    print('done.')

if __name__ == '__main__':
    main()
