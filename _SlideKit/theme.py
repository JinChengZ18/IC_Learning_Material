# -*- coding: utf-8 -*-
"""
_SlideKit · theme.py  (v3 · 鲜明 IC 学术配色)
=============================================
论文/图书级 IC 插图主题。配色为**鲜明的 IC 学术多色「语义」方案**——
不同功能用不同色相、足够饱和以最大化元素辨识度（蓝=逻辑/信号，青绿=存储/Macro，
橙=电源/PG，红=IO/高亮，紫=时钟，石板灰=衬底/中性）。**用纯色不滥用透明度**（卡片底用 _L 浅调实色）。

一次导出 PNG(给 PPT) + SVG(给 md)。在 diagrams/decks 里 `import theme as T`。

设计准则（向论文插图看齐）：
- 白底、细线、2px 饱和描边、浅色填充 + 深色文字的"两段色"块；
- 语义配色固定，必要处给图例(legend)；
- 柔和投影做层次，不靠粗边框；克制留白；
- 标题用小色块 + 粗墨色字，不用整条色带。
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

# --------------------------------------------------------------------------- #
# 语义调色板（Vibrant）：每个角色 = (浅填充, 饱和主色, 深文字)
# --------------------------------------------------------------------------- #
# 靛蓝学术配色 (IEEE 风) · 近双色 + 灰阶 + 暖橙点缀；白底、细线、低饱和、克制
# 主色靛蓝主导结构，暖橙仅作强调，其余语义色降饱和到学术色调（不再有糖果紫/品红）。
BLUE   = "#5B2C86"; BLUE_L   = "#ECE5F3"; BLUE_D   = "#3C1C5A"   # 主色 深清华紫：逻辑/信号/结构/标题
TEAL   = "#0D9488"; TEAL_L   = "#CCFBF1"; TEAL_D   = "#115E59"   # 存储/Macro（青绿）
AMBER  = "#EA580C"; AMBER_L  = "#FFEDD5"; AMBER_D  = "#9A3412"   # 电源/PG/强调（橙）
ROSE   = "#DC2626"; ROSE_L   = "#FEE2E2"; ROSE_D   = "#991B1B"   # IO/高亮/关键网（红，非粉）
VIOLET = "#2563EB"; VIOLET_L = "#DBEAFE"; VIOLET_D = "#1E3A8A"   # 时钟/特殊（蓝；主色让位给清华紫后腾出）

INK    = "#1A1F2B"   # 主文字
INK2   = "#3A4252"   # 次文字
MUTED  = "#6B7280"   # 脚注/弱化
LINE   = "#C7CDD6"   # 浅描边/网格
GRID   = "#E6E9EE"   # 更浅网格
SLATE_L = "#EDF0F4"  # 中性浅填充
WHITE  = "#FFFFFF"
PAPER  = "#FFFFFF"   # 图底色
SHADOW = "#1A1F2B"   # 投影基色（配合低 alpha）

# 角色 → (fill, edge, text)；node(variant='soft') 默认用之
ROLE = {
    "logic":   (BLUE_L,   BLUE,   BLUE_D),
    "memory":  (TEAL_L,   TEAL,   TEAL_D),
    "power":   (AMBER_L,  AMBER,  AMBER_D),
    "io":      (ROSE_L,   ROSE,   ROSE_D),
    "clock":   (VIOLET_L, VIOLET, VIOLET_D),
    "neutral": (SLATE_L,  "#94A3B8", INK),
    "ink":     ("#E2E8F0", INK,    INK),
}
MAIN = {"logic": BLUE, "memory": TEAL, "power": AMBER, "io": ROSE,
        "clock": VIOLET, "neutral": "#94A3B8", "ink": INK}

BYLINE = "整理 J.C · 源自 Digital VLSI Design (DVD), A. Teman, Bar-Ilan Univ."

# 字号层级（hierarchy）：主标签 > 次级 > 正文 > 脚注
FS_H1, FS_H2, FS_BODY, FS_CAP = 24, 19, 17, 15  # 调大：图被缩到 ~0.78 插入幻灯片，字号要够大才看得清
ASCII_RATIO = 0.6   # ASCII 字符相对 CJK 的近似宽度比；折行的单一真源（theme._wrap_w 与 deck._wrap 同用）


def setup_fonts():
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei", "Microsoft YaHei UI", "SimHei", "Segoe UI", "DejaVu Sans"]
    plt.rcParams["font.monospace"] = ["Consolas", "Cascadia Mono", "Courier New", "DejaVu Sans Mono"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["svg.fonttype"] = "none"


def canvas(w=16.0, h=9.0, dpi=200, bg=PAPER, grid=False):
    """新建画布。坐标系 0..w / 0..h，1 单位 = 1 英寸（等比）。"""
    setup_fonts()
    fig, ax = plt.subplots(figsize=(w, h), dpi=dpi)
    ax.set_xlim(0, w); ax.set_ylim(0, h)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_autoscale_on(False)  # 防止后续 plot/fill 改动坐标范围，破坏 1 单位=1 英寸
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.add_patch(Rectangle((0, 0), w, h, fc=bg, ec="none", zorder=-50))
    if grid:
        gx = 0.5
        while gx < w:
            ax.add_line(Line2D([gx, gx], [0, h], color=GRID, lw=0.5, zorder=-40)); gx += 0.5
        gy = 0.5
        while gy < h:
            ax.add_line(Line2D([0, w], [gy, gy], color=GRID, lw=0.5, zorder=-40)); gy += 0.5
    return fig, ax


def _shadow(alpha=0.16, blur=3):
    return [pe.withSimplePatchShadow(offset=(1.4, -1.6), shadow_rgbFace=SHADOW,
                                     alpha=alpha, rho=1.0)]


def node(ax, x, y, w, h, title, sub=None, role="logic", variant="soft",
         fs=17, sub_fs=13, rounding=0.12, lw=1.8, z=2, shadow=True,
         header=False, weight="bold"):
    """两段色圆角块。
    variant: soft(浅填充+饱和边+深字, 默认) / solid(饱和填充+白字) / outline(白底+饱和边)。
    header=True: 顶部加一条饱和色 header 条 + 白字标题（芯片式）。"""
    fill, edge, txt = ROLE[role]
    if variant == "solid":
        fc, ec, tc = MAIN[role], MAIN[role], WHITE
    elif variant == "outline":
        fc, ec, tc = WHITE, MAIN[role], txt
    else:
        fc, ec, tc = fill, MAIN[role], txt
    box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rounding}",
                         fc=fc, ec=ec, lw=lw, zorder=z)
    if shadow:
        box.set_path_effects(_shadow())
    ax.add_patch(box)
    cx, cy = x + w / 2.0, y + h / 2.0
    if header:
        hh = min(0.42, h * 0.32)
        ax.add_patch(FancyBboxPatch((x, y + h - hh), w, hh,
                     boxstyle=f"round,pad=0,rounding_size={rounding}",
                     fc=MAIN[role], ec="none", zorder=z + 1))
        ax.add_patch(Rectangle((x, y + h - hh), w, hh * 0.5, fc=MAIN[role], ec="none", zorder=z + 1))
        ax.text(cx, y + h - hh / 2.0, title, ha="center", va="center", color=WHITE,
                fontsize=fs * 0.86, fontweight="bold", zorder=z + 2)
        if sub:
            ax.text(cx, y + (h - hh) / 2.0, sub, ha="center", va="center", color=txt,
                    fontsize=sub_fs, zorder=z + 2)
        return _anchors(x, y, w, h)
    if sub:
        ax.text(cx, cy + h * 0.15, title, ha="center", va="center", color=tc,
                fontsize=fs, fontweight=weight, zorder=z + 2)
        ax.text(cx, cy - h * 0.22, sub, ha="center", va="center", color=tc,
                fontsize=sub_fs, zorder=z + 2)
    else:
        ax.text(cx, cy, title, ha="center", va="center", color=tc,
                fontsize=fs, fontweight=weight, zorder=z + 2)
    return _anchors(x, y, w, h)


def _anchors(x, y, w, h):
    cx, cy = x + w / 2.0, y + h / 2.0
    return dict(x=x, y=y, w=w, h=h, cx=cx, cy=cy,
                top=(cx, y + h), bottom=(cx, y), left=(x, cy), right=(x + w, cy),
                tl=(x, y + h), tr=(x + w, y + h), bl=(x, y), br=(x + w, y))


def rect(ax, x, y, w, h, fc="none", ec=LINE, lw=1.5, z=1, ls="-", hatch=None,
         rounding=None, alpha=1.0, shadow=False):
    if rounding:
        p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rounding}",
                           fc=fc, ec=ec, lw=lw, ls=ls, zorder=z, alpha=alpha)
    else:
        p = Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, ls=ls, zorder=z, alpha=alpha, hatch=hatch)
    if shadow:
        p.set_path_effects(_shadow())
    ax.add_patch(p)
    return p


def line(ax, x0, y0, x1, y1, color=INK2, lw=2.0, z=2, ls="-", cap="round"):
    ax.add_line(Line2D([x0, x1], [y0, y1], color=color, lw=lw, zorder=z, ls=ls,
                       solid_capstyle=cap))


def arrow(ax, p0, p1, color=INK2, lw=2.2, z=3, style="-|>", rad=0.0, ls="-", scale=15):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=scale, lw=lw,
                 color=color, connectionstyle=f"arc3,rad={rad}", zorder=z, linestyle=ls,
                 shrinkA=3, shrinkB=3, capstyle="round"))


def heading(ax, text, sub=None, x=0.55, top=None, role="logic"):
    """图标题：小色块 + 粗墨色标题(+ 灰副标题)。"""
    if top is None:
        top = ax.get_ylim()[1] - 0.6
    ax.add_patch(FancyBboxPatch((x, top - 0.16), 0.34, 0.34,
                 boxstyle="round,pad=0,rounding_size=0.07", fc=MAIN[role], ec="none", zorder=5))
    ax.text(x + 0.56, top + 0.02, text, ha="left", va="center", color=INK,
            fontsize=24, fontweight="bold", zorder=5)
    if sub:
        ax.text(x + 0.57, top - 0.5, sub, ha="left", va="center", color=MUTED,
                fontsize=15, zorder=5)


def caption(ax, text=BYLINE, x=None, y=0.42):
    if x is None:
        x = ax.get_xlim()[1] - 0.45
    ax.text(x, y, text, ha="right", va="center", color=MUTED, fontsize=11, zorder=5)


def plate(ax, pad=0.16, ec=LINE, lw=1.4):
    """给整张图加一圈极浅的"图版"边框（论文插图感），并占满画布。"""
    w, h = ax.get_xlim()[1], ax.get_ylim()[1]
    ax.add_patch(FancyBboxPatch((pad, pad), w - 2 * pad, h - 2 * pad,
                 boxstyle="round,pad=0,rounding_size=0.12", fc="none", ec=ec, lw=lw, zorder=-10))


def ftitle(ax, text, x=0.5, y=None, role="logic", fs=22):
    """图内小标题（可选）。教案里多数图不用，标题交给幻灯片。"""
    if y is None:
        y = ax.get_ylim()[1] - 0.55
    ax.add_patch(FancyBboxPatch((x, y - 0.16), 0.34, 0.34,
                 boxstyle="round,pad=0,rounding_size=0.07", fc=MAIN[role], ec="none", zorder=5))
    ax.text(x + 0.54, y, text, ha="left", va="center", color=INK, fontsize=fs, fontweight="bold", zorder=5)


def tag(ax, x, y, text, role="io", fs=13, ha="center"):
    fill, edge, txt = ROLE[role]
    ax.text(x, y, text, ha=ha, va="center", color=txt, fontsize=fs, fontweight="bold", zorder=6,
            bbox=dict(boxstyle="round,pad=0.32", fc=fill, ec=edge, lw=1.3))


def legend(ax, items, x, y, fs=13, dy=0.46, swatch=0.24):
    """语义色图例。items=[(role_or_color, label), ...]。"""
    yy = y
    for role_or_color, label in items:
        c = MAIN.get(role_or_color, role_or_color)
        ax.add_patch(FancyBboxPatch((x, yy - swatch / 2), swatch, swatch,
                     boxstyle="round,pad=0,rounding_size=0.04", fc=c, ec="none", zorder=6))
        ax.text(x + swatch + 0.16, yy, label, ha="left", va="center", color=INK2, fontsize=fs, zorder=6)
        yy -= dy


def annotate(ax, xy, xytext, text, color=INK2, fs=13, rad=-0.18, ha="left", lw=1.3):
    """带引线的标注。"""
    ax.add_patch(FancyArrowPatch(xytext, xy, arrowstyle="-", mutation_scale=10, lw=lw,
                 color=color, connectionstyle=f"arc3,rad={rad}", zorder=6, shrinkA=2, shrinkB=2))
    ax.text(xytext[0], xytext[1], text, ha=ha, va="center", color=color, fontsize=fs, zorder=6)


def bracket(ax, x0, x1, y, text, color=INK2, depth=0.3, fs=15, down=True):
    yy = y - depth if down else y + depth
    line(ax, x0, y, x0, yy, color=color, lw=1.8)
    line(ax, x1, y, x1, yy, color=color, lw=1.8)
    line(ax, x0, yy, x1, yy, color=color, lw=1.8)
    ty = yy - 0.32 if down else yy + 0.32
    ax.text((x0 + x1) / 2.0, ty, text, ha="center", va="center", color=color, fontsize=fs, fontweight="bold")


def flow(ax, items, y, x0, x1, h=1.7, gap=0.32, fs=13.5, sub_fs=9.5, z=2,
         arrow_color=INK2, variant="soft"):
    """横向流程。items=[(title, sub, role), ...]。返回锚点列表。"""
    n = len(items)
    w = (x1 - x0 - gap * (n - 1)) / n
    nodes, x = [], x0
    for (title, sub, role) in items:
        nodes.append(node(ax, x, y, w, h, title, sub=sub, role=role, variant=variant,
                          fs=fs, sub_fs=sub_fs, z=z))
        x += w + gap
    for a, b in zip(nodes[:-1], nodes[1:]):
        arrow(ax, a["right"], b["left"], color=arrow_color, lw=2.4)
    return nodes


# --------------------------------------------------------------------------- #
# 参考信息图风格图元（卡片 / chevron 流程 / 分节标题）—— 柔和、留白克制、层级分明
# --------------------------------------------------------------------------- #
SOFT = {  # 各角色的浅卡片底色（取各色 _L 浅调，纯色不透明，不靠 alpha）
    "logic": "#DBEAFE", "memory": "#CCFBF1", "power": "#FFEDD5",
    "io": "#FEE2E2", "clock": "#EDE9FE", "neutral": "#EEF1F5",
}
CARD_EDGE = "#CBD2DC"


def _wrap_w(s, width_in, fs):
    """按卡片可用宽度(英寸)折行：CJK≈1em、ASCII≈0.6em（em = fs/72 英寸）。防横向溢出。
    连续 ASCII 字母/数字聚成"词"整体折行，不拆词（避免 mesh→m/esh 这类断裂）。"""
    em = fs / 72.0
    toks, i, n = [], 0, len(s)
    while i < n:                       # 分词：ASCII 字母数字成块，其余逐字符
        if s[i].isascii() and s[i].isalnum():
            j = i + 1
            while j < n and s[j].isascii() and s[j].isalnum():
                j += 1
            toks.append(s[i:j]); i = j
        else:
            toks.append(s[i]); i += 1
    out, line, used = [], "", 0.0
    for t in toks:
        tw = sum(em * (ASCII_RATIO if ord(c) < 128 else 1.0) for c in t)
        if used + tw > width_in and line:
            out.append(line.rstrip()); line, used = t.lstrip(), tw
        else:
            line += t; used += tw
    if line.strip():
        out.append(line.rstrip())
    return out or [""]


def infocard(ax, x, y, w, h, title, detail=None, role="neutral", highlight=False,
             title_fs=17, detail_fs=14, z=2, pad_x=0.3):
    """参考图的核心卡片：浅色底 + 粗体深色标题 + 该色系细节行。
    标题/细节按卡宽**折行**（防横向溢出），作为一组在卡内**垂直居中、行间留足行距**
    （≈1.32 倍行高，杜绝 0 行距重叠）；整组超高时**等比缩字号**塞下（防纵向溢出）。"""
    ec = MAIN[role] if highlight else CARD_EDGE
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.1",
                 fc=SOFT[role], ec=ec, lw=2.6 if highlight else 1.4, zorder=z))
    inner = w - 2 * pad_x
    tlines = _wrap_w(title, inner, title_fs)
    dlines = _wrap_w(detail, inner, detail_fs) if detail else []
    th = title_fs / 72.0 * 1.32          # 标题单行行高（含行距）
    dh = detail_fs / 72.0 * 1.32         # 细节单行行高
    gap = 0.16 if detail else 0.0        # 标题与细节之间额外间距
    block = th * len(tlines) + gap + dh * len(dlines)
    avail = h - 0.16
    if block > avail and block > 0:       # 竖向放不下 → 等比缩字号
        sc = avail / block
        th *= sc; dh *= sc; gap *= sc; title_fs *= sc; detail_fs *= sc; block = avail
    yy = y + h / 2.0 + block / 2.0        # 组顶（va=top，逐行下移）
    for ln in tlines:
        ax.text(x + pad_x, yy, ln, ha="left", va="top", color=INK,
                fontsize=title_fs, fontweight="bold", zorder=z + 1)
        yy -= th
    if detail:
        yy -= gap
        for ln in dlines:
            ax.text(x + pad_x, yy, ln, ha="left", va="top", color=ROLE[role][2],
                    fontsize=detail_fs, zorder=z + 1)
            yy -= dh
    return dict(x=x, y=y, w=w, h=h, cx=x + w / 2, cy=y + h / 2,
                right=(x + w, y + h / 2), left=(x, y + h / 2), top=(x + w / 2, y + h), bottom=(x + w / 2, y))


def chevron(ax, x, y, color=MUTED, size=20):
    ax.text(x, y, "›", ha="center", va="center", color=color, fontsize=size, fontweight="bold", zorder=4)


def flowrow(ax, items, y, x0, x1, h, gap=0.55, title_fs=16, sub_fs=12.5):
    """chevron 横向流程：items=[(主, 次, role, highlight), …]，框之间用 › 分隔。返回锚点。"""
    n = len(items)
    w = (x1 - x0 - gap * (n - 1)) / n
    nodes, x = [], x0
    for (main, sub, role, hl) in items:
        ec = MAIN[role] if hl else CARD_EDGE
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.1",
                     fc=(SOFT[role] if hl else "#F8F9FB"), ec=ec, lw=2.4 if hl else 1.4, zorder=2))
        tc = MAIN[role] if hl else INK
        cx, cy = x + w / 2, y + h / 2
        if sub:
            ax.text(cx, cy + 0.22, main, ha="center", va="center", color=tc, fontsize=title_fs, fontweight="bold", zorder=3)
            ax.text(cx, cy - 0.28, sub, ha="center", va="center", color=(MAIN[role] if hl else MUTED), fontsize=sub_fs, zorder=3)
        else:
            ax.text(cx, cy, main, ha="center", va="center", color=tc, fontsize=title_fs, fontweight="bold", zorder=3)
        nodes.append(dict(x=x, y=y, w=w, h=h, cx=cx, cy=cy, right=(x + w, cy), left=(x, cy)))
        x += w + gap
    for a, b in zip(nodes[:-1], nodes[1:]):
        chevron(ax, (a["right"][0] + b["left"][0]) / 2, a["cy"], size=18)
    return nodes


def sechead(ax, x, y, num, text, color=None):
    """分节标题：带圈数字 + 粗体（如 “① 标题”）。"""
    color = color or INK
    ax.text(x, y, f"{num}", ha="left", va="center", color=VIOLET, fontsize=FS_H2 + 2, fontweight="bold", zorder=5)
    ax.text(x + 0.42, y, text, ha="left", va="center", color=color, fontsize=FS_H2, fontweight="bold", zorder=5)


def save(fig, outdir, name, png=True, svg=True, dpi=None):
    os.makedirs(outdir, exist_ok=True)
    out_png = os.path.join(outdir, name + ".png")
    if png:
        fig.savefig(out_png, dpi=dpi or fig.dpi, bbox_inches="tight", pad_inches=0.08,
                    facecolor=PAPER)
    if svg:
        fig.savefig(os.path.join(outdir, name + ".svg"), bbox_inches="tight", pad_inches=0.08,
                    facecolor=PAPER)
    plt.close(fig)
    return out_png
