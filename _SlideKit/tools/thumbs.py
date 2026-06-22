# -*- coding: utf-8 -*-
"""QA helper: 把某目录下的大图缩成 <=maxw 宽的缩略图到 <dir>/_qa/，便于在对话里查看。
用法: python tools/thumbs.py <dir> [maxw=1280]"""
import os
import sys
from PIL import Image

src = sys.argv[1]
maxw = int(sys.argv[2]) if len(sys.argv) > 2 else 1280
out = os.path.join(src, "_qa")
os.makedirs(out, exist_ok=True)
for fn in sorted(os.listdir(src)):
    if fn.lower().endswith(".png") and not fn.startswith("_"):
        im = Image.open(os.path.join(src, fn)).convert("RGB")
        w, h = im.size
        if w > maxw:
            im = im.resize((maxw, int(h * maxw / w)), Image.LANCZOS)
        im.save(os.path.join(out, fn), quality=85)
        print(fn, im.size)
