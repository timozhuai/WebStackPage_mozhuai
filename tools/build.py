# -*- coding: utf-8 -*-
"""
WebStack 设计师网址导航 - 静态站构建脚本
==========================================

本站部署在 Cloudflare Pages（push master 自动部署），纯静态无服务端。
导航内容与文章全部由本脚本从数据源生成，**不要手改生成的区域**。

目录约定：
  data/sites.json          导航唯一数据源（分类 + 站点 + 侧栏结构）
  articles/src/            文章源 = Obsidian 库（*.md + attachments/）
  cn/index.html, en/index.html   导航页（含 BUILD 标记区，脚本重建标记区内容）
  index.html               首页落地页（分类列表区由脚本重建）
  articles/index.html      文章列表页（脚本生成）
  articles/<slug>.html     文章页（脚本生成）
  articles/rss.xml         订阅源（脚本生成）
  sitemap.xml              站点地图（脚本生成）
  _redirects               Cloudflare 规则，屏蔽源码目录（脚本生成）

加一个网站：编辑 data/sites.json，在对应分类 sites 数组里加一条：
    {"url": "https://example.com/", "logo": "example.png",
     "name": {"cn": "例子", "en": "Example"},
     "desc": {"cn": "一句话介绍。", "en": "One line intro."}}
  logo 图片放到 assets/images/logos/ 下；en 可省略（自动回退中文）。
加一个分类：categories 数组新增一条（id 用中文，如 "AI工具"），并在 sidebar
  对应分组的 children 里加 {"category": "AI工具"}。
写一篇文章：在 Obsidian 里往 articles/src/ 新建 Markdown（或复制 _template.md），
  frontmatter 见 articles/src/README.md；支持 [[双链]]、![[图片]]、==高亮==、
  %%注释%%、> [!tip] callout。draft: true 不发布，_ 开头文件与 README.md 跳过。
  单篇解析失败只跳过并告警，不会让整站构建失败。

然后运行：python tools/build.py && git add -A && git commit -m "..." && git push
（依赖 markdown 库；git pre-commit 钩子已配置为自动执行本脚本，一般无需手动跑）
"""
import html
import json
import os
import re
import shutil
import sys
from urllib.parse import quote

try:
    import markdown as md_lib
except ImportError:
    print('缺少 markdown 库：pip install markdown', file=sys.stderr)
    sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://dh.mozhuai.site'

VAULT_DIR = os.path.join(ROOT, 'articles', 'src')
ARTICLES_DIR = os.path.join(ROOT, 'articles')
ARTICLE_ASSETS_DIR = os.path.join(ROOT, 'assets', 'images', 'articles')
ARTICLE_ASSET_URL = '../assets/images/articles/'

IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.avif', '.bmp'}

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
# 文章系统 —— 源 = Obsidian 库（articles/src）
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r'^---\s*\r?\n(.*?)\r?\n---\s*\r?\n', re.S)
CODE_FENCE_RE = re.compile(r'(`{3,}|~{3,})[\s\S]*?\1')
INLINE_CODE_RE = re.compile(r'`[^`\n]+`')
STASH_RE = re.compile('\x00(\\d+)\x00')

CALLOUT_LABELS = {
    'note': '提示', 'info': '说明', 'tip': '技巧', 'hint': '技巧',
    'success': '推荐', 'check': '完成', 'question': '疑问', 'help': '疑问',
    'warning': '注意', 'caution': '注意', 'attention': '注意',
    'failure': '失败', 'fail': '失败', 'missing': '缺失', 'danger': '警告',
    'error': '错误', 'bug': '问题', 'example': '示例', 'quote': '引用',
    'cite': '引用', 'important': '重要', 'todo': '待办', 'abstract': '摘要',
    'summary': '摘要', 'tldr': '摘要',
}


def unquote(v):
    v = str(v).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'':
        return v[1:-1]
    return v


def parse_frontmatter(text):
    """极简 YAML 子集：标量 / 引号 / 行内 [a, b] / `- ` 块列表。"""
    meta = {}
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if ':' not in line:
            continue
        key, val = line.split(':', 1)
        key, val = key.strip(), val.strip()
        if not key:
            continue
        if val == '':
            items = []
            while i < len(lines) and re.match(r'^\s*-\s+', lines[i]):
                items.append(unquote(re.sub(r'^\s*-\s+', '', lines[i])))
                i += 1
            meta[key] = items
            continue
        meta[key] = unquote(val)
    return meta


def to_date_str(v):
    if not v:
        return None
    m = re.search(r'(\d{4})\s*[-/年.]\s*(\d{1,2})\s*[-/月.]\s*(\d{1,2})', str(v))
    if not m:
        return None
    return '%04d-%02d-%02d' % (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def as_list(v):
    if isinstance(v, list):
        return [unquote(x).strip() for x in v if unquote(x).strip()]
    if not v:
        return []
    raw = unquote(v).strip()
    if raw.startswith('[') and raw.endswith(']'):
        raw = raw[1:-1]
    return [unquote(x).strip() for x in re.split(r'[,，]', raw) if unquote(x).strip()]


def as_bool(v):
    return str(v).strip().lower() in ('true', 'yes', '1', 'on')


def slug_from_filename(filename):
    s = re.sub(r'\.md$', '', filename, flags=re.I)
    s = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', s).strip().lower()
    s = re.sub(r'[^a-z0-9\u4e00-\u9fff-]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s


def plain_text(md):
    s = CODE_FENCE_RE.sub(' ', md)
    s = re.sub(r'!?\[\[[^\]]*\]\]', ' ', s)
    s = re.sub(r'!?\[[^\]]*\]\([^)]*\)', ' ', s)
    s = re.sub(r'[#>*`_|\[\]()!~=+%-]', '', s)
    return re.sub(r'\s+', ' ', s).strip()


class Vault:
    """库内文件索引：用于解析 [[双链]] 与 ![[附件]]。"""

    def __init__(self, root):
        self.root = root
        self.files = {}
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not d.startswith(('.', '_'))]
            for fn in filenames:
                if fn.startswith('.'):
                    continue
                self.files.setdefault(fn.lower(), []).append(os.path.join(dirpath, fn))

    def find(self, name):
        return self.files.get(os.path.basename(name).lower(), [])


def preprocess_obsidian(body, ctx):
    """把 Obsidian 专有语法转成标准 Markdown / 内联 HTML。"""
    stash = []

    def keep(m):
        stash.append(m.group(0))
        return '\x00%d\x00' % (len(stash) - 1)

    s = CODE_FENCE_RE.sub(keep, body)
    s = INLINE_CODE_RE.sub(keep, s)

    s = re.sub(r'%%.*?%%', '', s, flags=re.S)                       # %% 注释 %%
    s = re.sub(r'==(.+?)==', r'<mark>\1</mark>', s)                  # ==高亮==

    def embed(m):
        target = m.group(1).strip()
        alias = (m.group(2) or '').strip()
        hits = ctx['vault'].find(target)
        if not hits:
            return '<span class="art-missing">[缺少附件：%s]</span>' % html.escape(target)
        src = hits[0]
        ext = os.path.splitext(src)[1].lower()
        if ext not in IMAGE_EXT:
            return '[[%s%s]]' % (target, ('|' + alias) if alias else '')
        url = ctx['publish'](src)
        alt = os.path.splitext(os.path.basename(src))[0]
        width = ''
        if alias:
            if re.fullmatch(r'\d+(px)?', alias):
                width = ' width="%s"' % alias.rstrip('px')
            else:
                alt = alias
        return '<img src="%s" alt="%s"%s>' % (url, html.escape(alt), width)

    s = re.sub(r'!\[\[([^\]\|]+)(?:\|([^\]]*))?\]\]', embed, s)

    def wikilink(m):
        target = m.group(1).strip()
        heading = (m.group(2) or '').strip()
        alias = (m.group(3) or '').strip()
        label = alias or heading or target
        art = ctx['resolve'](target)
        if art:
            url = art['rel_url'] + (('#' + quote(heading, safe='')) if heading else '')
            return '[%s](%s)' % (label, url)
        return '<span class="art-nolink">%s</span>' % html.escape(label)

    s = re.sub(r'\[\[([^\]\|#]+)(?:#([^\]\|]+))?(?:\|([^\]]+))?\]\]', wikilink, s)

    def callout(m):
        kind = m.group(2).lower()
        title = m.group(3).strip()
        text = '**%s**' % CALLOUT_LABELS.get(kind, kind)
        if title:
            text += '：%s' % title
        return m.group(1) + text

    # 行内用 [ \t] 而非 \s：\s 会吃掉换行，把无标题 callout 的下一行吞进标题
    s = re.sub(r'^(>[ \t]*)\[!(\w+)\][-+]?[ \t]*(.*?)[ \t]*$', callout, s, flags=re.M)

    return STASH_RE.sub(lambda m: stash[int(m.group(1))], s)


def md_to_html(body):
    return md_lib.markdown(body, extensions=['tables', 'fenced_code', 'nl2br'])


def collect_articles():
    """扫描 Obsidian 库，返回按日期倒序的文章列表；单篇异常只跳过。"""
    vault = Vault(VAULT_DIR)
    if not os.path.isdir(VAULT_DIR):
        print('  ! 文章库不存在：%s' % VAULT_DIR)
        return [], vault

    sources = []
    for dirpath, dirnames, filenames in os.walk(VAULT_DIR):
        dirnames[:] = [d for d in dirnames if not d.startswith(('.', '_'))]
        for fn in filenames:
            if not fn.lower().endswith('.md'):
                continue
            if fn.startswith(('_', '.')) or fn.lower() == 'readme.md':
                continue
            sources.append(os.path.join(dirpath, fn))
    sources.sort()

    if os.path.isdir(ARTICLE_ASSETS_DIR):
        shutil.rmtree(ARTICLE_ASSETS_DIR)
    articles = []
    used_slugs = {}

    for path in sources:
        rel = os.path.relpath(path, VAULT_DIR).replace(os.sep, '/')
        try:
            raw = open(path, encoding='utf-8').read()
            m = FRONTMATTER_RE.match(raw)
            meta = parse_frontmatter(m.group(1)) if m else {}
            body = raw[m.end():] if m else raw

            if as_bool(meta.get('draft', 'false')):
                print('  跳过草稿: %s' % rel)
                continue

            body = re.sub(r'^#\s+(.+)\n+', '', body, count=1)  # 去掉正文首个一级标题

            title = unquote(meta.get('title', '')).strip()
            if not title:
                h1 = re.search(r'^#\s+(.+)$', body, re.M)
                title = h1.group(1).strip() if h1 else ''
            if not title:
                print('  ! 缺少 title，跳过: %s' % rel)
                continue

            date = (to_date_str(meta.get('date'))
                    or to_date_str(os.path.basename(path)[:10])
                    or datetime.date.today().isoformat())
            slug = unquote(meta.get('slug', '')).strip() or slug_from_filename(os.path.basename(path))
            if not slug:
                print('  ! 无法生成 slug，跳过: %s' % rel)
                continue
            if slug in used_slugs:
                print('  ! slug 重复（%s，与 %s 冲突），跳过: %s' % (slug, used_slugs[slug], rel))
                continue
            used_slugs[slug] = rel

            description = unquote(meta.get('description', '')).strip() or plain_text(body)[:150]
            articles.append({
                'slug': slug,
                'title': title,
                'date': date,
                'description': description,
                'tags': as_list(meta.get('tags')),
                'keywords': '，'.join(as_list(meta.get('keywords'))),
                'body': body,
                'rel': rel,
                'rel_url': './' + quote(slug, safe='-'),
                'url_path': '/articles/' + quote(slug, safe='-'),
            })
        except Exception as exc:                       # 单篇失败不影响整站构建
            print('  ! 解析失败，跳过: %s — %s' % (rel, exc))

    articles.sort(key=lambda a: (a['date'], a['slug']), reverse=True)

    # 解析 [[双链]]：按文件名 / slug / 标题匹配
    index = {}
    for a in articles:
        stem = re.sub(r'\.md$', '', os.path.basename(a['rel']), flags=re.I).lower()
        stem_no_date = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', stem)
        for key in (stem, stem_no_date, '%s-%s' % (a['date'], a['slug'].lower()),
                    a['slug'].lower(), a['title'].lower()):
            index.setdefault(key, a)

    def resolve(name):
        return index.get(name.strip().lower())

    published = {}

    def publish(src):
        """把库内附件拷到站点资源目录；同一附件多次引用只拷一份。"""
        key = os.path.abspath(src)
        if key in published:
            return published[key]
        os.makedirs(ARTICLE_ASSETS_DIR, exist_ok=True)
        base = os.path.basename(src)
        dst = os.path.join(ARTICLE_ASSETS_DIR, base)
        n = 1
        while os.path.exists(dst):
            stem, ext = os.path.splitext(base)
            dst = os.path.join(ARTICLE_ASSETS_DIR, '%s-%d%s' % (stem, n, ext))
            n += 1
        shutil.copy2(src, dst)
        published[key] = ARTICLE_ASSET_URL + quote(os.path.basename(dst))
        return published[key]

    ctx = {'vault': vault, 'resolve': resolve, 'publish': publish}
    for a in articles:
        a['html'] = md_to_html(preprocess_obsidian(a['body'], ctx))
    return articles, ctx


def indent_html(source, pad='    '):
    """给生成的 HTML 加统一源码缩进；<pre> 内部保持原样（缩进会显示在代码块里）。"""
    out = []
    in_pre = False
    for line in source.split('\n'):
        if not line or in_pre or '<pre' in line:
            out.append(line)
        else:
            out.append(pad + line)
        if '<pre' in line and '</pre>' not in line:
            in_pre = True
        elif '</pre>' in line:
            in_pre = False
    return '\n'.join(out)


def json_ld(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)


PAGE_HEAD = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{url}">
    <link rel="shortcut icon" href="../assets/images/favicon.png">
    <link rel="stylesheet" href="../assets/css/article.css">'''

PAGE_HEADER = '''<body>
    <header class="art-head">
        <div class="wrap">
            <a class="brand" href="../cn/">设计师网址导航</a>
            <nav class="art-nav">
                <a href="../cn/">导航</a>
                <a href="./" aria-current="page">设计文章</a>
            </nav>
        </div>
    </header>'''

PAGE_FOOTER = '''    <footer class="art-foot">
        <div class="wrap">
            <p>&copy; 2017-2026 <a href="../cn/about"><strong>WebStack</strong></a> &middot; 设计资源观察笔记</p>
        </div>
    </footer>
</body>
</html>
'''


def article_page_html(a):
    url = BASE + a['url_path']
    body = indent_html(a['html'])
    y, m, d = a['date'].split('-')
    date_cn = '%s 年 %s 月 %s 日' % (int(y), int(m), int(d))
    tags = ''.join('            <span class="art-tag">%s</span>\n' % html.escape(t) for t in a['tags'])
    keywords = ('    <meta name="keywords" content="%s">\n' % html.escape(a['keywords'])
                if a['keywords'] else '')
    ld = {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'Article',
                '@id': url + '#article',
                'headline': a['title'],
                'description': a['description'],
                'datePublished': a['date'],
                'dateModified': a['date'],
                'mainEntityOfPage': {'@type': 'WebPage', '@id': url},
                'url': url,
                'inLanguage': 'zh-CN',
                'author': {'@type': 'Organization', 'name': 'WebStack 设计师网址导航', 'url': BASE + '/'},
                'publisher': {'@type': 'Organization', 'name': 'WebStack 设计师网址导航', 'url': BASE + '/'},
            },
            {
                '@type': 'BreadcrumbList',
                'itemListElement': [
                    {'@type': 'ListItem', 'position': 1, 'name': '首页', 'item': BASE + '/'},
                    {'@type': 'ListItem', 'position': 2, 'name': '设计文章', 'item': BASE + '/articles/'},
                    {'@type': 'ListItem', 'position': 3, 'name': a['title'], 'item': url},
                ],
            },
        ],
    }
    head = PAGE_HEAD.format(title=html.escape(a['title']) + ' - 设计师网址导航',
                            desc=html.escape(a['description']), url=url)
    return (head + '\n'
            + '    <meta property="og:type" content="article">\n'
            + '    <meta property="og:url" content="%s">\n' % url
            + '    <meta property="og:title" content="%s">\n' % html.escape(a['title'])
            + '    <meta property="og:description" content="%s">\n' % html.escape(a['description'])
            + '    <meta property="og:site_name" content="WebStack 设计师网址导航">\n'
            + '    <meta property="article:published_time" content="%s">\n' % a['date']
            + keywords
            + '    <script type="application/ld+json">\n    %s\n    </script>\n' % json_ld(ld)
            + '</head>\n' + PAGE_HEADER + '''
    <main class="art-main">
        <article>
            <p class="art-meta"><time datetime="%s">%s</time></p>
            <h1>%s</h1>
            <p class="art-lead">%s</p>
            <div class="art-body">
%s
            </div>
%s        </article>
        <p class="art-back"><a href="./">&larr; 返回文章列表</a> &middot; <a href="../cn/">去逛逛导航 &rarr;</a></p>
    </main>
''' % (a['date'], date_cn, html.escape(a['title']), html.escape(a['description']), body,
       ('            <p class="art-tags">\n' + tags + '            </p>\n') if tags else '')
            + PAGE_FOOTER)


def articles_list_html(articles):
    items = []
    for a in articles:
        y, m, d = a['date'].split('-')
        items.append('            <a class="art-item" href="%s">\n'
                     '                <h2>%s</h2>\n'
                     '                <p>%s</p>\n'
                     '                <p class="art-item-date"><time datetime="%s">%s 年 %s 月 %s 日</time></p>\n'
                     '            </a>'
                     % (a['rel_url'], html.escape(a['title']), html.escape(a['description']),
                        a['date'], int(y), int(m), int(d)))
    list_body = '\n'.join(items) if items else '            <p class="art-empty">第一篇文章即将上线。</p>'
    latest = articles[0]['date'] if articles else ''
    ld_items = ',\n'.join(
        '        {"@type": "ListItem", "position": %d, "url": "%s", "name": %s}'
        % (i + 1, BASE + a['url_path'], json.dumps(a['title'], ensure_ascii=False))
        for i, a in enumerate(articles[:30]))
    head = PAGE_HEAD.format(
        title='设计文章 - 设计工具、素材资源与灵感观察 - 设计师网址导航',
        desc='整理设计工具评测、素材资源清单与灵感趋势的观察笔记，配合站内 240+ 设计站点导航持续更新。',
        url=BASE + '/articles/')
    ld = ('{\n  "@context": "https://schema.org",\n  "@type": "Blog",\n'
          '  "name": "设计文章",\n  "url": "%s/articles/",\n  "inLanguage": "zh-CN",\n'
          '  "publisher": {"@type": "Organization", "name": "WebStack 设计师网址导航", "url": "%s/"},\n'
          '  "blogPost": [\n%s\n  ]\n}' % (BASE, BASE, ld_items))
    return (head + '\n'
            + '    <link rel="alternate" type="application/rss+xml" title="设计文章 RSS" href="./rss.xml">\n'
            + '    <meta property="og:type" content="website">\n'
            + '    <meta property="og:url" content="%s/articles/">\n' % BASE
            + '    <meta property="og:title" content="设计文章 - 设计工具、素材资源与灵感观察">\n'
            + '    <meta property="og:description" content="设计工具评测、素材资源清单与灵感趋势的观察笔记。">\n'
            + '    <meta property="og:site_name" content="WebStack 设计师网址导航">\n'
            + '    <script type="application/ld+json">\n    %s\n    </script>\n' % ld
            + '</head>\n' + PAGE_HEADER + '''
    <main class="art-main art-main-list">
        <h1>设计文章</h1>
        <p class="art-lead">设计工具、素材资源与灵感趋势的观察笔记，配合站内导航持续更新。</p>
        <div class="art-list">
%s
        </div>
        <p class="art-back"><a href="./rss.xml">RSS 订阅</a> &middot; <a href="../cn/">去逛逛导航 &rarr;</a></p>
    </main>
''' % list_body + PAGE_FOOTER)


def articles_rss(articles):
    def esc(s):
        return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                .replace('"', '&quot;').replace("'", '&apos;'))
    items = []
    for a in articles:
        link = BASE + a['url_path']
        items.append('    <item>\n'
                     '      <title>%s</title>\n'
                     '      <link>%s</link>\n'
                     '      <guid isPermaLink="true">%s</guid>\n'
                     '      <pubDate>%s</pubDate>\n'
                     '      <description>%s</description>\n'
                     '    </item>' % (esc(a['title']), esc(link), esc(link),
                                       '%sT08:00:00+08:00' % a['date'], esc(a['description'])))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0">\n  <channel>\n'
            '    <title>%s</title>\n'
            '    <link>%s/articles/</link>\n'
            '    <description>设计工具评测、素材资源清单与灵感趋势的观察笔记。</description>\n'
            '    <language>zh-CN</language>\n'
            '%s\n  </channel>\n</rss>\n' % (esc('设计文章 - WebStack 设计师网址导航'), BASE,
                                            '\n'.join(items)))


# ---------------------------------------------------------------------------
# sitemap 与 _redirects
# ---------------------------------------------------------------------------

def build_sitemap(articles):
    latest = max((a['date'] for a in articles), default=None)
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
        entry(BASE + a['url_path'], a['date'], 'monthly', '0.6')

    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!-- 本文件由 tools/build.py 生成：导航或文章更新后重新运行构建即可。 -->\n'
            '<!-- 注意：本站在托管平台启用净 URL（.html 会被 308 跳转），\n'
            '     因此 sitemap / canonical / hreflang 一律使用无跳转的最终地址。 -->\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n\n'
            + '\n\n'.join(urls) + '\n\n</urlset>\n')


def build_redirects(articles):
    """生成 Cloudflare Pages 规则。

    Cloudflare 的 _redirects 不支持 404 状态码，但重定向优先于静态资源，
    因此用 301 把源码 / 工具 / 数据目录从公网可访问路径上摘掉。
    逐篇的 md -> 文章页规则必须排在通配规则之前（同源规则以最上面的为准）。
    """
    lines = [
        '# 本文件由 tools/build.py 生成，请勿手改。',
        '# 目的：源码、工具与数据目录不对公网提供（Pages 的 _redirects 不支持 404，故用 301）。',
        '',
    ]
    for a in articles:
        lines.append('%-52s %-40s 301' % ('/articles/src/' + quote(a['rel'], safe='/'), a['url_path']))
    lines += [
        '',
        '/articles/src/*                                      /articles/                           301',
        '/tools/*                                             /                                   301',
        '/data/*                                              /                                   301',
        '/README.md                                           /                                   301',
        '/.gitignore                                          /                                   301',
        '',
    ]
    return '\n'.join(lines)


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
    text = re.sub(r'含全部 \d+ 个分类', '含全部 %d 个分类' % n_cats, text)
    open(home_path, 'w', encoding='utf-8', newline='\n').write(text)
    print('built index.html (categories: %d)' % n_cats)

    # ---- 文章（源 = Obsidian 库） ----
    os.makedirs(VAULT_DIR, exist_ok=True)
    articles, _ctx = collect_articles()
    keep = set()
    for a in articles:
        out = os.path.join(ARTICLES_DIR, a['slug'] + '.html')
        with open(out, 'w', encoding='utf-8', newline='\n') as f:
            f.write(article_page_html(a))
        keep.add(os.path.basename(out))
        print('built articles/%s.html  (%s)  %s' % (a['slug'], a['date'], a['title']))
    with open(os.path.join(ARTICLES_DIR, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(articles_list_html(articles))
    print('built articles/index.html (%d articles)' % len(articles))
    with open(os.path.join(ARTICLES_DIR, 'rss.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(articles_rss(articles))
    print('built articles/rss.xml')

    # 清理已删除 / 改名的文章残留页面
    keep.add('index.html')
    for fn in os.listdir(ARTICLES_DIR):
        if fn.endswith('.html') and fn not in keep:
            os.remove(os.path.join(ARTICLES_DIR, fn))
            print('removed stale articles/%s' % fn)

    # ---- sitemap 与 _redirects ----
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(build_sitemap(articles))
    print('built sitemap.xml')
    with open(os.path.join(ROOT, '_redirects'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(build_redirects(articles))
    print('built _redirects')

    print('done.')

if __name__ == '__main__':
    main()
