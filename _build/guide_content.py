# -*- coding: utf-8 -*-
"""ページ内容の集約。ここでの並び順が生成順になる（ナビの並びとは独立）。"""
from content_basic import PAGES as _BASIC
from content_schedule import PAGES as _SCHEDULE
from content_filter import PAGES as _FILTER
from content_review import PAGES as _REVIEW

PAGES = _BASIC + _SCHEDULE + _FILTER + _REVIEW
