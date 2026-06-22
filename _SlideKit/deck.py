# -*- coding: utf-8 -*-
"""
_SlideKit · deck.py  (v3 · 可编辑 PPT)
=====================================
从一份「幻灯片规格」(specs) 同时产出：
  build_pptx(specs)      → 可编辑 .pptx（原生标题/要点文本 + 插入的论文插图）
  build_previews(specs)  → 每页一张 matplotlib 版面预览 PNG（供肉眼校对，因为本机无法渲染 pptx）
两者用同一套版面坐标，预览看着对，pptx 版面就对。

规格 spec = {kind, title, sub, bullets, bullets2, figure, accent, ...}
kind ∈ title | split | cards2 | grid6 | cols2 | close
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle, FancyBboxPatch
from PIL import Image

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as T  # noqa: E402

SLIDE_W, SLIDE_H = 13.333, 7.5
YAHEI = "Microsoft YaHei"
MONO = "Consolas"


def _rgb(hexc):
    return RGBColor.from_string(hexc.lstrip("#"))


def fit(box, iw, ih):
    """图片等比放入 box=(x,top,w,h)，返回居中后的 (x,top,w,h)。"""
    x, t, w, h = box
    ar = iw / float(ih)
    if ar > w / float(h):
        nw, nh = w, w / ar
    else:
        nh, nw = h, h * ar
    return x + (w - nw) / 2.0, t + (h - nh) / 2.0, nw, nh


# ============================ pptx 端 ===================================== #
def _set_font(run, name=YAHEI, size=14, bold=False, color="1E293B", mono=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = _rgb(color)
    fn = MONO if mono else name
    run.font.name = fn
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        e = rPr.find(qn(tag))
        if e is None:
            e = rPr.makeelement(qn(tag), {}); rPr.append(e)
        e.set("typeface", fn)


def _txt(slide, box, lines, sizes=None, colors=None, bolds=None, monos=None,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space=6, wrap=True, line_sp=None):
    x, t, w, h = box
    tb = slide.shapes.add_textbox(Inches(x), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Pt(2)
    tf.margin_top = tf.margin_bottom = Pt(2)
    n = len(lines)
    sizes = sizes or [14] * n
    colors = colors or ["1E293B"] * n
    bolds = bolds or [False] * n
    monos = monos or [False] * n
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space)
        if line_sp:
            p.line_spacing = line_sp
        r = p.add_run(); r.text = ln
        _set_font(r, size=sizes[i], color=colors[i], bold=bolds[i], mono=monos[i])
    return tb


def _bar(slide, x, t, w, h, color):
    sp = slide.shapes.add_shape(1, Inches(x), Inches(t), Inches(w), Inches(h))  # 1=rect
    sp.fill.solid(); sp.fill.fore_color.rgb = _rgb(color)
    sp.line.fill.background()
    sp.shadow.inherit = False
    return sp


def _card(slide, x, t, w, h, fill="FFFFFF", line="CBD5E1", accent=None):
    sp = slide.shapes.add_shape(5, Inches(x), Inches(t), Inches(w), Inches(h))  # 5=rounded rect
    sp.fill.solid(); sp.fill.fore_color.rgb = _rgb(fill)
    sp.line.color.rgb = _rgb(line); sp.line.width = Pt(1)
    sp.shadow.inherit = False
    if accent:
        _bar(slide, x, t + 0.12, 0.09, h - 0.24, accent)
    return sp


def _title_block(slide, title, sub, accent):
    _bar(slide, 0.6, 0.5, 0.16, 0.62, accent)
    _txt(slide, (0.85, 0.42, 11.8, 0.8), [title], sizes=[28], bolds=[True], colors=["1E293B"])
    if sub:
        _txt(slide, (0.87, 1.18, 11.8, 0.5), [sub], sizes=[14], colors=["64748B"])


def _page(slide, n, total, label="Floorplan"):
    _txt(slide, (10.8, 7.06, 2.2, 0.4), [f"{n:02d} / {total:02d}"], sizes=[10], colors=["94A3B8"], align=PP_ALIGN.RIGHT)
    _txt(slide, (0.6, 7.06, 4, 0.4), [label], sizes=[10], colors=["94A3B8"])


def _bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = _rgb(color)


def _pic(slide, path, box):
    iw, ih = Image.open(path).size
    x, t, w, h = fit(box, iw, ih)
    slide.shapes.add_picture(path, Inches(x), Inches(t), Inches(w), Inches(h))


def _bullets_lines(bullets):
    return ["▪  " + b for b in bullets]


def build_pptx(specs, out_pptx, total, author="J.C", asset_dir=""):
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W); prs.slide_height = Inches(SLIDE_H)
    blank = prs.slide_layouts[6]
    for i, s in enumerate(specs, 1):
        sl = prs.slides.add_slide(blank)
        k = s["kind"]; acc = s.get("accent", "2563EB")
        if k in ("title", "close"):
            _bg(sl, "1E293B")
            _bar(sl, 0.9, 2.5 if k == "title" else 3.0, 0.16, 0.7, "F59E0B")
            _txt(sl, (1.2, 2.3 if k == "title" else 2.85, 11, 1.2), [s["title"]], sizes=[44], bolds=[True], colors=["FFFFFF"])
            if s.get("sub"):
                _txt(sl, (1.2, 3.6 if k == "title" else 3.9, 11, 0.6), [s["sub"]], sizes=[18], colors=["CBD5E1"])
            _txt(sl, (1.2, 6.6, 11, 0.5), [s.get("src", "")], sizes=[11], colors=["64748B"])
            continue
        _title_block(sl, s["title"], s.get("sub"), acc)
        if k == "split":
            _txt(sl, (0.7, 1.75, 5.15, 5.3), _bullets_lines(s["bullets"]),
                 sizes=[15] * len(s["bullets"]), colors=["1E293B"] * len(s["bullets"]), space=10, line_sp=1.15)
            _pic(sl, os.path.join(asset_dir, s["figure"]), (6.0, 1.7, 6.85, 5.25))
        elif k == "cards2":
            for j, (hdr, code, a) in enumerate(s["cards"]):
                x = 0.7 + j * 6.1
                _card(sl, x, 1.7, 5.8, 5.1, accent=a)
                _txt(sl, (x + 0.35, 1.95, 5.2, 0.5), [hdr], sizes=[15], bolds=[True], colors=[a])
                _txt(sl, (x + 0.35, 2.6, 5.3, 4.0), code, sizes=[11.5] * len(code), monos=[True] * len(code),
                     colors=["1E293B"] * len(code), space=7)
        elif k == "grid6":
            for j, (t1, t2, c) in enumerate(s["items"]):
                x = 0.7 + (j % 3) * 4.05
                y = 1.75 + (j // 3) * 2.45
                _card(sl, x, y, 3.75, 2.15, accent=c)
                _txt(sl, (x + 0.3, y + 0.28, 3.3, 0.6), [t1], sizes=[15], bolds=[True], colors=["1E293B"])
                _txt(sl, (x + 0.3, y + 1.05, 3.3, 0.9), ["→ " + t2], sizes=[12], colors=["64748B"])
        elif k == "cols2":
            for j, (hdr, items, a) in enumerate(s["cols"]):
                x = 0.7 + j * 6.1
                _card(sl, x, 1.7, 5.8, 5.1, accent=a)
                _txt(sl, (x + 0.35, 1.95, 5.2, 0.5), [hdr], sizes=[15], bolds=[True], colors=[a])
                _txt(sl, (x + 0.35, 2.6, 5.25, 4.1), _bullets_lines(items),
                     sizes=[13] * len(items), colors=["1E293B"] * len(items), space=8, line_sp=1.1)
        elif k == "bullets":
            items = s["bullets"]
            if s.get("two_col"):
                mid = (len(items) + 1) // 2
                _txt(sl, (0.7, 1.75, 6.0, 5.3), _bullets_lines(items[:mid]),
                     sizes=[14.5] * mid, colors=["1E293B"] * mid, space=9, line_sp=1.2)
                _txt(sl, (6.9, 1.75, 6.0, 5.3), _bullets_lines(items[mid:]),
                     sizes=[14.5] * (len(items) - mid), colors=["1E293B"] * (len(items) - mid), space=9, line_sp=1.2)
            else:
                _txt(sl, (0.7, 1.75, 12.0, 5.3), _bullets_lines(items),
                     sizes=[15] * len(items), colors=["1E293B"] * len(items), space=10, line_sp=1.25)
        _page(sl, i, total)
    try:
        prs.core_properties.author = author
    except Exception:
        pass
    os.makedirs(os.path.dirname(out_pptx), exist_ok=True)
    prs.save(out_pptx)
    return out_pptx


# ============================ 预览端 (matplotlib) ========================= #
def _mtext(ax, x, ytop, s, fs=14, color=T.INK, bold=False, mono=False, ha="left", va="top"):
    ax.text(x, SLIDE_H - ytop, s, fontsize=fs, color=color, ha=ha, va=va,
            fontweight=("bold" if bold else "normal"),
            family=("monospace" if mono else "sans-serif"))


def _mcard(ax, x, ytop, w, h, fc="#FFFFFF", ec=T.LINE, accent=None):
    ax.add_patch(FancyBboxPatch((x, SLIDE_H - ytop - h), w, h, boxstyle="round,pad=0,rounding_size=0.08",
                 fc=fc, ec=ec, lw=1.3, zorder=2))
    if accent:
        ax.add_patch(Rectangle((x, SLIDE_H - ytop - h + 0.12), 0.09, h - 0.24, fc=accent, ec="none", zorder=3))


def build_previews(specs, outdir, total, asset_dir=""):
    os.makedirs(outdir, exist_ok=True)
    paths = []
    T.setup_fonts()
    for i, s in enumerate(specs, 1):
        fig, ax = plt.subplots(figsize=(SLIDE_W, SLIDE_H), dpi=110)
        ax.set_xlim(0, SLIDE_W); ax.set_ylim(0, SLIDE_H); ax.axis("off"); ax.set_autoscale_on(False)
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        k = s["kind"]; acc = s.get("accent", T.BLUE)
        accx = acc if acc.startswith("#") else "#" + acc
        if k in ("title", "close"):
            ax.add_patch(Rectangle((0, 0), SLIDE_W, SLIDE_H, fc=T.INK, ec="none", zorder=0))
            ax.add_patch(Rectangle((0.9, SLIDE_H - (2.5 if k == "title" else 3.0) - 0.7), 0.16, 0.7, fc=T.AMBER, ec="none", zorder=2))
            _mtext(ax, 1.2, 2.3 if k == "title" else 2.85, s["title"], fs=40, color="white", bold=True)
            if s.get("sub"):
                _mtext(ax, 1.2, 3.7 if k == "title" else 4.0, s["sub"], fs=17, color="#CBD5E1")
            _mtext(ax, 1.2, 6.7, s.get("src", ""), fs=10, color="#64748B")
            paths.append(_save_prev(fig, outdir, i)); continue
        ax.add_patch(Rectangle((0, 0), SLIDE_W, SLIDE_H, fc="white", ec="none", zorder=0))
        ax.add_patch(Rectangle((0.6, SLIDE_H - 0.5 - 0.62), 0.16, 0.62, fc=accx, ec="none", zorder=2))
        _mtext(ax, 0.85, 0.5, s["title"], fs=24, bold=True)
        if s.get("sub"):
            _mtext(ax, 0.87, 1.2, s["sub"], fs=13, color=T.MUTED)
        if k == "split":
            yy = 1.95
            for b in s["bullets"]:
                _mtext(ax, 0.7, yy, "▪", fs=15, color=accx, bold=True)
                _mtext(ax, 1.02, yy, b, fs=14)
                yy += 0.62
            box = (6.0, 1.7, 6.85, 5.25)
            p = os.path.join(asset_dir, s["figure"])
            iw, ih = Image.open(p).size
            fx, ft, fw, fh = fit(box, iw, ih)
            ax.imshow(mpimg.imread(p), extent=[fx, fx + fw, SLIDE_H - ft - fh, SLIDE_H - ft], aspect="auto", zorder=4)
            ax.add_patch(Rectangle((box[0], SLIDE_H - box[1] - box[3]), box[2], box[3], fc="none", ec="#E2E8F0", lw=1, zorder=1))
        elif k == "cards2":
            for j, (hdr, code, a) in enumerate(s["cards"]):
                x = 0.7 + j * 6.1
                _mcard(ax, x, 1.7, 5.8, 5.1, accent="#" + a if not a.startswith("#") else a)
                _mtext(ax, x + 0.35, 1.95, hdr, fs=14, bold=True, color="#" + a if not a.startswith("#") else a)
                yy = 2.6
                for ln in code:
                    _mtext(ax, x + 0.35, yy, ln, fs=11, mono=True); yy += 0.42
        elif k == "grid6":
            for j, (t1, t2, c) in enumerate(s["items"]):
                x = 0.7 + (j % 3) * 4.05; y = 1.75 + (j // 3) * 2.45
                _mcard(ax, x, y, 3.75, 2.15, accent=c if c.startswith("#") else "#" + c)
                _mtext(ax, x + 0.3, y + 0.28, t1, fs=14, bold=True)
                _mtext(ax, x + 0.3, y + 1.05, "→ " + t2, fs=12, color=T.MUTED)
        elif k == "cols2":
            for j, (hdr, items, a) in enumerate(s["cols"]):
                x = 0.7 + j * 6.1
                ac = a if a.startswith("#") else "#" + a
                _mcard(ax, x, 1.7, 5.8, 5.1, accent=ac)
                _mtext(ax, x + 0.35, 1.95, hdr, fs=14, bold=True, color=ac)
                yy = 2.6
                for it in items:
                    _mtext(ax, x + 0.35, yy, "▪ " + it, fs=13); yy += 0.6
        elif k == "bullets":
            items = s["bullets"]
            if s.get("two_col"):
                mid = (len(items) + 1) // 2
                yy = 1.95
                for b in items[:mid]:
                    _mtext(ax, 0.7, yy, "▪", fs=14, color=accx, bold=True); _mtext(ax, 1.0, yy, b, fs=14); yy += 0.62
                yy = 1.95
                for b in items[mid:]:
                    _mtext(ax, 6.9, yy, "▪", fs=14, color=accx, bold=True); _mtext(ax, 7.2, yy, b, fs=14); yy += 0.62
            else:
                yy = 1.95
                for b in items:
                    _mtext(ax, 0.7, yy, "▪", fs=15, color=accx, bold=True); _mtext(ax, 1.0, yy, b, fs=15); yy += 0.66
        _mtext(ax, 12.9, 7.1, f"{i:02d}/{total:02d}", fs=10, color=T.MUTED, ha="right")
        paths.append(_save_prev(fig, outdir, i))
    return paths


def _save_prev(fig, outdir, i):
    p = os.path.join(outdir, f"prev_{i:02d}.png")
    fig.savefig(p, dpi=110); plt.close(fig)
    return p
