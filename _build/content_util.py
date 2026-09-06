# -*- coding: utf-8 -*-
"""ページ内容を書くときの小道具。"""
import re


def faq(q, a_html):
    """FAQ を (質問, 本文HTML, 構造化データ用のプレーン текст) の3つ組にする。

    JSON-LD にタグを入れると Google のリッチリザルトテストで警告になるので、
    同じ文面から自動で剥がす。二重管理を避けるための関数。
    """
    plain = re.sub(r'<[^>]+>', '', a_html)
    plain = re.sub(r'\s+', ' ', plain).strip()
    return (q, a_html, plain)


# 図解で共通して使う矢印マーカー。id が衝突しないよう呼び出し側で名前を渡す。
def arrow_defs(name, color='#4f46e5'):
    return ('<defs><marker id="%s" viewBox="0 0 10 10" refX="8" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="%s"/></marker></defs>' % (name, color))


_svg_seq = [0]


def svg(view_box, title, desc, body):
    """タイトルと説明を持つ SVG。読み上げと検索エンジンのために必ず付ける。

    id は連番で振る。hash() は実行ごとに値が変わるため、使うと
    中身を変えていないのに毎回 diff が出てしまう。
    """
    _svg_seq[0] += 1
    n = _svg_seq[0]
    tid = 'svgt-%d' % n
    did = 'svgd-%d' % n
    return ('      <svg viewBox="%s" role="img" aria-labelledby="%s %s" '
            'xmlns="http://www.w3.org/2000/svg">\n'
            '        <title id="%s">%s</title>\n'
            '        <desc id="%s">%s</desc>\n%s\n      </svg>'
            % (view_box, tid, did, tid, title, did, desc, body))
