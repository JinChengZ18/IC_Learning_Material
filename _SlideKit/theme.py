# -*- coding: utf-8 -*-
"""
_SlideKit · theme.py  (v2 · Vibrant Semantic)
=============================================
论文/图书级 IC 插图主题。配色**重置**为现代多色「语义」方案——
不同功能用不同色相，最大化元素辨识度（电蓝=逻辑/信号，青绿=存储/Macro，
琥珀=电源/PG，品红=IO/高亮，紫=时钟，石板灰=衬底/中性）。

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
BLUE   = "#2563EB"; BLUE_L   = "#DBEAFE"; BLUE_D   = "#1E3A8A"
TEAL   = "#14B8A6"; TEAL_L   = "#CCFBF1"; TEAL_D   = "#0F766E"
AMBER  = "#F59E0B"; AMBER_L  = "#FEF3C7"; AMBER_D  = "#92400E"
ROSE   = "#DB2777"; ROSE_L   = "#FCE7F3"; ROSE_D   = "#9D174D"   # 品红 / IO / 高亮
VIOLET = "#7C3AED"; VIOLET_L = "#EDE9FE"; VIOLET_D = "#5B21B6"   # 时钟 / 特殊

INK    = "#1E293B"   # 主文字（墨色）
INK2   = "#475569"   # 次文字
MUTED  = "#64748B"   # 脚注/弱化
LINE   = "#CBD5E1"   # 浅描边/网格
GRID   = "#E2E8F0"   # 更浅网格
SLATE_L = "#F1F5F9"  # 中性浅填充
WHITE  = "#FFFFFF"
PAPER  = "#FFFFFF"   # 图底色
SHADOW = "#0F172A"   # 投影基色（配合低 alpha）

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


def setup_fonts():
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei", "Microsoft YaHei UI", "SimHei", "Segoe UI", "DejaVu Sans"]
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
         fs=15, sub_fs=10.5, rounding=0.12, lw=1.8, z=2, shadow=True,
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
                fontsize=sub_fs, zorder=z + 2, alpha=0.92)
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
            fontsize=21, fontweight="bold", zorder=5)
    if sub:
        ax.text(x + 0.57, top - 0.5, sub, ha="left", va="center", color=MUTED,
                fontsize=12, zorder=5)


def caption(ax, text=BYLINE, x=None, y=0.42):
    if x is None:
        x = ax.get_xlim()[1] - 0.45
    ax.text(x, y, text, ha="right", va="center", color=MUTED, fontsize=8.5, zorder=5)


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


def tag(ax, x, y, text, role="io", fs=10, ha="center"):
    fill, edge, txt = ROLE[role]
    ax.text(x, y, text, ha=ha, va="center", color=txt, fontsize=fs, fontweight="bold", zorder=6,
            bbox=dict(boxstyle="round,pad=0.32", fc=fill, ec=edge, lw=1.3))


def legend(ax, items, x, y, fs=10.5, dy=0.42, swatch=0.20):
    """语义色图例。items=[(role_or_color, label), ...]。"""
    yy = y
    for role_or_color, label in items:
        c = MAIN.get(role_or_color, role_or_color)
        ax.add_patch(FancyBboxPatch((x, yy - swatch / 2), swatch, swatch,
                     boxstyle="round,pad=0,rounding_size=0.04", fc=c, ec="none", zorder=6))
        ax.text(x + swatch + 0.16, yy, label, ha="left", va="center", color=INK2, fontsize=fs, zorder=6)
        yy -= dy


def annotate(ax, xy, xytext, text, color=INK2, fs=10.5, rad=-0.18, ha="left", lw=1.3):
    """带引线的标注。"""
    ax.add_patch(FancyArrowPatch(xytext, xy, arrowstyle="-", mutation_scale=10, lw=lw,
                 color=color, connectionstyle=f"arc3,rad={rad}", zorder=6, shrinkA=2, shrinkB=2))
    ax.text(xytext[0], xytext[1], text, ha=ha, va="center", color=color, fontsize=fs, zorder=6)


def bracket(ax, x0, x1, y, text, color=INK2, depth=0.3, fs=12, down=True):
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
