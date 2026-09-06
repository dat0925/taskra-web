# -*- coding: utf-8 -*-
"""
Taskra 使い方ガイドの静的ページ生成スクリプト
------------------------------------------------------------------
ページの枠（ヘッダー・目次ナビ・パンくず・フッター・構造化データ）は
全ページで同じなので、ここで一括生成する。
ナビに1行足すだけで15ページ全部に反映されるのが、手書きしない理由。

  実行:  python _build/build_guide.py
  出力:  guide/<slug>.html  と  guide/index.html
"""
import io
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'guide')
SITE = 'https://taskra.jp'

# ---------------------------------------------------------------- 目次ナビ
# (グループ見出し, [(slug, 英語名, 日本語の一言)])
NAV = [
    ('まず押さえる', [
        ('dashboard', 'Dashboard', '今日の全体像'),
        ('inbox',     'Inbox',     '未整理の受信箱'),
        ('next',      'Next',      '各PJの次の1手'),
    ]),
    ('期限とスケジュール', [
        ('today',     'Today',     '今日やること'),
        ('overdue',   'Overdue',   '期限切れ'),
        ('forecast',  'Forecast',  '2週間の見通し'),
        ('gantt',     'Gantt',     'ガントチャート'),
    ]),
    ('絞り込んで見る', [
        ('flagged',   'Flagged',   '重要マーク'),
        ('assigned',  'Assigned',  '自分の担当'),
        ('project',   'プロジェクト', '案件ごとの一覧'),
        ('tag',       'タグ',       '横断ラベル'),
    ]),
    ('振り返る・探す', [
        ('review',    'Review',    '週次の棚卸し'),
        ('logbook',   'Logbook',   '完了の履歴'),
        ('search',    'Search',    '横断検索'),
        ('note',      'Note',      '自由なメモ'),
    ]),
]

# 関連ビューのカードに出す短い説明（slug -> (見出し, 説明)）
REGISTRY = {
    'dashboard': ('Dashboard', '期限切れ・今日・自分の担当・通知を1画面に集めた要約。'),
    'inbox':     ('Inbox', 'プロジェクトをまだ決めていないタスクの置き場。'),
    'next':      ('Next', '各プロジェクトの「次の1件」だけを抜き出した一覧。'),
    'today':     ('Today', '期限が今日のタスクと、フラグを付けたタスク。'),
    'overdue':   ('Overdue', '期限を過ぎてしまったタスクだけの一覧。'),
    'forecast':  ('Forecast', '今日から2週間分を日別のカレンダーで表示。'),
    'gantt':     ('Gantt', 'プロジェクトの期間を横棒で可視化。'),
    'flagged':   ('Flagged', '重要マーク（フラグ）を付けたタスクの一覧。'),
    'assigned':  ('Assigned', 'チームの中で自分が担当になっているタスク。'),
    'project':   ('プロジェクト', '案件ごとのタスク一覧。並び順が Next を決めます。'),
    'tag':       ('タグ', 'プロジェクトをまたぐ切り口でまとめて表示。'),
    'review':    ('Review', '期限切れ・停滞・レビュー時期をまとめて点検。'),
    'logbook':   ('Logbook', '完了したタスクの履歴と、取り消し。'),
    'search':    ('Search', 'タスクとノートをキーワードで横断検索。'),
    'note':      ('Note', 'タスクに紐づかない自由なメモ。'),
}


def nav_html(current):
    """左の目次。current のページだけ強調する。"""
    h = ['    <h2>使い方ガイド</h2>', '    <ul>']
    cls = ' class="is-current"' if current == 'index' else ''
    h.append('      <li><a href="/guide/"%s><span class="nav-en">目次</span>'
             '<span class="nav-ja">ガイドのトップ</span></a></li>' % cls)
    h.append('    </ul>')
    for group, items in NAV:
        h.append('    <h2>%s</h2>' % group)
        h.append('    <ul>')
        for slug, en, ja in items:
            cls = ' class="is-current"' if slug == current else ''
            h.append('      <li><a href="/guide/%s.html"%s><span class="nav-en">%s</span>'
                     '<span class="nav-ja">%s</span></a></li>' % (slug, cls, en, ja))
        h.append('    </ul>')
    return '\n'.join(h)


HEADER = '''<header>
  <div class="header-inner">
    <a href="/" class="logo">
      <img src="/icon.png" class="logo-img" alt="Taskra">
      Taskra
    </a>
    <nav>
      <a href="/#features">機能</a>
      <a href="/#pricing">料金</a>
      <a href="/#faq">FAQ</a>
      <a href="/guide/" class="is-current">使い方ガイド</a>
    </nav>
    <div class="header-cta">
      <a class="btn btn-primary" href="https://app.taskra.jp" target="_blank" rel="noopener">アプリを開く</a>
    </div>
  </div>
</header>'''

FOOTER = '''<footer>
  <div class="footer-inner">
    <div class="footer-bottom" style="border-top:none;padding-top:0;">
      <p>© 2025 Taskra. All rights reserved.</p>
      <div class="footer-bottom-links">
        <a href="/guide/">使い方ガイド</a>
        <a href="/terms.html">利用規約</a>
        <a href="/privacy.html">プライバシーポリシー</a>
        <a href="/tokushoho.html">特定商取引法</a>
      </div>
    </div>
  </div>
</footer>'''


def ld(obj):
    return ('<script type="application/ld+json">\n%s\n</script>'
            % json.dumps(obj, ensure_ascii=False, indent=2))


def breadcrumb_ld(page_name, url):
    items = [
        {"@type": "ListItem", "position": 1, "name": "Taskra", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "使い方ガイド", "item": SITE + "/guide/"},
    ]
    if page_name:
        items.append({"@type": "ListItem", "position": 3, "name": page_name, "item": url})
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList",
               "itemListElement": items})


def faq_ld(faq):
    return ld({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a_plain}}
            for q, _a_html, a_plain in faq
        ]})


def howto_ld(name, desc, steps):
    return ld({
        "@context": "https://schema.org", "@type": "HowTo",
        "name": name, "description": desc,
        "step": [{"@type": "HowToStep", "name": n, "text": t} for n, t in steps]})


def render_page(p):
    slug = p['slug']
    url = '%s/guide/%s.html' % (SITE, slug)
    og_img = SITE + p.get('og_img', '/guide/img/%s.jpg' % slug)

    parts = []
    parts.append('<!DOCTYPE html>\n<html lang="ja">\n<head>')
    parts.append('<meta charset="UTF-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    parts.append('<title>%s | Taskra 使い方ガイド</title>' % p['title'])
    parts.append('<meta name="description" content="%s">' % p['desc'])
    parts.append('<link rel="canonical" href="%s">' % url)
    parts.append('<meta property="og:title" content="%s">' % p['title'])
    parts.append('<meta property="og:description" content="%s">' % p['og_desc'])
    parts.append('<meta property="og:type" content="article">')
    parts.append('<meta property="og:url" content="%s">' % url)
    parts.append('<meta property="og:image" content="%s">' % og_img)
    parts.append('<meta name="twitter:card" content="summary_large_image">')
    parts.append('<meta name="twitter:image" content="%s">' % og_img)
    parts.append('<link rel="icon" href="/icon.png">')
    parts.append('<link rel="stylesheet" href="/css/style.css">')
    parts.append('<link rel="stylesheet" href="/guide/guide.css">')
    parts.append(breadcrumb_ld(p['crumb'], url))
    if p.get('howto'):
        parts.append(howto_ld(p['howto_name'], p['howto_desc'], p['howto']))
    if p.get('faq'):
        parts.append(faq_ld(p['faq']))
    parts.append('</head>\n<body>\n')
    parts.append(HEADER)
    parts.append('\n<div class="guide-wrap">\n')
    parts.append('  <aside class="guide-nav">')
    parts.append(nav_html(slug))
    parts.append('  </aside>\n')
    parts.append('  <main class="guide-main">\n')

    parts.append('    <nav class="breadcrumb" aria-label="パンくず">')
    parts.append('      <a href="/">Taskra</a>')
    parts.append('      <span aria-hidden="true">/</span>')
    parts.append('      <a href="/guide/">使い方ガイド</a>')
    parts.append('      <span aria-hidden="true">/</span>')
    parts.append('      <span>%s</span>' % p['crumb'])
    parts.append('    </nav>\n')

    parts.append('    <span class="g-eyebrow">')
    parts.append('      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" '
                 'stroke="currentColor" stroke-width="2.5">%s</svg>' % p['icon'])
    parts.append('      %s' % p['eyebrow'])
    parts.append('    </span>\n')

    parts.append('    <h1>%s</h1>\n' % p['h1'])
    parts.append('    <p class="g-lead">\n      %s\n    </p>\n' % p['lead'])

    # この画面でできること
    parts.append('    <h2>この画面でできること</h2>')
    parts.append('    <div class="conds">\n      <ul>')
    for c in p['can_do']:
        parts.append('        <li>%s</li>' % c)
    parts.append('      </ul>\n    </div>\n')

    # 画面の見かた
    shot = p['shot']
    parts.append('    <h2>画面の見かた</h2>\n')
    parts.append('    <figure class="shot">')
    parts.append('      <img src="%s" alt="%s" width="1568" height="697">'
                 % (shot['img'], shot['alt']))
    for i, (left, top) in enumerate(shot.get('pins', []), 1):
        parts.append('      <span class="pin" style="left:%s;top:%s">%d</span>'
                     % (left, top, i))
    parts.append('    </figure>')
    if shot.get('cap'):
        parts.append('    <p class="shot-cap">%s</p>' % shot['cap'])
    if p.get('pin_list'):
        parts.append('\n    <ul class="pin-list">')
        for i, t in enumerate(p['pin_list'], 1):
            parts.append('      <li><span class="n">%d</span><span>%s</span></li>' % (i, t))
        parts.append('    </ul>\n')

    # 図解セクション
    for sec in p.get('sections', []):
        hid = ' id="%s"' % sec['id'] if sec.get('id') else ''
        parts.append('    <h2%s>%s</h2>' % (hid, sec['h2']))
        if sec.get('intro'):
            parts.append('    %s' % sec['intro'])
        if sec.get('svg'):
            parts.append('    <div class="figure">')
            parts.append(sec['svg'])
            parts.append('    </div>')
            if sec.get('fig_cap'):
                parts.append('    <p class="figure-cap">%s</p>' % sec['fig_cap'])
        if sec.get('after'):
            parts.append('    %s' % sec['after'])
        parts.append('')

    # 使い方
    if p.get('steps'):
        parts.append('    <h2>使い方</h2>')
        parts.append('    <ol class="steps">')
        for s in p['steps']:
            parts.append('      <li>%s</li>' % s)
        parts.append('    </ol>\n')

    if p.get('note'):
        parts.append('    <div class="note">\n      %s\n    </div>\n' % p['note'])

    # 表示条件
    parts.append('    <h2>表示条件</h2>')
    parts.append('    <div class="conds">')
    parts.append('      <h3>%s</h3>' % p.get('conds_title', 'この画面に表示されるもの'))
    parts.append('      <ul>')
    for c in p['conds']:
        parts.append('        <li>%s</li>' % c)
    parts.append('      </ul>\n    </div>\n')

    # FAQ
    if p.get('faq'):
        parts.append('    <h2>よくある質問</h2>')
        parts.append('    <div class="faq">')
        for q, a_html, _plain in p['faq']:
            parts.append('      <details>')
            parts.append('        <summary>%s</summary>' % q)
            parts.append('        <p>%s</p>' % a_html)
            parts.append('      </details>')
        parts.append('    </div>\n')

    # 関連ビュー
    parts.append('    <h2>関連するビュー</h2>')
    parts.append('    <div class="related">')
    for rs in p['related']:
        t, d = REGISTRY[rs]
        parts.append('      <a class="g-card" href="/guide/%s.html">' % rs)
        parts.append('        <span class="t">%s</span>' % t)
        parts.append('        <span class="d">%s</span>' % d)
        parts.append('      </a>')
    parts.append('    </div>\n')

    # CTA
    parts.append('    <div class="g-cta">')
    parts.append('      <h2>%s</h2>' % p.get('cta_h', 'Taskraを使ってみる'))
    parts.append('      <p>フリープランはクレジットカード不要。Googleアカウントですぐに始められます。</p>')
    parts.append('      <a class="btn btn-lg" href="https://app.taskra.jp" target="_blank" '
                 'rel="noopener">無料で始める</a>')
    parts.append('    </div>\n')

    parts.append('  </main>\n</div>\n')
    parts.append(FOOTER)
    parts.append('\n</body>\n</html>\n')
    return '\n'.join(parts)


# サイト全体のページ。ガイドを足したら sitemap も一緒に更新されるよう、
# ここで生成まで面倒を見る（手書きの sitemap は必ず古くなる）。
LP_PAGES = [
    ('/', '1.0', 'weekly'),
    ('/guide/', '0.9', 'monthly'),
    ('/terms.html', '0.3', 'yearly'),
    ('/privacy.html', '0.3', 'yearly'),
    ('/tokushoho.html', '0.3', 'yearly'),
    ('/contact.html', '0.4', 'yearly'),
]


def build_sitemap(slugs):
    import datetime
    nl = chr(10)
    today = datetime.date.today().isoformat()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pri, freq in LP_PAGES:
        out += ['  <url>', '    <loc>%s%s</loc>' % (SITE, loc),
                '    <lastmod>%s</lastmod>' % today,
                '    <changefreq>%s</changefreq>' % freq,
                '    <priority>%s</priority>' % pri, '  </url>']
    for slug in slugs:
        out += ['  <url>', '    <loc>%s/guide/%s.html</loc>' % (SITE, slug),
                '    <lastmod>%s</lastmod>' % today,
                '    <changefreq>monthly</changefreq>',
                '    <priority>0.8</priority>', '  </url>']
    out.append('</urlset>')
    io.open(os.path.join(BASE, 'sitemap.xml'), 'w', encoding='utf-8',
            newline=nl).write(nl.join(out) + nl)

    robots = nl.join(['User-agent: *', 'Allow: /', '',
                      'Sitemap: %s/sitemap.xml' % SITE, ''])
    io.open(os.path.join(BASE, 'robots.txt'), 'w', encoding='utf-8',
            newline=nl).write(robots)
    print('  sitemap.xml / robots.txt を更新（%d URL）' % (len(LP_PAGES) + len(slugs)))


def build():
    from guide_content import PAGES
    slugs = [s for _g, items in NAV for s, _e, _j in items]
    got = [p['slug'] for p in PAGES]
    missing = [s for s in slugs if s not in got]
    if missing:
        raise SystemExit('コンテンツ未定義のページがあります: %s' % ', '.join(missing))

    for p in PAGES:
        html = render_page(p)
        path = os.path.join(OUT, '%s.html' % p['slug'])
        io.open(path, 'w', encoding='utf-8', newline='\n').write(html)
        print('  %-12s %6d bytes' % (p['slug'] + '.html', len(html.encode('utf-8'))))
    build_sitemap([p['slug'] for p in PAGES])
    print('%d ページを生成しました。' % len(PAGES))


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    build()
