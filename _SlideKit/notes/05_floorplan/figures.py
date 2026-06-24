# -*- coding: utf-8 -*-
"""
notes/05_floorplan/figures.py  (v5 · 4:3 侧插图)
===============================================
Floorplan 主题插图，图幅统一为 ~4:3 / 1:1，便于作为 16:9 幻灯片右栏侧插图。
风格：无外框、字号分层(FS_H1>H2>BODY>CAP)、卡片/图示混排、填满画面。
运行：python notes/05_floorplan/figures.py → ../../../IC_Backend_Notes/assets/floorplan/
"""
import os
import sys

_SK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # _SlideKit 根
sys.path.insert(0, _SK)
import theme as T  # noqa: E402
from matplotlib.patches import Circle as _Circle  # noqa: E402

OUT = os.path.abspath(os.path.join(_SK, "..", "IC_Backend_Notes", "assets", "floorplan"))
H1, H2, BODY, CAP = T.FS_H1, T.FS_H2, T.FS_BODY, T.FS_CAP


def _hx(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def lerp(c1, c2, t):
    a, b = _hx(c1), _hx(c2)
    return "#%02X%02X%02X" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# F01 流程定位（4:3）------------------------------------------------------- #
def f01_position():
    fig, ax = T.canvas(9, 6.8)
    ax.text(0.4, 6.4, "Floorplan 在 PnR 流程中的位置", ha="left", va="center", color=T.INK, fontsize=H2, fontweight="bold")
    items = [("逻辑综合", "Synth", "neutral", False), ("布图规划", "Floorplan", "clock", True),
             ("布局", "Place", "neutral", False), ("时钟树", "CTS", "neutral", False), ("布线", "Route", "neutral", False)]
    T.flowrow(ax, items, y=4.5, x0=0.4, x1=8.6, h=1.4, gap=0.42, title_fs=BODY + 1, sub_fs=12.5)
    ax.text(0.4, 3.85, "Floorplan 主要任务", ha="left", va="center", color=T.INK, fontsize=BODY, fontweight="bold")
    tasks = ["① die / core 几何", "② 宏摆放 & 朝向", "③ 电源规划 PG", "④ 多电压 / blockage"]
    for i, t in enumerate(tasks):
        x = 0.4 + (i % 2) * 4.25
        y = 2.45 - (i // 2) * 1.3
        T.infocard(ax, x, y, 4.0, 1.1, t, role="clock", title_fs=BODY)
    return T.save(fig, OUT, "f01_position")


# F03 芯片几何（~1:1）----------------------------------------------------- #
def _pads(ax, x, y, s, n, dep, gap=0.12):
    plh = (s - gap * (n + 1)) / n
    for i in range(n):
        p = x + gap + i * (plh + gap)
        T.rect(ax, p, y, plh, dep, fc=T.ROSE_L, ec=T.ROSE, lw=1.0, z=3)
        T.rect(ax, p, y + s - dep, plh, dep, fc=T.ROSE_L, ec=T.ROSE, lw=1.0, z=3)
    plv = (s - 2 * dep - gap * (n + 1)) / n
    for i in range(n):
        q = y + dep + gap + i * (plv + gap)
        T.rect(ax, x, q, dep, plv, fc=T.ROSE_L, ec=T.ROSE, lw=1.0, z=3)
        T.rect(ax, x + s - dep, q, dep, plv, fc=T.ROSE_L, ec=T.ROSE, lw=1.0, z=3)


def f03_geometry():
    fig, ax = T.canvas(8.6, 7)
    dx, dy, s = 0.5, 0.6, 5.0
    T.rect(ax, dx, dy, s, s, fc=T.WHITE, ec=T.INK2, lw=2.2, z=1, shadow=True)
    dep = 0.36
    _pads(ax, dx, dy, s, 8, dep)
    inset = dep + 0.45
    cx, cy, cs = dx + inset, dy + inset, s - 2 * inset
    T.rect(ax, cx, cy, cs, cs, fc=T.BLUE_L, ec=T.BLUE, lw=1.6, z=2)
    ry = cy + 0.3
    while ry < cy + cs - 0.18:
        T.line(ax, cx + 0.18, ry, cx + cs - 0.18, ry, color=T.BLUE, lw=0.6, z=3); ry += 0.38
    ax.text(cx + cs / 2, cy + cs - 0.38, "Core", ha="center", color=T.BLUE_D, fontsize=H2, fontweight="bold", zorder=5)
    ax.text(dx + 0.1, dy + s + 0.06, "Die", ha="left", va="bottom", color=T.INK, fontsize=H2, fontweight="bold")
    lx = dx + s + 0.45
    items = [("Die 边界", "含 scribe 切割道", "neutral"), ("I/O Pad", "焊盘环", "io"),
             ("Core 核心区", "标准单元 + 宏", "logic"), ("Core Rows", "标准单元行", "logic")]
    for i, (t, d, role) in enumerate(items):
        T.infocard(ax, lx, 5.5 - i * 1.15, 2.35, 1.0, t, d, role=role, title_fs=BODY, detail_fs=CAP - 1)
    ax.text(0.5, 0.18, "利用率 = (Σ单元+Σ宏)/Core ≈ 0.5–0.8   ·   长宽比 H/W ≈ 1 最均衡", ha="left", color=T.MUTED, fontsize=CAP - 0.5)
    return T.save(fig, OUT, "f03_geometry")


# F06 宏摆放原则（4:3）---------------------------------------------------- #
def f06_macro():
    fig, ax = T.canvas(9.4, 6.8)
    cx, cy, cw, ch = 0.4, 0.5, 4.7, 5.8
    T.rect(ax, cx, cy, cw, ch, fc=T.WHITE, ec=T.INK2, lw=1.8, z=1)
    T.rect(ax, cx + 0.2, cy + 0.2, cw - 0.4, ch - 0.4, fc=T.BLUE_L, ec="none", z=1)
    ax.text(cx + cw * 0.5, cy + ch * 0.42, "Std-Cell\nRegion", ha="center", va="center", color=T.BLUE_D, fontsize=BODY, fontweight="bold", zorder=2)
    m1 = T.node(ax, cx + 0.3, cy + ch - 1.9, 1.85, 1.6, "SRAM", role="memory", z=4, fs=BODY)
    m2 = T.node(ax, cx + cw - 2.15, cy + ch - 1.9, 1.85, 1.6, "SRAM", role="memory", z=4, fs=BODY)
    T.node(ax, cx + 0.3, cy + 0.3, 1.7, 1.3, "PLL", role="memory", variant="outline", z=4, fs=BODY)
    for m in (m1, m2):
        for k in range(4):
            px = m["x"] + 0.3 + k * (m["w"] - 0.6) / 3
            T.rect(ax, px - 0.05, m["y"] - 0.03, 0.1, 0.14, fc=T.ROSE, ec="none", z=5)
    for dyf in (0.3, 0.7, 1.1):
        T.line(ax, m1["x"] + m1["w"], m1["y"] + dyf, cx + cw * 0.5, cy + ch * 0.42, color=T.TEAL, lw=0.9, ls=(0, (3, 3)), z=3)
    T.tag(ax, (m1["x"] + m1["w"] + m2["x"]) / 2, cy + ch - 1.05, "channel", role="io", fs=CAP - 1)
    px = cx + cw + 0.4
    cards = [("① 沿边 / 沿角", "memory"), ("② 引脚朝 core", "io"), ("③ 按数据流就近", "clock"),
             ("④ 对称背靠背", "power"), ("⑤ 留 channel", "neutral")]
    for i, (t, role) in enumerate(cards):
        T.infocard(ax, px, 5.55 - i * 1.16, 9.4 - px - 0.3, 0.98, t, role=role, title_fs=BODY)
    return T.save(fig, OUT, "f06_macro")


# F07 channel / halo / blockage（4:3）------------------------------------- #
def f07_halo():
    fig, ax = T.canvas(8.6, 6.4)
    cx, cy, cw, ch = 0.4, 0.4, 7.8, 5.0
    T.rect(ax, cx, cy, cw, ch, fc=T.WHITE, ec=T.INK2, lw=1.8, z=1)
    m1 = T.node(ax, cx + 0.6, cy + 1.2, 2.3, 3.2, "Macro A", role="memory", z=4, fs=H2)
    m2 = T.node(ax, cx + 4.9, cy + 1.2, 2.3, 3.2, "Macro B", role="memory", z=4, fs=H2)
    T.rect(ax, m1["x"] - 0.28, m1["y"] - 0.28, m1["w"] + 0.56, m1["h"] + 0.56, fc="none", ec=T.ROSE, lw=1.7, ls=(0, (5, 3)), z=4)
    T.tag(ax, m1["cx"], m1["y"] - 0.55, "halo / keepout", role="io", fs=CAP)
    chx0, chx1 = m1["x"] + m1["w"] + 0.3, m2["x"] - 0.3
    for k in range(7):
        xx = chx0 + (k + 1) * (chx1 - chx0) / 8
        T.line(ax, xx, cy + 1.3, xx, cy + 4.5, color=T.TEAL, lw=1.1, z=3)
    T.tag(ax, (chx0 + chx1) / 2, cy + 4.75, "channel", role="memory", fs=CAP)
    T.rect(ax, cx + cw - 2.2, cy + 0.3, 1.9, 1.0, fc=T.SLATE_L, ec=T.MUTED, lw=1.2, hatch="////", z=3)
    ax.text(cx + cw - 1.25, cy + 0.8, "blockage", ha="center", va="center", color=T.INK2, fontsize=CAP)
    ax.text(0.4, 6.0, "channel 走线 · halo 防贴死 · blockage 控密度", ha="left", color=T.INK2, fontsize=BODY, fontweight="bold")
    return T.save(fig, OUT, "f07_halo")


# F09 IR drop 与 EM（4:3）------------------------------------------------- #
def f09_irem():
    fig, ax = T.canvas(9.4, 6.6)
    gx, gy, gs, n = 0.6, 1.6, 4.0, 8
    cell = gs / n
    ramp = ["#16A34A", "#65A30D", "#CA8A04", "#EA580C", "#DC2626"]
    for r in range(n):
        for c in range(n):
            tt = (r / (n - 1)) * (len(ramp) - 1)
            i0 = int(tt)
            col = lerp(ramp[i0], ramp[min(i0 + 1, len(ramp) - 1)], tt - i0)
            T.rect(ax, gx + c * cell, gy + (n - 1 - r) * cell, cell, cell, fc=col, ec=T.WHITE, lw=0.6, z=2)
    for c in range(n):
        T.rect(ax, gx + c * cell + 0.05, gy + gs + 0.05, cell - 0.1, 0.22, fc=T.AMBER, ec=T.AMBER_D, lw=0.8, z=3)
    ax.text(gx + gs / 2, gy + gs + 0.55, "电源 pad（供电边）", ha="center", color=T.AMBER_D, fontsize=BODY, fontweight="bold")
    ax.text(gx + gs / 2, gy - 0.38, "ΔV = I·R  离电源越远压降越大", ha="center", color=T.INK, fontsize=CAP, fontweight="bold")
    lx = gx + gs + 0.25
    for i, col in enumerate(ramp):
        T.rect(ax, lx, gy + gs - 0.15 - i * 0.45, 0.26, 0.45, fc=col, ec="none", z=3)
    ax.text(lx + 0.36, gy + gs, "高", ha="left", va="center", color=T.INK2, fontsize=CAP - 1)
    ax.text(lx + 0.36, gy - 0.05, "低", ha="left", va="center", color=T.INK2, fontsize=CAP - 1)
    ex = 5.5
    ax.text(ex, gy + gs + 0.55, "电迁移 EM", ha="left", color=T.ROSE_D, fontsize=H2, fontweight="bold")
    T.rect(ax, ex, gy + 2.9, 3.6, 0.75, fc=T.SLATE_L, ec=T.INK2, lw=1.4, z=2)
    for k in range(4):
        T.arrow(ax, (ex + 0.45 + k * 0.85, gy + 3.27), (ex + 0.9 + k * 0.85, gy + 3.27), color=T.ROSE, lw=2.2, scale=12)
    ax.text(ex, gy + 2.55, "J 过大 → 金属原子迁移 → 断/短路", ha="left", color=T.INK2, fontsize=CAP)
    T.infocard(ax, ex, gy + 0.7, 3.6, 1.4, "缓解", "加宽金属 / 多 via / 更密 mesh → 降低 J", role="memory", title_fs=BODY, detail_fs=CAP)
    return T.save(fig, OUT, "f09_irem")


# F12 输入 / 输出（~1:1，纵向）-------------------------------------------- #
def f12_io():
    fig, ax = T.canvas(7.6, 7)
    ins = ["Netlist (.v)", "LEF", "Liberty (.lib)", "SDC", "UPF", "Partition / 预算"]
    for i, label in enumerate(ins):
        x = 0.4 + (i % 2) * 2.0
        y = 6.0 - (i // 2) * 0.95
        T.node(ax, x, y - 0.78, 1.85, 0.78, label, role="neutral", fs=CAP - 0.5, z=3, shadow=False)
    eng = T.node(ax, 4.7, 4.0, 2.6, 1.6, "Floorplan", sub="ICC2 / Innovus", role="logic", variant="solid", z=4, fs=H2, sub_fs=CAP)
    outs = [("DEF：宏 + PG + blockage", "memory"), ("Floorplan DB (NDM/OA)", "memory"), ("可布线性 / 时序初评", "io")]
    for i, (label, role) in enumerate(outs):
        T.infocard(ax, 0.4, 2.4 - i * 0.92, 6.9, 0.78, label, role=role, title_fs=CAP)
    T.arrow(ax, (3.3, 4.0), eng["left"], color=T.LINE, lw=1.6, scale=12)
    T.arrow(ax, eng["bottom"], (3.85, 2.95), color=T.INK2, lw=2.0, rad=-0.1)
    return T.save(fig, OUT, "f12_io")


# F15 Floorplan 迭代闭环（~1:1）------------------------------------------ #
def f15_loop():
    fig, ax = T.canvas(7.4, 6.6)
    n1 = T.node(ax, 2.4, 5.0, 2.6, 1.1, "Floorplan", sub="定 die/macro/PG", role="logic", z=4, fs=H2, sub_fs=CAP)
    n2 = T.node(ax, 4.9, 2.7, 2.4, 1.1, "试布局 + GR", role="memory", z=4, fs=BODY)
    n3 = T.node(ax, 2.4, 0.4, 2.6, 1.1, "评估", sub="拥塞 / 时序 / IR", role="io", z=4, fs=H2, sub_fs=CAP)
    n4 = T.node(ax, 0.1, 2.7, 2.4, 1.1, "回退调整", role="power", z=4, fs=BODY)
    T.arrow(ax, n1["right"], n2["top"], color=T.INK2, lw=2.2, rad=-0.35)
    T.arrow(ax, n2["bottom"], n3["right"], color=T.INK2, lw=2.2, rad=-0.35)
    T.arrow(ax, n3["left"], n4["bottom"], color=T.INK2, lw=2.2, rad=-0.35)
    T.arrow(ax, n4["top"], n1["left"], color=T.INK2, lw=2.2, rad=-0.35)
    ax.text(3.7, 3.25, "迭代\n闭环", ha="center", va="center", color=T.MUTED, fontsize=BODY, fontweight="bold")
    ax.text(3.7, 6.35, "收敛后才进详细 Placement", ha="center", color=T.INK, fontsize=BODY, fontweight="bold")
    return T.save(fig, OUT, "f15_loop")


# F16 网表唯一化（4:3）--------------------------------------------------- #
def f16_uniquify():
    fig, ax = T.canvas(9.4, 6.2)
    ax.text(0.4, 5.85, "唯一化：每个子模块只被引用一次", ha="left", va="center", color=T.INK, fontsize=H2, fontweight="bold")

    def tree(x0, shared, title, role_t):
        ax.text(x0 + 1.75, 5.05, title, ha="center", color=role_t, fontsize=BODY, fontweight="bold")
        top = T.node(ax, x0 + 0.95, 3.95, 1.6, 0.72, "top", role="neutral", fs=BODY)
        m1 = T.node(ax, x0 - 0.05, 2.75, 1.5, 0.72, "m1", role="logic", fs=BODY)
        m2 = T.node(ax, x0 + 2.05, 2.75, 1.5, 0.72, "m2", role="logic", fs=BODY)
        T.arrow(ax, top["bottom"], m1["top"], color=T.INK2, lw=1.8, scale=11)
        T.arrow(ax, top["bottom"], m2["top"], color=T.INK2, lw=1.8, scale=11)
        if shared:
            am = T.node(ax, x0 + 0.95, 1.55, 1.6, 0.72, "amod", role="memory", fs=BODY)
            u = T.node(ax, x0 + 0.95, 0.45, 1.6, 0.72, "u1·BUFFD1", role="io", fs=CAP)
            T.arrow(ax, m1["bottom"], am["top"], color=T.ROSE, lw=1.8, scale=11)
            T.arrow(ax, m2["bottom"], am["top"], color=T.ROSE, lw=1.8, scale=11)
            T.arrow(ax, am["bottom"], u["top"], color=T.INK2, lw=1.8, scale=11)
        else:
            a1 = T.node(ax, x0 - 0.05, 1.55, 1.5, 0.72, "amod1", role="memory", fs=CAP)
            a2 = T.node(ax, x0 + 2.05, 1.55, 1.5, 0.72, "amod2", role="memory", fs=CAP)
            u1 = T.node(ax, x0 - 0.05, 0.45, 1.5, 0.72, "u1", role="io", fs=CAP)
            u2 = T.node(ax, x0 + 2.05, 0.45, 1.5, 0.72, "u1", role="io", fs=CAP)
            T.arrow(ax, m1["bottom"], a1["top"], color=T.INK2, lw=1.8, scale=11)
            T.arrow(ax, m2["bottom"], a2["top"], color=T.INK2, lw=1.8, scale=11)
            T.arrow(ax, a1["bottom"], u1["top"], color=T.INK2, lw=1.8, scale=11)
            T.arrow(ax, a2["bottom"], u2["top"], color=T.INK2, lw=1.8, scale=11)

    tree(0.4, True, "非唯一：m1/m2 共享 amod", T.ROSE_D)
    tree(5.3, False, "唯一化：各自独立副本", T.TEAL_D)
    T.line(ax, 4.85, 0.3, 4.85, 5.0, color=T.LINE, lw=1.2, ls=(0, (3, 3)))
    ax.text(2.15, 0.02, "改 m1/u1 会牵连 m2/u1（不可独立优化）", ha="center", color=T.ROSE_D, fontsize=CAP - 0.5)
    ax.text(7.05, 0.02, "各实例可独立优化、移动", ha="center", color=T.TEAL_D, fontsize=CAP - 0.5)
    return T.save(fig, OUT, "f16_uniquify")


# F17 扁平 vs 层次化（4:3）------------------------------------------------ #
def f17_hier():
    fig, ax = T.canvas(9.4, 6.0)
    ax.text(2.35, 5.55, "扁平 Flat", ha="center", color=T.BLUE_D, fontsize=H2, fontweight="bold")
    T.rect(ax, 0.5, 1.4, 3.7, 3.7, fc=T.WHITE, ec=T.INK2, lw=1.8, z=1)
    T.node(ax, 1.15, 2.55, 2.4, 1.4, "整颗芯片\n一次 P&R", role="logic", fs=BODY, z=3)
    ax.text(2.35, 1.75, "运行慢 / 内存大", ha="center", color=T.MUTED, fontsize=CAP)
    ax.text(7.0, 5.55, "层次化 Hierarchical", ha="center", color=T.TEAL_D, fontsize=H2, fontweight="bold")
    T.rect(ax, 5.0, 1.4, 4.0, 3.7, fc=T.WHITE, ec=T.INK2, lw=1.8, z=1)
    top = T.node(ax, 6.35, 4.15, 1.5, 0.7, "Top 集成", role="neutral", fs=CAP, z=4)
    blks = []
    for i in range(3):
        b = T.node(ax, 5.2 + i * 1.28, 2.75, 1.12, 0.95, f"Blk{i+1}", role="memory", fs=CAP, z=3)
        blks.append(b)
        T.arrow(ax, b["top"], top["bottom"], color=T.INK2, lw=1.4, scale=9)
        ax.text(b["cx"], b["y"] - 0.28, "P&R", ha="center", color=T.MUTED, fontsize=CAP - 2)
    ax.text(7.0, 1.75, "并行 / 复用，但需 ILM、引脚、预算", ha="center", color=T.MUTED, fontsize=CAP)
    T.infocard(ax, 0.5, 0.25, 8.5, 0.9, "取舍",
               "层次化省运行时间与内存、利于复用，但全芯片时序收敛更难，依赖引脚分配 / feedthrough / 时序预算 / ILM",
               role="neutral", title_fs=BODY, detail_fs=CAP - 0.5)
    return T.save(fig, OUT, "f17_hier")


# =========================================================================== #
#  布图规划算法示意图 (f20–f28)  —— 忠于 Handbook of Algorithms for PDA, Ch.8–13
#  约定：等宽/代码块内文字仅用 ASCII；YaHei 缺字形处用文字/ASCII 替代。
# =========================================================================== #

MONO = "monospace"


# F20 发展脉络时间轴（4:3）---------------------------------------------------- #
def f20_devthread():
    fig, ax = T.canvas(9.8, 7.2)
    ax.text(0.4, 6.92, "布图规划算法 · 发展脉络", ha="left", va="center",
            color=T.INK, fontsize=H2, fontweight="bold")
    # 主时间轴（居中，上下各留一排卡片）
    ax0, ax1, ay = 0.7, 9.3, 3.85
    T.line(ax, ax0, ay, ax1, ay, color=T.INK2, lw=2.6, z=2)
    T.arrow(ax, (ax1 - 0.5, ay), (ax1 + 0.02, ay), color=T.INK2, lw=2.6, scale=16, z=2)
    CH = 1.6   # 卡片高
    stages = [
        ("早期构造法", "1980s", "矩形对偶 · mincut · 切片嵌入", "memory", 1.65),
        ("切片 + 模拟退火", "1986", "slicing tree · Polish · Stockmeyer · WongLiu", "logic", 3.65),
        ("非切片表示", "1995-2005", "SP · Btree · TCG · mosaic · Otree", "power", 5.85),
        ("现代 floorplan", "2000s-", "固定轮廓 · slack · 解析法 · 工业原型", "io", 8.05),
    ]
    for i, (name, yr, body, role, x) in enumerate(stages):
        col = T.MAIN[role]
        ax.add_patch(_Circle((x, ay), 0.13, fc=col, ec=T.WHITE, lw=1.6, zorder=5))
        up = (i % 2 == 0)
        # 年份标在轴上、朝向卡片的反侧，避开连接线
        ax.text(x, ay + (-0.38 if up else 0.28), yr, ha="center",
                va=("top" if up else "bottom"), color=col, fontsize=CAP, fontweight="bold", zorder=5)
        cy = ay + 0.62 if up else ay - 0.62 - CH
        T.line(ax, x, ay + (0.16 if up else -0.16), x, cy + (CH if up else 0.0), color=col, lw=1.4, z=3)
        cw = 2.15
        T.infocard(ax, x - cw / 2, cy, cw, CH, name, body, role=role,
                   highlight=True, title_fs=BODY, detail_fs=CAP - 2)
    ax.text(0.4, 0.25, "目标演化：最小面积 + 线长  →  固定轮廓内可行 + 拥塞 / 时序 / 功耗协同",
            ha="left", color=T.MUTED, fontsize=CAP - 1)
    return T.save(fig, OUT, "f20_devthread")


# F21 切片树 + Polish 表达式（~1:1）----------------------------------------- #
def f21_slicing():
    """切片布图 + slicing tree (V/H 内部节点、模块叶) + Polish 后序表达式。
    结构(自顶 H 割)：root = H( V(1, H(2,5)), V(3,4) )，后序 = 1 2 5 H V 3 4 V H。"""
    fig, ax = T.canvas(9.4, 7.4)
    ax.text(0.4, 7.05, "切片布图 · 切片树 · Polish 表达式", ha="left", va="center",
            color=T.INK, fontsize=H2, fontweight="bold")
    # ---- 左：切片布图 (5 块)，与右侧树一致 ----
    bx, by, bw, bh = 0.5, 1.7, 4.0, 4.6
    T.rect(ax, bx, by, bw, bh, fc=T.WHITE, ec=T.INK2, lw=2.0, z=1)
    midY = by + bh * 0.5
    T.line(ax, bx, midY, bx + bw, midY, color=T.ROSE, lw=2.4, z=4)            # 顶层 H 割
    vx = bx + bw * 0.42
    T.line(ax, vx, midY, vx, by + bh, color=T.AMBER_D, lw=2.2, z=4)          # 上半 V 割
    hUp = midY + (by + bh - midY) * 0.5
    T.line(ax, vx, hUp, bx + bw, hUp, color=T.ROSE, lw=2.0, z=4)             # 右侧 H 割
    vx2 = bx + bw * 0.5
    T.line(ax, vx2, by, vx2, midY, color=T.AMBER_D, lw=2.2, z=4)            # 下半 V 割

    def blk(cx, cy, lab, role):
        ax.text(cx, cy, lab, ha="center", va="center", color=T.MAIN[role],
                fontsize=H2, fontweight="bold", zorder=5)
    blk(bx + bw * 0.21, midY + bh * 0.25, "1", "logic")
    blk(vx + (bx + bw - vx) * 0.5, hUp + (by + bh - hUp) * 0.5, "2", "memory")
    blk(vx + (bx + bw - vx) * 0.5, midY + (hUp - midY) * 0.5, "5", "memory")
    blk(bx + bw * 0.25, by + bh * 0.25, "3", "power")
    blk(bx + bw * 0.75, by + bh * 0.25, "4", "power")
    ax.text(bx, by - 0.32, "切片布图（每刀贯穿子区域）", ha="left", color=T.INK2, fontsize=CAP)
    # 横向小图例（一行），置于切片图与 Polish 条之间，避开两者
    T.line(ax, bx + 0.05, 1.3, bx + 0.35, 1.3, color=T.ROSE, lw=3.0, z=5)
    ax.text(bx + 0.45, 1.3, "H 横割（上下）", ha="left", va="center", color=T.ROSE_D, fontsize=CAP - 1, zorder=5)
    T.line(ax, bx + 2.25, 1.3, bx + 2.55, 1.3, color=T.AMBER_D, lw=3.0, z=5)
    ax.text(bx + 2.65, 1.3, "V 竖割（左右）", ha="left", va="center", color=T.AMBER_D, fontsize=CAP - 1, zorder=5)

    # ---- 右：slicing tree ----  root H( V(1, H(2,5)), V(3,4) )
    tx0 = 5.2

    def tnode(x, y, lab, role, r=0.34):
        ax.add_patch(_Circle((x, y), r, fc=T.MAIN[role], ec=T.WHITE, lw=1.5, zorder=5))
        ax.text(x, y, lab, ha="center", va="center", color=T.WHITE, fontsize=BODY, fontweight="bold", zorder=6)
        return (x, y, r)

    def leaf(x, y, lab, role):
        s = 0.62
        T.rect(ax, x - s / 2, y - s / 2, s, s, fc=T.ROLE[role][0], ec=T.MAIN[role], lw=1.6, rounding=0.07, z=5)
        ax.text(x, y, lab, ha="center", va="center", color=T.MAIN[role], fontsize=BODY, fontweight="bold", zorder=6)
        return (x, y, s / 2)

    def edge(a, b):
        T.line(ax, a[0], a[1] - a[2], b[0], b[1] + b[2], color=T.INK2, lw=1.6, z=3)
    rootH = tnode(tx0 + 2.0, 6.15, "H", "io")
    vL = tnode(tx0 + 1.0, 5.0, "V", "power")
    vR = tnode(tx0 + 3.1, 5.0, "V", "power")
    edge(rootH, vL); edge(rootH, vR)
    l1 = leaf(tx0 + 0.35, 3.8, "1", "logic")
    hR = tnode(tx0 + 1.7, 3.8, "H", "io")
    edge(vL, l1); edge(vL, hR)
    l2 = leaf(tx0 + 1.25, 2.65, "2", "memory")
    l5 = leaf(tx0 + 2.15, 2.65, "5", "memory")
    edge(hR, l2); edge(hR, l5)
    l3 = leaf(tx0 + 2.75, 3.8, "3", "power")
    l4 = leaf(tx0 + 3.55, 3.8, "4", "power")
    edge(vR, l3); edge(vR, l4)
    ax.text(tx0 + 0.1, 1.95, "内部节点=割（V/H） · 叶=模块", ha="left", color=T.INK2, fontsize=CAP - 1)

    # ---- 底：Polish 表达式（后序遍历）----
    poly = "1 2 5 H V 3 4 V H"
    T.rect(ax, 0.5, 0.3, 8.5, 0.7, fc=T.SLATE_L, ec=T.LINE, lw=1.2, rounding=0.08, z=2)
    ax.text(0.72, 0.65, "Polish =", ha="left", va="center", color=T.INK, fontsize=BODY, fontweight="bold", zorder=4)
    ax.text(2.35, 0.65, poly, ha="left", va="center", color=T.BLUE_D, fontsize=BODY, fontfamily=MONO, fontweight="bold", zorder=4)
    ax.text(6.6, 0.65, "(规范化：长 2n-1，无连续同号)", ha="left", va="center",
            color=T.TEAL_D, fontsize=CAP - 2, zorder=4)
    return T.save(fig, OUT, "f21_slicing")


# F22 Stockmeyer 形状曲线合并（4:3）---------------------------------------- #
def f22_shapecurve():
    """两子块的阶梯形状曲线 → H 割竖加(高相加) / V 割横加(宽相加)。
    三个面板共用同一坐标比例(S)，便于直接对比；面板标题在顶部、小图示在标题下。"""
    fig, ax = T.canvas(9.8, 6.2)
    ax.text(0.4, 5.9, "Stockmeyer 形状曲线合并（soft / 可旋转块面积最优）",
            ha="left", va="center", color=T.INK, fontsize=H2, fontweight="bold")
    S = 0.82           # 统一坐标比例（数据单位 → 英寸）
    AXLEN = 3.4        # 坐标轴长度（数据单位）
    PY = 0.7           # 三个面板的统一底边 y

    def panel(ox, title, tcol):
        T.line(ax, ox, PY, ox + AXLEN * S, PY, color=T.INK2, lw=1.6, z=3)        # w 轴
        T.line(ax, ox, PY, ox, PY + AXLEN * S, color=T.INK2, lw=1.6, z=3)        # h 轴
        ax.text(ox + AXLEN * S + 0.02, PY - 0.05, "w", ha="left", va="top", color=T.INK2, fontsize=CAP - 1, zorder=3)
        ax.text(ox - 0.08, PY + AXLEN * S, "h", ha="right", va="center", color=T.INK2, fontsize=CAP - 1, zorder=3)
        ax.text(ox, 4.85, title, ha="left", va="center", color=tcol, fontsize=CAP, fontweight="bold", zorder=3)

    def staircase(ox, pts, col, lw=2.8):
        pts = sorted(set(pts))
        for k, (w, h) in enumerate(pts):
            X, Y = ox + w * S, PY + h * S
            if k > 0:
                pw, ph = ox + pts[k - 1][0] * S, PY + pts[k - 1][1] * S
                T.line(ax, pw, ph, X, ph, color=col, lw=lw, z=4)   # 水平段
                T.line(ax, X, ph, X, Y, color=col, lw=lw, z=4)     # 下台阶
            ax.add_patch(_Circle((X, Y), 0.06, fc=col, ec=T.WHITE, lw=0.8, zorder=6))

    A = [(0.7, 1.9), (1.3, 1.1)]      # 子块 u1 的两个朝向 (w,h)
    B = [(0.9, 1.7), (1.5, 0.9)]      # 子块 u2 的两个朝向
    # ---- 左：两子曲线 ----
    o1x = 0.85
    panel(o1x, "两子块曲线 C(u1), C(u2)", T.INK)
    staircase(o1x, A, T.MAIN["logic"])
    staircase(o1x, B, T.MAIN["memory"])
    ax.text(o1x + A[1][0] * S + 0.18, PY + A[1][1] * S, "u1", color=T.BLUE_D, fontsize=CAP - 1, fontweight="bold", zorder=6)
    ax.text(o1x + B[1][0] * S + 0.18, PY + B[1][1] * S, "u2", color=T.TEAL_D, fontsize=CAP - 1, fontweight="bold", zorder=6)

    # ---- 中：V 割 —— 宽相加 ----
    o2x = 4.05
    panel(o2x, "V 割：宽相加 (w1+w2)", T.AMBER_D)
    Vc = [(a[0] + b[0], max(a[1], b[1])) for a, b in zip(A, B)]
    Vc.append((A[0][0] + B[1][0], max(A[0][1], B[1][1])))
    staircase(o2x, Vc, T.MAIN["power"])
    # 小图示：两块并排（置于面板标题上方，避开标题文字）
    T.rect(ax, o2x + 2.55, 5.4, 0.4, 0.46, fc=T.BLUE_L, ec=T.BLUE, lw=1.3, z=5)
    T.rect(ax, o2x + 2.97, 5.4, 0.44, 0.42, fc=T.TEAL_L, ec=T.TEAL, lw=1.3, z=5)

    # ---- 右：H 割 —— 高相加 ----
    o3x = 7.25
    panel(o3x, "H 割：高相加 (h1+h2)", T.ROSE_D)
    Hc = [(max(a[0], b[0]), a[1] + b[1]) for a, b in zip(A, B)]
    Hc.append((max(A[1][0], B[0][0]), A[1][1] + B[0][1]))
    staircase(o3x, Hc, T.MAIN["io"])
    # 小图示：两块上下叠（置于面板标题上方）
    T.rect(ax, o3x + 1.95, 5.66, 0.46, 0.32, fc=T.TEAL_L, ec=T.TEAL, lw=1.3, z=5)
    T.rect(ax, o3x + 1.95, 5.32, 0.46, 0.32, fc=T.BLUE_L, ec=T.BLUE, lw=1.3, z=5)

    ax.text(0.4, 0.2, "自底向上合并 Pareto 阶梯曲线；父曲线每段记所选割向 → 取面积最小点回溯定形",
            ha="left", color=T.MUTED, fontsize=CAP - 1)
    return T.save(fig, OUT, "f22_shapecurve")


# F23 Wong–Liu SA 三种移动 M1/M2/M3（4:3）-------------------------------- #
def f23_wongliu():
    """对一个 normalized Polish 串演示 M1/M2/M3 三种移动（前后小例）。
    M1 换相邻模块 · M2 补一段割链(V<->H) · M3 换相邻 模块与割。"""
    fig, ax = T.canvas(9.6, 6.0)
    ax.text(0.4, 5.7, "Wong–Liu 模拟退火 · 三种移动", ha="left", va="center",
            color=T.INK, fontsize=H2, fontweight="bold")
    ax.text(0.4, 5.2, "状态 = 规范化 Polish 串；代价 = 面积 A + λ·线长 W", ha="left",
            color=T.INK2, fontsize=CAP)

    label_desc = {"M1": "换相邻模块", "M2": "补一段割链 V—H", "M3": "换相邻 模块与割"}

    def poly_row(y, label, lcol, before, after, hi_idx):
        T.tag(ax, 1.0, y, label, role="clock", fs=BODY)
        ax.text(1.85, y, label_desc[label], ha="left", va="center", color=lcol, fontsize=CAP - 1, fontweight="bold")
        for tag, seq, x0 in (("前", before, 1.85), ("后", after, 5.7)):
            ax.text(x0, y - 0.62, tag + ":", ha="left", va="center", color=T.MUTED, fontsize=CAP - 2)
            xx = x0 + 0.55
            for i, ch in enumerate(seq):
                hot = i in hi_idx
                ax.text(xx, y - 0.62, ch, ha="left", va="center",
                        color=(T.ROSE_D if hot else T.INK), fontsize=BODY,
                        fontfamily=MONO, fontweight="bold" if hot else "normal")
                xx += 0.28

    # 基串 1 2 3 V H 4 V （合法且规范化的后序 Polish）
    poly_row(4.35, "M1", T.MAIN["logic"], list("123VH4V"), list("132VH4V"), {1, 2})   # 换相邻模块 2,3
    poly_row(2.95, "M2", T.MAIN["power"], list("123VH4V"), list("123VH4H"), {6})       # 末尾割 V→H
    poly_row(1.55, "M3", T.MAIN["io"], list("123VH4V"), list("123V4HV"), {4, 5})       # 换相邻 割H 与 模块4

    T.rect(ax, 0.5, 0.18, 9.0, 0.62, fc=T.SLATE_L, ec=T.LINE, lw=1.2, rounding=0.08, z=2)
    ax.text(0.75, 0.49, "M1/M2 必得规范化串；M3 可能破坏 → 反复选直到结果规范化。变化仅触及局部子树 → 代价增量重算",
            ha="left", va="center", color=T.INK2, fontsize=CAP - 1, zorder=4)
    return T.save(fig, OUT, "f23_wongliu")


# F24 Sequence Pair：序列 → 约束图 → 最长路（~1:1）---------------------- #
def f24_seqpair():
    """packing + (P+,P-) + 水平/垂直约束图(源 s 汇 t + 最长路示意)。
    规则：i 在 +,- 都先于 j → i 左于 j；i 在 + 后、- 先于 j → i 在 j 下方。
    例：(P+,P-) = (c a b, a c b)：a 左 b、c 左 b、a 下 c —— 与下方 packing/图一致。"""
    fig, ax = T.canvas(9.4, 6.6)
    ax.text(0.4, 6.25, "Sequence Pair：序列 → 约束图 → 最长路", ha="left", va="center",
            color=T.INK, fontsize=H2, fontweight="bold")
    # 三块 packing：a 左下、c 上、b 右 —— 与 SP (c a b, a c b) 一致
    bx, by = 0.6, 0.9
    T.node(ax, bx + 0.0, by + 0.0, 1.5, 1.3, "a", role="logic", fs=H2, z=4)
    T.node(ax, bx + 0.0, by + 1.3, 1.5, 1.5, "c", role="memory", fs=H2, z=4)
    T.node(ax, bx + 1.5, by + 0.0, 1.6, 2.8, "b", role="power", fs=H2, z=4)
    ax.text(bx, by - 0.32, "packing（紧凑布局）", ha="left", color=T.INK2, fontsize=CAP)
    # 序列对
    T.rect(ax, 0.5, 5.0, 4.4, 0.95, fc=T.SLATE_L, ec=T.LINE, lw=1.2, rounding=0.08, z=2)
    ax.text(0.75, 5.66, "P+ =", ha="left", va="center", color=T.INK, fontsize=BODY, fontweight="bold", zorder=4)
    ax.text(1.55, 5.66, "c  a  b", ha="left", va="center", color=T.BLUE_D, fontsize=BODY, fontfamily=MONO, fontweight="bold", zorder=4)
    ax.text(0.75, 5.22, "P- =", ha="left", va="center", color=T.INK, fontsize=BODY, fontweight="bold", zorder=4)
    ax.text(1.55, 5.22, "a  c  b", ha="left", va="center", color=T.AMBER_D, fontsize=BODY, fontfamily=MONO, fontweight="bold", zorder=4)
    ax.text(2.95, 5.66, "( + 先 且 - 先 → 左 )", ha="left", va="center", color=T.MUTED, fontsize=CAP - 2, zorder=4)
    ax.text(2.95, 5.22, "( + 后 且 - 先 → 下 )", ha="left", va="center", color=T.MUTED, fontsize=CAP - 2, zorder=4)

    def cgraph(ox, oy, title, tcol, edges, layout):
        ax.text(ox + 1.5, oy + 2.15, title, ha="center", color=tcol, fontsize=BODY, fontweight="bold", zorder=5)
        pos = {}
        for nm, (x, y), role in layout:
            r = 0.27
            col = T.MAIN[role]
            ax.add_patch(_Circle((ox + x, oy + y), r, fc=col, ec=T.WHITE, lw=1.4, zorder=6))
            ax.text(ox + x, oy + y, nm, ha="center", va="center", color=T.WHITE, fontsize=CAP, fontweight="bold", zorder=7)
            pos[nm] = (ox + x, oy + y, r)
        for u, v, hot in edges:
            a, b = pos[u], pos[v]
            T.arrow(ax, a[:2], b[:2], color=(tcol if hot else T.LINE),
                    lw=(2.6 if hot else 1.4), scale=12, z=5)
        return pos

    # GH: s->a->b->t ; s->c->b ; 最长路 s-a-b-t (高亮)
    gh_layout = [("s", (0.0, 1.0), "neutral"), ("a", (1.0, 1.5), "logic"),
                 ("c", (1.0, 0.4), "memory"), ("b", (2.0, 1.0), "power"), ("t", (3.0, 1.0), "neutral")]
    gh_edges = [("s", "a", True), ("s", "c", False), ("a", "b", True),
                ("c", "b", False), ("b", "t", True)]
    cgraph(5.5, 3.7, "GH 水平约束图（左→右）", T.BLUE_D, gh_edges, gh_layout)
    ax.text(5.5, 3.5, "x 坐标 = s→i 最长路；芯宽 = s→t 最长路", ha="left", color=T.MUTED, fontsize=CAP - 2, zorder=5)

    # GV: s->a->c->t ; s->b->t ; 最长路 s-a-c-t
    gv_layout = [("s", (0.0, 1.0), "neutral"), ("a", (1.0, 0.4), "logic"),
                 ("c", (2.0, 0.4), "memory"), ("b", (1.0, 1.6), "power"), ("t", (3.0, 1.0), "neutral")]
    gv_edges = [("s", "a", True), ("a", "c", True), ("c", "t", True),
                ("s", "b", False), ("b", "t", False)]
    cgraph(5.5, 0.7, "GV 垂直约束图（下→上）", T.ROSE_D, gv_edges, gv_layout)
    ax.text(5.5, 0.5, "y 坐标 = s→i 最长路；芯高 = s→t 最长路", ha="left", color=T.MUTED, fontsize=CAP - 2, zorder=5)
    return T.save(fig, OUT, "f24_seqpair")


# F25 B*-tree：左孩右邻 / 右孩上邻 + contour（~1:1）--------------------- #
def f25_bstar():
    """admissible packing + B*-tree（根=左下块，左孩=右邻 x=xi+wi，右孩=上邻 x=xi）+ contour。"""
    fig, ax = T.canvas(9.4, 6.6)
    ax.text(0.4, 6.25, "B*-tree：左孩=右邻块 · 右孩=上邻块 · contour 打包",
            ha="left", va="center", color=T.INK, fontsize=H2, fontweight="bold")
    # ---- 左：admissible packing ----
    bx, by = 0.5, 0.6
    blocks = {
        "a": (0.0, 0.0, 1.6, 1.5, "logic"),    # 左下 = 根
        "b": (1.6, 0.0, 1.4, 1.0, "power"),    # b 右邻 a (x = xa + wa)
        "c": (1.6, 1.0, 1.9, 1.4, "memory"),   # c 在 b 之上 (同 x=1.6) → b 的右孩
        "d": (3.0, 0.0, 1.1, 1.0, "io"),       # d 右邻 b
        "e": (0.0, 1.5, 1.6, 1.4, "memory"),   # e 在 a 之上 (同 x=0) → a 的右孩
    }
    sc = 1.05
    for nm, (x, y, w, h, role) in blocks.items():
        T.node(ax, bx + x * sc, by + y * sc, w * sc, h * sc, nm, role=role, fs=H2, z=4)
    # contour 顶轮廓（阶梯红线）
    contour = [(0.0, 2.9), (1.6, 2.9), (1.6, 2.4), (3.0, 2.4), (3.0, 1.0), (4.1, 1.0)]
    cpx = [bx + x * sc for x, _ in contour]
    cpy = [by + y * sc for _, y in contour]
    for k in range(len(contour) - 1):
        T.line(ax, cpx[k], cpy[k], cpx[k + 1], cpy[k], color=T.ROSE, lw=2.6, z=6)
        T.line(ax, cpx[k + 1], cpy[k], cpx[k + 1], cpy[k + 1], color=T.ROSE, lw=2.6, z=6)
    T.tag(ax, bx + 2.2, by + 3.35, "contour 轮廓线", role="io", fs=CAP - 1)
    ax.text(bx, by - 0.3, "admissible（左/下都压实）", ha="left", color=T.INK2, fontsize=CAP)

    # ---- 右：B*-tree ----
    tx = 5.4

    def tn(x, y, lab, role, r=0.36):
        ax.add_patch(_Circle((x, y), r, fc=T.MAIN[role], ec=T.WHITE, lw=1.6, zorder=6))
        ax.text(x, y, lab, ha="center", va="center", color=T.WHITE, fontsize=BODY, fontweight="bold", zorder=7)
        return (x, y, r)

    def tedge(a, b, kind):
        col = T.BLUE_D if kind == "L" else T.AMBER_D
        T.arrow(ax, (a[0], a[1] - a[2]), (b[0], b[1] + b[2]), color=col, lw=2.0, scale=12, z=4)

    na = tn(tx + 1.4, 5.3, "a", "logic")
    nb = tn(tx + 0.6, 4.1, "b", "power")   # 左孩 = 右邻块 b
    ne = tn(tx + 2.3, 4.1, "e", "memory")  # 右孩 = 上邻块 e
    tedge(na, nb, "L"); tedge(na, ne, "R")
    nd = tn(tx + 0.1, 2.9, "d", "io")      # b 的左孩 = b 的右邻 d
    nc = tn(tx + 1.2, 2.9, "c", "memory")  # b 的右孩 = b 的上邻 c
    tedge(nb, nd, "L"); tedge(nb, nc, "R")
    ax.text(tx - 0.1, 1.95, "根 a = 左下块；DFS + contour → O(n) 打包", ha="left", color=T.INK2, fontsize=CAP - 1)
    T.legend(ax, [(T.BLUE_D, "左孩：右邻块  x = xi + wi"),
                  (T.AMBER_D, "右孩：上邻块  x = xi")],
             tx + 0.1, 1.5, fs=CAP - 1, dy=0.42)
    return T.save(fig, OUT, "f25_bstar")


# F26 TCG：水平/垂直传递闭包图（可选，4:3）------------------------------ #
def f26_tcg():
    """Ch / Cv 传递闭包图：关系在图中透明、打包前可判。"""
    fig, ax = T.canvas(9.4, 5.6)
    ax.text(0.4, 5.25, "TCG：水平/垂直传递闭包图（关系透明、打包前可判）",
            ha="left", va="center", color=T.INK, fontsize=H2, fontweight="bold")

    def graph(ox, oy, title, tcol, nodes, edges, closure):
        ax.text(ox + 1.4, oy + 2.55, title, ha="center", color=tcol, fontsize=BODY, fontweight="bold", zorder=5)
        pos = {}
        for nm, (x, y), role in nodes:
            ax.add_patch(_Circle((ox + x, oy + y), 0.3, fc=T.MAIN[role], ec=T.WHITE, lw=1.4, zorder=6))
            ax.text(ox + x, oy + y, nm, ha="center", va="center", color=T.WHITE, fontsize=BODY, fontweight="bold", zorder=7)
            pos[nm] = (ox + x, oy + y)
        for u, v in closure:   # 闭包边（虚线、浅）
            T.arrow(ax, pos[u], pos[v], color=T.LINE, lw=1.3, scale=10, z=4, rad=-0.32, ls=(0, (3, 3)))
        for u, v in edges:     # reduction 边（实线、主色）
            T.arrow(ax, pos[u], pos[v], color=tcol, lw=2.4, scale=13, z=5)
        return pos
    nodes = [("a", (0.0, 0.4), "logic"), ("b", (1.5, 0.4), "power"),
             ("c", (2.9, 0.4), "memory")]
    # Ch: a 左 b 左 c → reduction a->b, b->c ; closure a->c
    graph(0.6, 0.7, "Ch 水平闭包图（左→右）", T.BLUE_D,
          nodes, [("a", "b"), ("b", "c")], [("a", "c")])
    # Cv: a 下 d、b 下 c
    nodes2 = [("a", (0.6, 0.0), "logic"), ("d", (0.6, 1.4), "io"),
              ("b", (2.4, 0.0), "power"), ("c", (2.4, 1.4), "memory")]
    graph(5.2, 0.7, "Cv 垂直闭包图（下→上）", T.ROSE_D,
          nodes2, [("a", "d"), ("b", "c")], [])
    ax.text(0.4, 0.2, "每对模块恰一条边在 Ch 或 Cv；闭包(虚线)显式记间接关系 → 不必打包即可判先后",
            ha="left", color=T.MUTED, fontsize=CAP - 1)
    return T.save(fig, OUT, "f26_tcg")


# F27 固定轮廓 + slack（4:3）-------------------------------------------- #
def f27_fixedoutline():
    """经典最小面积结果 vs 固定轮廓（画目标 outline + slack/whitespace）。"""
    fig, ax = T.canvas(9.6, 6.2)
    ax.text(0.4, 5.9, "经典最小面积  vs  固定轮廓 floorplanning", ha="left", va="center",
            color=T.INK, fontsize=H2, fontweight="bold")
    # ---- 左：经典 min-area（外形自由，可能不符封装）----
    bx, by = 0.5, 1.0
    ax.text(bx, by + 4.5, "经典：最小面积（外形自由）", ha="left", color=T.BLUE_D, fontsize=BODY, fontweight="bold")
    T.rect(ax, bx, by, 1.7, 3.9, fc=T.WHITE, ec=T.INK2, lw=2.0, z=1)
    for (x, y, w, h, role) in [(0.1, 0.1, 1.5, 1.2, "logic"), (0.1, 1.4, 0.7, 1.1, "power"),
                               (0.9, 1.4, 0.7, 1.1, "memory"), (0.1, 2.6, 1.5, 1.2, "io")]:
        T.node(ax, bx + x, by + y, w, h, "", role=role, fs=CAP, z=4, shadow=False)
    ax.text(bx + 0.85, by - 0.32, "面积最小但 15×6", ha="center", color=T.MUTED, fontsize=CAP - 1)
    T.tag(ax, bx + 0.85, by + 4.08, "装不进 10×10（不可行）", role="io", fs=CAP - 2)

    # ---- 右：固定轮廓 + slack ----
    ox, oy = 4.3, 1.0
    ax.text(ox, oy + 4.5, "固定轮廓：塞进给定 outline + 用 slack 引导", ha="left", color=T.AMBER_D, fontsize=BODY, fontweight="bold")
    OW, OH = 4.5, 3.9
    T.rect(ax, ox, oy, OW, OH, fc="none", ec=T.AMBER_D, lw=2.6, ls=(0, (6, 3)), z=2)  # 目标 outline
    T.tag(ax, ox + OW - 0.95, oy + OH - 0.3, "目标 outline", role="power", fs=CAP - 2)
    blk = [(0.15, 0.15, 1.7, 1.6, "logic"), (1.95, 0.15, 1.15, 1.1, "power"),
           (0.15, 1.9, 1.5, 1.8, "memory"), (1.8, 1.45, 1.5, 2.25, "io")]
    for (x, y, w, h, role) in blk:
        T.node(ax, ox + x, oy + y, w, h, "", role=role, fs=CAP, z=4, shadow=False)
    # whitespace（右下角空白阴影），与 power 块间留可见空隙
    T.rect(ax, ox + 3.55, oy + 0.15, 0.8, 1.1, fc=T.SLATE_L, ec=T.LINE, lw=1.0, hatch="////", z=3)
    ax.text(ox + 3.95, oy + 0.7, "white\nspace", ha="center", va="center", color=T.MUTED, fontsize=CAP - 3, zorder=4)
    # slack：power 块向右可移动的余量（横跨空隙的双箭头）
    sb = blk[1]
    sy = oy + sb[1] + sb[3] / 2
    T.arrow(ax, (ox + sb[0] + sb[2], sy), (ox + 3.5, sy), color=T.ROSE_D, lw=2.2, style="<|-|>", scale=13, z=6)
    ax.text(ox + (sb[0] + sb[2] + 3.5) / 2, sy + 0.26, "slack", ha="center", color=T.ROSE_D, fontsize=CAP - 1, fontweight="bold", zorder=6)

    ax.text(0.4, 0.3, "slack = 左下压实 vs 右上压实的位置差；把零-slack（关键路径）块挪到高-slack 块旁 → 收进轮廓",
            ha="left", color=T.MUTED, fontsize=CAP - 1)
    return T.save(fig, OUT, "f27_fixedoutline")


# F28 工业：flat vs hierarchical + floorplanning→prototyping（4:3）------ #
def f28_hier():
    fig, ax = T.canvas(9.6, 6.4)
    ax.text(0.4, 6.05, "工业布图：flat vs hierarchical · floorplanning → prototyping",
            ha="left", va="center", color=T.INK, fontsize=H2, fontweight="bold")
    # ---- 左：flat ----
    bx, by = 0.5, 2.6
    ax.text(bx + 1.85, by + 3.0, "flat 扁平", ha="center", color=T.BLUE_D, fontsize=BODY, fontweight="bold")
    T.rect(ax, bx, by, 3.7, 2.7, fc=T.WHITE, ec=T.INK2, lw=1.8, z=1)
    for (x, y, w, h, role) in [(0.25, 0.3, 1.5, 1.0, "memory"), (1.95, 0.3, 1.45, 1.6, "logic"),
                               (0.25, 1.5, 1.5, 0.9, "power")]:
        T.node(ax, bx + x, by + y, w, h, "", role=role, fs=CAP, z=4, shadow=False)
    for k in range(5):  # 边界引脚
        T.rect(ax, bx + 0.4 + k * 0.65, by + 2.7 - 0.04, 0.12, 0.16, fc=T.ROSE, ec="none", z=5)
    ax.text(bx + 1.85, by - 0.32, "整片一次布线/摆 · 引脚在外环", ha="center", color=T.MUTED, fontsize=CAP - 1)

    # ---- 右：hierarchical ----
    hx, hy = 5.0, 2.6
    ax.text(hx + 2.1, hy + 3.0, "hierarchical 层次化", ha="center", color=T.TEAL_D, fontsize=BODY, fontweight="bold")
    T.rect(ax, hx, hy, 4.2, 2.7, fc=T.WHITE, ec=T.INK2, lw=1.8, z=1)
    for i, (x, w) in enumerate([(0.25, 1.7), (2.15, 1.8)]):
        b = T.node(ax, hx + x, hy + 0.35, w, 1.9, f"Blk{i+1}", role="memory", fs=CAP, z=4)
        for k in range(3):  # 块边界引脚
            T.rect(ax, b["x"] + 0.25 + k * (w - 0.5) / 2 - 0.05, b["y"] + b["h"] - 0.02, 0.1, 0.14, fc=T.ROSE, ec="none", z=5)
        ax.text(b["cx"], b["y"] - 0.22, "预算 budget", ha="center", color=T.AMBER_D, fontsize=CAP - 3, zorder=5)
    ax.text(hx + 2.1, hy - 0.32, "顶层切块 + 引脚分配 + 时序预算（一个坏预算拖垮全片）",
            ha="center", color=T.MUTED, fontsize=CAP - 2)

    # ---- 底：floorplanning → prototyping 流程 ----
    items = [("floorplanning", "诊断可行性\n容忍不全数据", "logic", False),
             ("pin assign +\ntiming budget", "zero-slack 分配\n到/必需时间", "power", False),
             ("routability", "全局布线\n估拥塞/试布线", "memory", False),
             ("prototyping", "验 RTL 可实现\n签核前闸门", "io", True)]
    T.flowrow(ax, items, y=0.45, x0=0.5, x1=9.1, h=1.5, gap=0.55, title_fs=CAP, sub_fs=CAP - 4)
    return T.save(fig, OUT, "f28_hier")


def main():
    figs = [f01_position, f03_geometry, f06_macro,
            f07_halo, f09_irem, f12_io,
            f15_loop, f16_uniquify, f17_hier,
            f20_devthread, f21_slicing, f22_shapecurve, f23_wongliu,
            f24_seqpair, f25_bstar, f26_tcg, f27_fixedoutline, f28_hier]
    print("Output:", OUT)
    for fn in figs:
        print("  saved:", os.path.basename(fn()))
    print("done:", len(figs))


if __name__ == "__main__":
    main()
