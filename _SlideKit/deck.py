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
import copy

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
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

# 统一配色（IEEE 靛蓝学术）——全篇一致，不每页换色；白底浅母版
PRIMARY   = "1F3A8A"   # 主色 靛蓝：标题条/页码/主卡片/封面竖条
PRIMARY_D = "15275E"
ACCENT    = "C2772E"   # 暖橙：仅作次列/强调
INK_C     = "1A1F2B"   # 主文字
SUB_C     = "3A4252"   # 次文字
MUTED_C   = "6B7280"   # 弱化
PAGE_C    = "9AA3B0"   # 页码/页脚
HAIR_C    = "C7CDD6"   # 细分隔线
BG_C      = "FFFFFF"   # 母版底色（浅）
PAGE_LABEL = "Floorplan · 布图规划"


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
def _set_font(run, name=YAHEI, size=14, bold=False, color=INK_C, mono=False):
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
    colors = colors or [INK_C] * n
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


def _title_block(slide, title, sub, accent=PRIMARY):
    # 左侧主色竖条 + 全宽细分隔线已下放到版式（母版）上，这里只填每页不同的标题文本
    _txt(slide, (0.85, 0.42, 11.8, 0.8), [title], sizes=[28], bolds=[True], colors=[INK_C])
    if sub:
        _txt(slide, (0.87, 1.18, 11.8, 0.5), [sub], sizes=[14], colors=[SUB_C])


def _page(slide):
    """底部右侧：插入 PowerPoint 原生【幻灯片编号字段】(slidenum)，随增删/重排页自动更新；
    比手写 'N/24' 更省事——加页不用改总数。页脚标签在版式上，二者不重叠（左/右分置）。"""
    tb = slide.shapes.add_textbox(Inches(10.8), Inches(7.05), Inches(2.2), Inches(0.4))
    tf = tb.text_frame; tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Pt(0)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
    fld = p._p.makeelement(qn("a:fld"), {"id": "{8B7AE7E1-4F6F-4B3A-9E2D-1A2B3C4D5E6F}", "type": "slidenum"})
    rPr = fld.makeelement(qn("a:rPr"), {"lang": "en-US", "sz": "1000"})
    sf = rPr.makeelement(qn("a:solidFill"), {}); cl = sf.makeelement(qn("a:srgbClr"), {"val": PAGE_C})
    sf.append(cl); rPr.append(sf)
    rPr.append(rPr.makeelement(qn("a:latin"), {"typeface": YAHEI}))
    t = fld.makeelement(qn("a:t"), {}); t.text = "1"
    fld.append(rPr); fld.append(t)
    p._p.append(fld)
    return tb


def _layout_chrome(prs, lay, page_label):
    """把每页重复出现的"母版件"放到【版式】上——内容/导览页自动继承，新增页自动带样式；
    要全局改样式（条色/分隔线/页脚）只改这一处，或直接在 PowerPoint 的版式视图里改。
    python-pptx 不支持直接给版式加形状，故先在草稿页上画好，再把形状 XML 复制进版式、删草稿页。
    页脚标签 page_label 随每篇笔记而变（如 'Floorplan · 布图规划' / 'Placement · 布局'），由调用方传入。"""
    scratch = prs.slides.add_slide(lay)
    before = len(scratch.shapes._spTree)
    _bar(scratch, 0.6, 0.5, 0.16, 0.62, PRIMARY)        # 左侧主色竖条
    _bar(scratch, 0.85, 1.6, 11.85, 0.022, HAIR_C)      # 全宽细分隔线
    _txt(scratch, (0.6, 7.06, 6.5, 0.4), [page_label], sizes=[10], colors=[PAGE_C])  # 左下页脚标签（随文档变）
    lay_spTree = lay.shapes._spTree
    for el in list(scratch.shapes._spTree)[before:]:
        lay_spTree.append(copy.deepcopy(el))
    sldIdLst = prs.slides._sldIdLst                      # 删掉这张临时草稿页
    sid = sldIdLst[-1]
    rId = sid.get(qn("r:id"))
    sldIdLst.remove(sid)
    try:
        prs.part.drop_rel(rId)
    except Exception:
        pass


def _mask(slide):
    """封面/收尾页：盖一层满版白底，遮住版式继承来的内容页母版件，再画自己的整版设计。"""
    _bar(slide, 0, 0, SLIDE_W, SLIDE_H, BG_C)


def _bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = _rgb(color)


def _pic(slide, path, box):
    iw, ih = Image.open(path).size
    x, t, w, h = fit(box, iw, ih)
    slide.shapes.add_picture(path, Inches(x), Inches(t), Inches(w), Inches(h))


def _bullets_lines(bullets):
    return ["▪  " + b for b in bullets]


CIRC = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭"


def _marks(items, style="bullet"):
    """并列内容用 ▪；递进/有序内容用 ①②③（style='num'）。"""
    if style == "num":
        return [f"{CIRC[i]}  {b}" for i, b in enumerate(items)]
    return ["▪  " + b for b in items]


def _circ_num(slide, x, y, num, d=0.46, fill=PRIMARY, fg="FFFFFF", fs=15):
    sp = slide.shapes.add_shape(9, Inches(x), Inches(y), Inches(d), Inches(d))  # 9=oval
    sp.fill.solid(); sp.fill.fore_color.rgb = _rgb(fill)
    sp.line.fill.background(); sp.shadow.inherit = False
    tf = sp.text_frame; tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = str(num)
    _set_font(r, size=fs, bold=True, color=fg)


def _cover(slide, s):
    """封面：浅底 + 左侧主色厚竖条 + 大标题，独立于内容页版式。"""
    _bg(slide, BG_C)
    _mask(slide)
    _bar(slide, 0.0, 0.0, 0.30, SLIDE_H, PRIMARY)
    _txt(slide, (1.15, 1.45, 11, 0.4), [s.get("tag", "数字 IC 后端 · DVD Lecture 6")],
         sizes=[14], bolds=[True], colors=[PRIMARY])
    _txt(slide, (1.1, 2.45, 11.6, 1.3), [s["title"]], sizes=[46], bolds=[True], colors=[INK_C])
    if s.get("sub"):
        _txt(slide, (1.15, 3.95, 11, 0.6), [s["sub"]], sizes=[19], colors=[SUB_C])
    _bar(slide, 1.15, 4.80, 3.8, 0.045, PRIMARY)
    if s.get("line"):
        _txt(slide, (1.15, 5.08, 11.4, 0.6), [s["line"]], sizes=[14], bolds=[True], colors=[ACCENT])
    _txt(slide, (1.15, 6.85, 11.6, 0.4), [s.get("src", "")], sizes=[11], colors=[MUTED_C])


def _agenda(slide, s):
    """导览：浅底 + 标题条 + 两列编号小节 + 底部主线高亮，独立于内容页版式。"""
    _bg(slide, BG_C)
    _title_block(slide, s["title"], s.get("sub"))
    secs = s["sections"]; colx = [0.95, 7.0]; w = 5.45
    top0, rowh, per = 2.05, 1.16, 4
    for j, (num, ttl, det) in enumerate(secs):
        x = colx[j // per]; y = top0 + (j % per) * rowh
        _circ_num(slide, x, y, num)
        _txt(slide, (x + 0.64, y - 0.06, w, 0.45), [ttl], sizes=[16], bolds=[True], colors=[INK_C])
        _txt(slide, (x + 0.64, y + 0.40, w, 0.55), [det], sizes=[12.5], colors=[MUTED_C])
    if s.get("line"):
        _card(slide, 0.95, 6.28, 11.0, 0.6, fill="F6E8D5", line="E4C79A")
        _txt(slide, (1.25, 6.41, 10.6, 0.4), [s["line"]], sizes=[13], bolds=[True], colors=["8A5212"])


def _close(slide, s):
    """收尾：浅底 + 左侧主色厚竖条，与封面呼应。"""
    _bg(slide, BG_C)
    _mask(slide)
    _bar(slide, 0.0, 0.0, 0.30, SLIDE_H, PRIMARY)
    _txt(slide, (1.1, 2.75, 11.6, 1.2), [s["title"]], sizes=[44], bolds=[True], colors=[INK_C])
    if s.get("sub"):
        _txt(slide, (1.15, 4.15, 11, 0.6), [s["sub"]], sizes=[18], colors=[SUB_C])
    _bar(slide, 1.15, 4.95, 3.4, 0.045, ACCENT)
    if s.get("line"):
        _txt(slide, (1.15, 5.25, 11.4, 0.5), [s["line"]], sizes=[13], colors=[MUTED_C])
    _txt(slide, (1.15, 6.85, 11.6, 0.4), [s.get("src", "")], sizes=[11], colors=[MUTED_C])


def _clean_master(prs, keep):
    """清掉默认模板自带的占位符（日期/页脚/页码/标题/正文）并删掉未使用的版式：
    否则默认占位符会与自定义母版件重叠（日期框压住页脚标签），且默认模板是 4:3、占位符按
    4:3 排布，在 16:9 母版视图里显得不对。只保留实际使用的那张空白版式（已 16:9、放了母版件）。"""
    for m in prs.slide_masters:
        for ph in list(m.placeholders):                       # 母版上的占位符
            ph._element.getparent().remove(ph._element)
        for lay in list(m.slide_layouts):
            if lay._element is keep._element:                 # 保留并清干净这张要用的版式
                for ph in list(lay.placeholders):
                    ph._element.getparent().remove(ph._element)
            else:                                             # 删掉其余未用版式（4:3）
                try:
                    m.slide_layouts.remove(lay)
                except Exception:
                    for ph in list(lay.placeholders):
                        ph._element.getparent().remove(ph._element)


def build_pptx(specs, out_pptx, total, author="J.C", asset_dir="", template=None, page_label=PAGE_LABEL):
    """template=<.pptx 路径> 时，基于该模板（继承其母版/主题/字体），并清掉模板自带的示例幻灯片。"""
    prs = Presentation(template) if template else Presentation()
    if template:
        sld = prs.slides._sldIdLst
        for s in list(sld):
            sld.remove(s)
    prs.slide_width = Inches(SLIDE_W); prs.slide_height = Inches(SLIDE_H)
    blank = (min(prs.slide_layouts, key=lambda L: len(L.placeholders)) if template
             else prs.slide_layouts[6])
    _clean_master(prs, blank)   # 删默认 4:3 占位符/未用版式，避免页脚重叠、母版按 16:9
    _layout_chrome(prs, blank, page_label)  # 母版件下放到版式：所有内容页继承，新增页自动带样式
    for i, s in enumerate(specs, 1):
        sl = prs.slides.add_slide(blank)
        k = s["kind"]
        if k in ("cover", "title"):
            _cover(sl, s); continue
        if k == "close":
            _close(sl, s); continue
        if k == "agenda":
            _agenda(sl, s); _page(sl); continue
        acc = (s.get("accent", PRIMARY) or PRIMARY).lstrip("#")
        _title_block(sl, s["title"], s.get("sub"))
        if k == "split":
            _txt(sl, (0.7, 1.72, 5.2, 5.4), _marks(s["bullets"], s.get("style", "bullet")),
                 sizes=[14] * len(s["bullets"]), colors=[INK_C] * len(s["bullets"]), space=8, line_sp=1.1)
            _pic(sl, os.path.join(asset_dir, s["figure"]), (6.0, 1.7, 6.85, 5.25))
        elif k == "cards2":
            for j, (hdr, code, a) in enumerate(s["cards"]):
                x = 0.7 + j * 6.1
                _card(sl, x, 1.7, 5.8, 5.1, accent=a)
                _txt(sl, (x + 0.35, 1.95, 5.2, 0.5), [hdr], sizes=[15], bolds=[True], colors=[a])
                _txt(sl, (x + 0.35, 2.6, 5.3, 4.0), code, sizes=[11.5] * len(code), monos=[True] * len(code),
                     colors=[INK_C] * len(code), space=7)
        elif k == "grid6":
            for j, (t1, t2, c) in enumerate(s["items"]):
                x = 0.7 + (j % 3) * 4.05
                y = 1.75 + (j // 3) * 2.45
                _card(sl, x, y, 3.75, 2.15, accent=c)
                _txt(sl, (x + 0.3, y + 0.28, 3.3, 0.6), [t1], sizes=[15], bolds=[True], colors=[INK_C])
                _txt(sl, (x + 0.3, y + 1.05, 3.3, 0.9), ["→ " + t2], sizes=[12], colors=[MUTED_C])
        elif k == "cols2":
            for j, (hdr, items, a) in enumerate(s["cols"]):
                x = 0.7 + j * 6.1
                _card(sl, x, 1.7, 5.8, 5.1, accent=a)
                _txt(sl, (x + 0.35, 1.95, 5.2, 0.5), [hdr], sizes=[15], bolds=[True], colors=[a])
                _txt(sl, (x + 0.35, 2.55, 5.3, 4.2), _bullets_lines(items),
                     sizes=[12.5] * len(items), colors=[INK_C] * len(items), space=6, line_sp=1.08)
        elif k == "bullets":
            items = s["bullets"]
            if s.get("two_col"):
                mid = (len(items) + 1) // 2
                _txt(sl, (0.7, 1.75, 6.0, 5.3), _bullets_lines(items[:mid]),
                     sizes=[14.5] * mid, colors=[INK_C] * mid, space=9, line_sp=1.2)
                _txt(sl, (6.9, 1.75, 6.0, 5.3), _bullets_lines(items[mid:]),
                     sizes=[14.5] * (len(items) - mid), colors=[INK_C] * (len(items) - mid), space=9, line_sp=1.2)
            else:
                _txt(sl, (0.7, 1.75, 12.0, 5.3), _bullets_lines(items),
                     sizes=[15] * len(items), colors=[INK_C] * len(items), space=10, line_sp=1.25)
        _page(sl)
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


def _wrap(s, maxu):
    """按显示宽度折行（CJK≈1，ASCII≈0.55 单位），让预览贴近 pptx 的自动换行。"""
    out, line, u = [], "", 0.0
    for ch in s:
        w = 0.55 if ord(ch) < 128 else 1.0
        if u + w > maxu and line:
            out.append(line); line, u = ch, w
        else:
            line += ch; u += w
    if line:
        out.append(line)
    return out or [""]


def _pbul(ax, xb, xt, yy, text, fs, color, maxu, lh=0.40, gap=0.16, mark="▪"):
    """预览端：画一条带标记(▪ 或 ①)的可折行要点，返回下一行 y。"""
    _mtext(ax, xb, yy, mark, fs=fs, color=color, bold=True)
    for ln in _wrap(text, maxu):
        _mtext(ax, xt, yy, ln, fs=fs)
        yy += lh
    return yy + gap


def _pcover(ax, s):
    ax.add_patch(Rectangle((0, 0), SLIDE_W, SLIDE_H, fc="white", ec="none", zorder=0))
    ax.add_patch(Rectangle((0, 0), 0.30, SLIDE_H, fc="#" + PRIMARY, ec="none", zorder=2))
    _mtext(ax, 1.15, 1.45, s.get("tag", "数字 IC 后端 · DVD Lecture 6"), fs=13, bold=True, color="#" + PRIMARY)
    _mtext(ax, 1.1, 2.45, s["title"], fs=40, bold=True, color="#" + INK_C)
    if s.get("sub"):
        _mtext(ax, 1.15, 3.95, s["sub"], fs=17, color="#" + SUB_C)
    ax.add_patch(Rectangle((1.15, SLIDE_H - 4.80 - 0.05), 3.8, 0.05, fc="#" + PRIMARY, ec="none", zorder=2))
    if s.get("line"):
        _mtext(ax, 1.15, 5.18, s["line"], fs=13, bold=True, color="#" + ACCENT)
    _mtext(ax, 1.15, 6.9, s.get("src", ""), fs=10, color="#" + MUTED_C)


def _pclose(ax, s):
    ax.add_patch(Rectangle((0, 0), SLIDE_W, SLIDE_H, fc="white", ec="none", zorder=0))
    ax.add_patch(Rectangle((0, 0), 0.30, SLIDE_H, fc="#" + PRIMARY, ec="none", zorder=2))
    _mtext(ax, 1.1, 2.75, s["title"], fs=38, bold=True, color="#" + INK_C)
    if s.get("sub"):
        _mtext(ax, 1.15, 4.15, s["sub"], fs=16, color="#" + SUB_C)
    ax.add_patch(Rectangle((1.15, SLIDE_H - 4.95 - 0.05), 3.4, 0.05, fc="#" + ACCENT, ec="none", zorder=2))
    if s.get("line"):
        _mtext(ax, 1.15, 5.40, s["line"], fs=12, color="#" + MUTED_C)
    _mtext(ax, 1.15, 6.9, s.get("src", ""), fs=10, color="#" + MUTED_C)


def _pagenda(ax, s, i, page_label):
    ax.add_patch(Rectangle((0, 0), SLIDE_W, SLIDE_H, fc="white", ec="none", zorder=0))
    ax.add_patch(Rectangle((0.6, SLIDE_H - 0.5 - 0.62), 0.16, 0.62, fc="#" + PRIMARY, ec="none", zorder=2))
    _mtext(ax, 0.85, 0.5, s["title"], fs=24, bold=True)
    if s.get("sub"):
        _mtext(ax, 0.87, 1.2, s["sub"], fs=13, color=T.MUTED)
    ax.add_patch(Rectangle((0.85, SLIDE_H - 1.6 - 0.02), 11.85, 0.02, fc="#" + HAIR_C, ec="none", zorder=1))
    secs = s["sections"]; colx = [0.95, 7.0]; top0, rowh, per = 2.05, 1.16, 4
    for j, (num, ttl, det) in enumerate(secs):
        x = colx[j // per]; y = top0 + (j % per) * rowh
        ax.add_patch(Circle((x + 0.23, SLIDE_H - y - 0.23), 0.23, fc="#" + PRIMARY, ec="none", zorder=3))
        _mtext(ax, x + 0.23, y + 0.23, str(num), fs=14, bold=True, color="white", ha="center", va="center")
        _mtext(ax, x + 0.64, y - 0.02, ttl, fs=15, bold=True, color="#" + INK_C)
        _mtext(ax, x + 0.64, y + 0.42, det, fs=12, color="#" + MUTED_C)
    if s.get("line"):
        ax.add_patch(FancyBboxPatch((0.95, SLIDE_H - 6.28 - 0.6), 11.0, 0.6,
                     boxstyle="round,pad=0,rounding_size=0.06", fc="#F6E8D5", ec="#E4C79A", lw=1.2, zorder=2))
        _mtext(ax, 1.25, 6.5, s["line"], fs=12.5, bold=True, color="#8A5212")
    _mtext(ax, 0.6, 7.1, page_label, fs=10, color="#" + PAGE_C)
    _mtext(ax, 12.9, 7.1, str(i), fs=10, color="#" + PAGE_C, ha="right")


def build_previews(specs, outdir, total, asset_dir="", page_label=PAGE_LABEL):
    os.makedirs(outdir, exist_ok=True)
    paths = []
    T.setup_fonts()
    for i, s in enumerate(specs, 1):
        fig, ax = plt.subplots(figsize=(SLIDE_W, SLIDE_H), dpi=110)
        ax.set_xlim(0, SLIDE_W); ax.set_ylim(0, SLIDE_H); ax.axis("off"); ax.set_autoscale_on(False)
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        k = s["kind"]; acc = s.get("accent", T.BLUE)
        accx = acc if acc.startswith("#") else "#" + acc
        if k in ("cover", "title"):
            _pcover(ax, s); paths.append(_save_prev(fig, outdir, i)); continue
        if k == "close":
            _pclose(ax, s); paths.append(_save_prev(fig, outdir, i)); continue
        if k == "agenda":
            _pagenda(ax, s, i, page_label); paths.append(_save_prev(fig, outdir, i)); continue
        ax.add_patch(Rectangle((0, 0), SLIDE_W, SLIDE_H, fc="white", ec="none", zorder=0))
        ax.add_patch(Rectangle((0.6, SLIDE_H - 0.5 - 0.62), 0.16, 0.62, fc="#" + PRIMARY, ec="none", zorder=2))
        _mtext(ax, 0.85, 0.5, s["title"], fs=24, bold=True)
        if s.get("sub"):
            _mtext(ax, 0.87, 1.2, s["sub"], fs=13, color=T.MUTED)
        ax.add_patch(Rectangle((0.85, SLIDE_H - 1.6 - 0.02), 11.85, 0.02, fc="#" + HAIR_C, ec="none", zorder=1))
        _mtext(ax, 0.6, 7.1, page_label, fs=10, color="#" + PAGE_C)
        if k == "split":
            style = s.get("style", "bullet")
            yy = 1.95
            for bi, b in enumerate(s["bullets"]):
                mk = CIRC[bi] if style == "num" else "▪"
                yy = _pbul(ax, 0.7, 1.05, yy, b, 14, accx, 24, mark=mk)
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
                yy = 2.55
                for it in items:
                    yy = _pbul(ax, x + 0.32, x + 0.6, yy, it, 12.5, ac, 28, lh=0.36, gap=0.12)
        elif k == "bullets":
            items = s["bullets"]
            if s.get("two_col"):
                mid = (len(items) + 1) // 2
                yy = 1.95
                for b in items[:mid]:
                    yy = _pbul(ax, 0.7, 1.0, yy, b, 14, accx, 30)
                yy = 1.95
                for b in items[mid:]:
                    yy = _pbul(ax, 6.9, 7.2, yy, b, 14, accx, 30)
            else:
                yy = 1.95
                for b in items:
                    yy = _pbul(ax, 0.7, 1.0, yy, b, 15, accx, 52)
        _mtext(ax, 12.9, 7.1, str(i), fs=10, color="#" + PAGE_C, ha="right")
        paths.append(_save_prev(fig, outdir, i))
    return paths


def _save_prev(fig, outdir, i):
    p = os.path.join(outdir, f"prev_{i:02d}.png")
    fig.savefig(p, dpi=110); plt.close(fig)
    return p
