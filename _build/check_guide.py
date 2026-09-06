# -*- coding: utf-8 -*-
"""生成したガイドの自己点検。

リンク切れ・画像の欠落・JSON-LD の構文エラーは、公開してからでは
気づきにくい（見た目が壊れない）ので、生成のたびにここで潰す。

  実行:  python _build/check_guide.py
"""
import glob
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

errs = []
files = sorted(glob.glob('guide/*.html'))
existing = set(f.replace(os.sep, '/') for f in files)
imgdir = 'guide/img'
imgs = set(imgdir + '/' + f for f in os.listdir(imgdir)) if os.path.isdir(imgdir) else set()

for f in files:
    s = io.open(f, encoding='utf-8').read()
    tag = f.replace(os.sep, '/')

    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            json.loads(m.group(1))
        except Exception as e:
            errs.append('%s: JSON-LD が壊れています: %s' % (tag, e))

    for href in re.findall(r'href="(/[^"#]*)"', s):
        p = href.lstrip('/')
        if href.endswith('/'):
            p = p + 'index.html'
        if p and not os.path.exists(p) and p not in existing:
            errs.append('%s: リンク切れ %s' % (tag, href))

    for src in re.findall(r'<img src="(/[^"]+)"', s):
        p = src.lstrip('/')
        if p not in imgs and not os.path.exists(p):
            errs.append('%s: 画像がありません %s' % (tag, src))

    if not re.search(r'<title>.+</title>', s):
        errs.append('%s: title がありません' % tag)
    if not re.search(r'name="description" content=".{40,}"', s):
        errs.append('%s: description が短すぎます' % tag)
    if not re.search(r'rel="canonical"', s):
        errs.append('%s: canonical がありません' % tag)

    body = s.split('<body>')[1] if '<body>' in s else s
    if '%s' in body or '%d' in body:
        errs.append('%s: 書式指定子が本文に残っています' % tag)
    # 図解の中で文字がはみ出していないかの簡易チェック（viewBox 幅を超える x 座標）
    for sv in re.finditer(r'viewBox="0 0 (\d+) (\d+)"(.*?)</svg>', s, re.S):
        w = int(sv.group(1))
        for x in re.findall(r'<text x="(\d+)"', sv.group(3)):
            if int(x) > w:
                errs.append('%s: 図解の文字が viewBox の外にあります (x=%s > %d)' % (tag, x, w))
                break

print('検査ファイル: %d' % len(files))
if errs:
    print('--- 問題 %d 件 ---' % len(errs))
    for e in errs[:80]:
        print('  ' + e)
    sys.exit(1)
print('問題なし')
