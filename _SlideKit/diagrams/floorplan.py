# -*- coding: utf-8 -*-
"""
_SlideKit/diagrams/floorplan.py  (v3 · 论文插图)
================================================
Floorplan 主题的论文/图书级插图（12 张），**用于插入 PPT**：
- 无图内大标题/署名（标题与出处交给幻灯片），图形**占满画框**；
- 字号更大、信息更密、空间利用更充分；
- 语义多色(theme.py v2)，一次导出 PNG + SVG。

运行：python diagrams/floorplan.py   输出：../IC_Backend_Notes/assets/floorplan/f01..f12
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme as T  # noqa: E402

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..",
                                   "IC_Backend_Notes", "assets", "floorplan"))


def _hx(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def lerp(c1, c2, t):
    a, b = _hx(c1), _hx(c2)
    return "#%02X%02X%02X" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def hflow(ax, specs, y, x0, x1, h, gap=0.28, fs=18, sub_fs=12, arrow=T.INK2, lw=2.8):
    n = len(specs)
    w = (x1 - x0 - gap * (n - 1)) / n
    nodes, x = [], x0
    for (title, sub, role, variant) in specs:
        nodes.append(T.node(ax, x, y, w, h, title, sub=sub, role=role, variant=variant, fs=fs, sub_fs=sub_fs))
        x += w + gap
    for a, b in zip(nodes[:-1], nodes[1:]):
        T.arrow(ax, a["right"], b["left"], color=arrow, lw=lw, scale=18)
    return nodes


# F01 ---------------------------------------------------------------------- #
def f01_position():
    fig, ax = T.canvas(13, 5.6); T.plate(ax)
    ax.text(0.55, 5.05, "RTL → 综合 → [ Floorplan · Power · Place · CTS · Route ] → Signoff → GDSII",
            ha="left", va="center", color=T.INK, fontsize=15, fontweight="bold")
    specs = [
        ("Netlist", "门级网表", "neutral", "soft"),
        ("Floorplan", "布图规划", "logic", "solid"),
        ("Power Plan", "电源规划", "power", "soft"),
        ("Placement", "布局", "logic", "soft"),
        ("CTS", "时钟树", "clock", "soft"),
        ("Routing", "布线", "memory", "soft"),
        ("Signoff", "STA/DRC/LVS", "neutral", "soft"),
    ]
    nodes = hflow(ax, specs, y=2.2, x0=0.5, x1=12.5, h=2.4, fs=18, sub_fs=12)
    T.bracket(ax, nodes[1]["x"], nodes[5]["x"] + nodes[5]["w"], 2.05,
              "物理实现 Physical Implementation（决定 PPA 上限）", depth=0.55, color=T.BLUE_D, fs=14)
    return T.save(fig, OUT, "f01_position")


# F02 ---------------------------------------------------------------------- #
def f02_why():
    fig, ax = T.canvas(12, 7.2); T.plate(ax)
    ox, oy, pw, ph = 1.4, 1.4, 5.6, 4.9
    T.line(ax, ox, oy, ox, oy + ph + 0.2, color=T.INK2, lw=2.2)
    T.line(ax, ox, oy, ox + pw + 0.2, oy, color=T.INK2, lw=2.2)
    ax.text(ox - 0.15, oy + ph + 0.45, "修改成本", ha="center", va="center", color=T.INK2, fontsize=14, fontweight="bold")
    stages = ["Floorplan", "Place", "CTS", "Route", "Signoff"]
    xs = [ox + 0.4 + i * (pw - 0.6) / 4 for i in range(5)]
    ys = [oy + v for v in (0.5, 1.4, 2.5, 3.7, 4.6)]
    ax.fill_between(xs, [oy] * 5, ys, color=T.ROSE_L, zorder=1)
    ax.plot(xs, ys, color=T.ROSE, lw=3.6, zorder=3, solid_capstyle="round")
    for xx, yy in zip(xs, ys):
        ax.plot([xx], [yy], "o", color=T.ROSE, ms=11, zorder=4, mec="white", mew=1.5)
    for i, xx in enumerate(xs):
        ax.text(xx, oy - 0.32, stages[i], ha="center", va="center", color=T.INK2, fontsize=12)
    T.annotate(ax, (xs[0], ys[0] + 0.05), (xs[0] + 0.55, ys[0] + 1.25), "改在此\n≈ 免费", color=T.TEAL_D, rad=-0.2, fs=13)
    T.annotate(ax, (xs[4], ys[4]), (xs[4] - 2.7, ys[4] + 0.35), "改在此\n≈ 推倒重来", color=T.ROSE_D, rad=0.25, fs=13)
    # 右：PPA 三角 + 三类代价
    cx, cy, r = 9.7, 5.4, 1.55
    ax.fill([cx, cx - r, cx + r], [cy + r, cy - r * 0.85, cy - r * 0.85], color=T.BLUE_L, ec=T.BLUE, lw=2, zorder=2, alpha=0.65)
    T.tag(ax, cx, cy + r + 0.3, "Performance", role="logic", fs=12)
    T.tag(ax, cx - r, cy - r * 0.85 - 0.3, "Power", role="power", fs=12)
    T.tag(ax, cx + r, cy - r * 0.85 - 0.3, "Area", role="memory", fs=12)
    ax.text(cx, cy - r * 0.1, "PPA\n权衡", ha="center", va="center", color=T.INK, fontsize=15, fontweight="bold", zorder=3)
    ax.text(8.0, 2.5, "三类典型代价：", ha="left", color=T.INK, fontsize=13.5, fontweight="bold")
    for i, (t, c) in enumerate([("利用率↑ → 拥塞绕不出", T.ROSE), ("宏乱放 → 时序收不回", T.AMBER), ("PG 不足 → IR/EM 超标", T.VIOLET)]):
        T.rect(ax, 8.0, 1.95 - i * 0.55, 0.22, 0.22, fc=c, ec="none", z=4)
        ax.text(8.35, 2.06 - i * 0.55, t, ha="left", va="center", color=T.INK2, fontsize=12.5)
    return T.save(fig, OUT, "f02_why")


# F03 ---------------------------------------------------------------------- #
def _pads(ax, x, y, s, n, dep, gap=0.13):
    plh = (s - gap * (n + 1)) / n
    for i in range(n):
        p = x + gap + i * (plh + gap)
        T.rect(ax, p, y, plh, dep, fc=T.ROSE_L, ec=T.ROSE, lw=1.1, z=3)
        T.rect(ax, p, y + s - dep, plh, dep, fc=T.ROSE_L, ec=T.ROSE, lw=1.1, z=3)
    plv = (s - 2 * dep - gap * (n + 1)) / n
    for i in range(n):
        q = y + dep + gap + i * (plv + gap)
        T.rect(ax, x, q, dep, plv, fc=T.ROSE_L, ec=T.ROSE, lw=1.1, z=3)
        T.rect(ax, x + s - dep, q, dep, plv, fc=T.ROSE_L, ec=T.ROSE, lw=1.1, z=3)


def f03_geometry():
    fig, ax = T.canvas(11, 8); T.plate(ax)
    dx, dy, s = 0.7, 0.7, 6.6
    T.rect(ax, dx, dy, s, s, fc=T.WHITE, ec=T.INK2, lw=2.4, z=1, shadow=True)
    dep = 0.42
    _pads(ax, dx, dy, s, 9, dep)
    inset = dep + 0.55
    cx, cy, cs = dx + inset, dy + inset, s - 2 * inset
    T.rect(ax, cx, cy, cs, cs, fc=T.BLUE_L, ec=T.BLUE, lw=1.8, z=2)
    ry = cy + 0.32
    while ry < cy + cs - 0.2:
        T.line(ax, cx + 0.2, ry, cx + cs - 0.2, ry, color=T.BLUE, lw=0.7, z=3); ry += 0.42
    ax.text(cx + cs / 2, cy + cs - 0.4, "Core", ha="center", color=T.BLUE_D, fontsize=17, fontweight="bold", zorder=5)
    ax.text(dx + 0.12, dy + s + 0.06, "Die", ha="left", va="bottom", color=T.INK, fontsize=16, fontweight="bold")
    lx = dx + s + 0.55
    T.annotate(ax, (dx + s, dy + s - 0.5), (lx, 7.3), "Die 边界\n(含 scribe 切割道)", rad=-0.15, fs=13.5)
    T.annotate(ax, (dx + s - dep / 2, dy + s * 0.5), (lx, 5.9), "I/O Pad / 焊盘环", rad=-0.12, color=T.ROSE_D, fs=13.5)
    T.annotate(ax, (cx + cs, cy + cs * 0.6), (lx, 4.6), "Core 核心区\n(标准单元 + 宏)", rad=-0.12, color=T.BLUE_D, fs=13.5)
    T.annotate(ax, (cx + cs - 0.3, cy + cs * 0.32), (lx, 3.0), "Core Rows\n标准单元行", rad=-0.12, color=T.BLUE_D, fs=13.5)
    ax.text(lx, 1.6, "利用率 = (Σ单元+Σ宏)/Core ≈ 0.5–0.8\n长宽比 H/W ≈ 1 最均衡\nCore-to-IO：留电源环 / IO 走线",
            ha="left", va="top", color=T.INK2, fontsize=12.5, linespacing=1.7)
    return T.save(fig, OUT, "f03_geometry")


# F04 ---------------------------------------------------------------------- #
def _fill_core(ax, x, y, s, density, color):
    cell, gap = 0.42, 0.14
    cols = int((s - gap) / (cell + gap))
    target = int(cols * cols * density)
    k = 0
    for r in range(cols):
        for c in range(cols):
            if k >= target:
                return
            T.rect(ax, x + gap + c * (cell + gap), y + gap + r * (cell + gap), cell, cell, fc=color, ec="none", z=3, rounding=0.04)
            k += 1


def f04_util():
    fig, ax = T.canvas(12, 6.6); T.plate(ax)
    T.rect(ax, 0.7, 1.7, 3.7, 3.7, fc=T.WHITE, ec=T.BLUE, lw=2.0, z=2)
    _fill_core(ax, 0.7, 1.7, 3.7, 0.45, T.BLUE_L)
    ax.text(2.55, 5.7, "利用率 ≈ 50% · 宽松", ha="center", color=T.BLUE_D, fontsize=14, fontweight="bold")
    T.rect(ax, 4.9, 1.7, 3.7, 3.7, fc=T.WHITE, ec=T.ROSE, lw=2.0, z=2)
    _fill_core(ax, 4.9, 1.7, 3.7, 0.85, T.ROSE_L)
    ax.text(6.75, 5.7, "利用率 ≈ 85% · 易拥塞", ha="center", color=T.ROSE_D, fontsize=14, fontweight="bold")
    T.tag(ax, 6.75, 3.5, "congestion\n热点", role="io", fs=11)
    T.rect(ax, 9.4, 1.7, 1.6, 3.7, fc=T.TEAL_L, ec=T.TEAL, lw=2.0, z=2)
    ax.text(10.2, 1.35, "H/W 大\n瘦高·差", ha="center", va="top", color=T.TEAL_D, fontsize=12)
    T.rect(ax, 9.4, 1.7, 2.6, 2.6, fc="none", ec=T.TEAL, lw=2.0, ls=(0, (4, 3)), z=1)
    ax.text(10.7, 5.7, "H/W ≈ 1 · 方正(推荐)", ha="center", color=T.TEAL_D, fontsize=12.5, fontweight="bold")
    ax.text(0.7, 0.95, "Total Util = (Σ std-cell + Σ macro) / Core 面积        "
            "Effective Util = Σ std-cell / (Core − blockage − halo)",
            ha="left", va="center", color=T.INK2, fontsize=13)
    return T.save(fig, OUT, "f04_util")


# F05 ---------------------------------------------------------------------- #
def f05_rows():
    fig, ax = T.canvas(13, 7.2); T.plate(ax)
    x0, x1 = 1.3, 9.6
    rows, rh, y = 4, 1.2, 1.0
    for i in range(rows):
        yy = y + i * rh
        T.rect(ax, x0, yy, x1 - x0, rh, fc=(T.SLATE_L if i % 2 == 0 else T.WHITE), ec=T.LINE, lw=1.0, z=2)
        ax.text(x1 + 0.2, yy + rh / 2, f"Row {i} · {'翻转 FS' if i % 2 else '正放 R0'}",
                ha="left", va="center", color=T.INK2, fontsize=13)
        for c in range(5):
            T.rect(ax, x0 + 0.55 + c * 1.6, yy + 0.2, 1.15, rh - 0.4, fc=T.BLUE_L, ec=T.BLUE, lw=1.1, z=3, rounding=0.05)
    for i in range(rows + 1):
        yy = y + i * rh
        col = T.AMBER if i % 2 == 0 else T.INK
        lbl = "VDD" if i % 2 == 0 else "VSS"
        T.line(ax, x0 - 0.35, yy, x1, yy, color=col, lw=3.6, z=4)
        ax.text(x0 - 0.5, yy, lbl, ha="right", va="center", color=col, fontsize=12, fontweight="bold")
    for c in range(int((x1 - x0) / 0.5) + 1):
        T.line(ax, x0 + c * 0.5, y, x0 + c * 0.5, y + 0.2, color=T.MUTED, lw=0.7, z=5)
    ax.text(x0, y - 0.4, "↑ site 栅格（行内最小放置单位，定义于 LEF）", ha="left", color=T.MUTED, fontsize=12)
    T.legend(ax, [("power", "VDD rail"), ("ink", "VSS rail"), ("logic", "标准单元")], 10.6, 6.8, fs=13, dy=0.46)
    return T.save(fig, OUT, "f05_rows")


# F06 ---------------------------------------------------------------------- #
def f06_macro():
    fig, ax = T.canvas(11.5, 7.6); T.plate(ax)
    cx, cy, cw, ch = 0.7, 0.7, 10.1, 6.2
    T.rect(ax, cx, cy, cw, ch, fc=T.WHITE, ec=T.INK2, lw=2.0, z=1)
    T.rect(ax, cx + 0.25, cy + 0.25, cw - 0.5, ch - 0.5, fc=T.BLUE_L, ec="none", z=1, alpha=0.45)
    ax.text(cx + cw * 0.62, cy + ch * 0.42, "Std-Cell Region\n标准单元区", ha="center", va="center",
            color=T.BLUE_D, fontsize=15, fontweight="bold", zorder=2)
    m1 = T.node(ax, cx + 0.4, cy + ch - 2.4, 3.0, 2.0, "SRAM", sub="hard IP", role="memory", z=4, fs=16, sub_fs=11)
    m2 = T.node(ax, cx + cw - 3.4, cy + ch - 2.4, 3.0, 2.0, "SRAM", sub="hard IP", role="memory", z=4, fs=16, sub_fs=11)
    T.node(ax, cx + 0.4, cy + 0.4, 2.7, 1.8, "PLL / IP", role="memory", variant="outline", z=4, fs=15)
    for m in (m1, m2):
        for k in range(6):
            px = m["x"] + 0.35 + k * (m["w"] - 0.7) / 5
            T.rect(ax, px - 0.06, m["y"] - 0.03, 0.12, 0.16, fc=T.ROSE, ec="none", z=5)
    ax.text(m1["cx"], m1["y"] - 0.35, "引脚朝 core →", ha="center", color=T.ROSE_D, fontsize=12)
    for dyf in (0.4, 0.9, 1.4):
        T.line(ax, m1["x"] + m1["w"], m1["y"] + dyf, cx + cw * 0.56, cy + ch * 0.42, color=T.TEAL, lw=1.1, ls=(0, (3, 3)), z=3)
    T.tag(ax, (m1["x"] + m1["w"] + m2["x"]) / 2, cy + ch - 1.3, "channel 通道", role="io", fs=12)
    T.legend(ax, [("memory", "Macro / 硬 IP"), ("io", "引脚 / channel"), ("teal", "数据流 flyline")], cx + 3.6, cy + 1.0, fs=12.5, dy=0.46)
    return T.save(fig, OUT, "f06_macro")


# F07 ---------------------------------------------------------------------- #
def f07_halo():
    fig, ax = T.canvas(11.5, 7); T.plate(ax)
    cx, cy, cw, ch = 0.7, 0.7, 10.1, 5.6
    T.rect(ax, cx, cy, cw, ch, fc=T.WHITE, ec=T.INK2, lw=2.0, z=1)
    m1 = T.node(ax, cx + 0.7, cy + 1.4, 3.0, 3.6, "Macro A", role="memory", z=4, fs=16)
    m2 = T.node(ax, cx + 6.0, cy + 1.4, 3.0, 3.6, "Macro B", role="memory", z=4, fs=16)
    T.rect(ax, m1["x"] - 0.32, m1["y"] - 0.32, m1["w"] + 0.64, m1["h"] + 0.64, fc="none", ec=T.ROSE, lw=1.8, ls=(0, (5, 3)), z=4)
    T.tag(ax, m1["cx"], m1["y"] - 0.62, "halo / keepout 隔离环", role="io", fs=12)
    chx0, chx1 = m1["x"] + m1["w"] + 0.35, m2["x"] - 0.35
    for k in range(8):
        xx = chx0 + (k + 1) * (chx1 - chx0) / 9
        T.line(ax, xx, cy + 1.5, xx, cy + 5.2, color=T.TEAL, lw=1.2, z=3)
    T.tag(ax, (chx0 + chx1) / 2, cy + 5.5, "channel 布线通道", role="memory", fs=12)
    T.rect(ax, cx + cw - 2.7, cy + 0.35, 2.3, 1.2, fc=T.SLATE_L, ec=T.MUTED, lw=1.3, hatch="////", z=3)
    ax.text(cx + cw - 1.55, cy + 0.95, "placement\nblockage", ha="center", va="center", color=T.INK2, fontsize=12)
    return T.save(fig, OUT, "f07_halo")


# F08 ---------------------------------------------------------------------- #
def f08_power():
    fig, ax = T.canvas(11, 7.6); T.plate(ax)
    cx, cy, cw, ch = 0.7, 0.7, 7.9, 6.2
    T.rect(ax, cx, cy, cw, ch, fc=T.WHITE, ec=T.INK2, lw=1.8, z=1)
    T.rect(ax, cx + 0.18, cy + 0.18, cw - 0.36, ch - 0.36, fc="none", ec=T.AMBER, lw=5, z=3)
    T.rect(ax, cx + 0.5, cy + 0.5, cw - 1.0, ch - 1.0, fc="none", ec=T.INK, lw=5, z=3)
    x0, x1 = cx + 0.5, cx + cw - 0.5
    y0, y1 = cy + 0.5, cy + ch - 0.5
    vx = [x0 + (i + 1) * (x1 - x0) / 7 for i in range(6)]
    hy = [y0 + (j + 1) * (y1 - y0) / 5 for j in range(4)]
    for i, xx in enumerate(vx):
        T.line(ax, xx, y0, xx, y1, color=T.AMBER if i % 2 == 0 else T.INK, lw=3, z=2)
    for j, yy in enumerate(hy):
        T.line(ax, x0, yy, x1, yy, color=T.INK if j % 2 == 0 else T.AMBER, lw=2.6, z=2)
    for xx in vx:
        for yy in hy:
            ax.plot([xx], [yy], "o", color=T.ROSE, ms=5, zorder=5)
    for k in range(8):
        yy = cy + 0.62 + k * 0.14
        T.line(ax, x0, yy, x1, yy, color=(T.AMBER if k % 2 else T.INK), lw=0.8, z=2)
    bx = cx + cw + 0.5
    ax.text(bx, cy + ch - 0.2, "供电骨架（逐层）", ha="left", va="top", color=T.INK, fontsize=14, fontweight="bold")
    for i, (t, c) in enumerate([("Power Ring 电源环(顶层金属)", T.AMBER), ("Power Stripe 电源条", T.AMBER),
                                 ("纵横交织成 Power Mesh", T.INK), ("Std-cell Rails 供电轨(M1)", T.INK), ("via 连接各金属层", T.ROSE)]):
        T.rect(ax, bx, cy + ch - 0.95 - i * 0.55, 0.24, 0.24, fc=c, ec="none", z=4)
        ax.text(bx + 0.38, cy + ch - 0.83 - i * 0.55, t, ha="left", va="center", color=T.INK2, fontsize=12.5)
    ax.text(bx, cy + 1.2, "mesh 越密 → IR 越小，\n但越占布线资源（权衡）", ha="left", va="top", color=T.MUTED, fontsize=12.5, linespacing=1.6)
    return T.save(fig, OUT, "f08_power")


# F09 ---------------------------------------------------------------------- #
def f09_irem():
    fig, ax = T.canvas(12.5, 6.8); T.plate(ax)
    gx, gy, gs, n = 0.9, 1.2, 4.9, 8
    cell = gs / n
    ramp = ["#16A34A", "#65A30D", "#CA8A04", "#EA580C", "#DC2626"]
    for r in range(n):
        for c in range(n):
            t = (r / (n - 1)) * (len(ramp) - 1)
            i0 = int(t)
            col = lerp(ramp[i0], ramp[min(i0 + 1, len(ramp) - 1)], t - i0)
            T.rect(ax, gx + c * cell, gy + (n - 1 - r) * cell, cell, cell, fc=col, ec=T.WHITE, lw=0.7, z=2)
    for c in range(n):
        T.rect(ax, gx + c * cell + 0.06, gy + gs + 0.06, cell - 0.12, 0.26, fc=T.AMBER, ec=T.AMBER_D, lw=0.9, z=3)
    ax.text(gx + gs / 2, gy + gs + 0.6, "电源 pad（供电边）", ha="center", color=T.AMBER_D, fontsize=13, fontweight="bold")
    ax.text(gx + gs / 2, gy - 0.4, "ΔV = I · R   离电源越远，压降越大", ha="center", color=T.INK, fontsize=13.5, fontweight="bold")
    lx = gx + gs + 0.35
    for i, col in enumerate(ramp):
        T.rect(ax, lx, gy + gs - 0.2 - i * 0.55, 0.32, 0.55, fc=col, ec="none", z=3)
    ax.text(lx + 0.45, gy + gs, "电压高", ha="left", va="center", color=T.INK2, fontsize=12)
    ax.text(lx + 0.45, gy - 0.05, "电压低", ha="left", va="center", color=T.INK2, fontsize=12)
    ex = 7.4
    ax.text(ex, gy + gs + 0.55, "电迁移 EM (Electromigration)", ha="left", color=T.ROSE_D, fontsize=15, fontweight="bold")
    T.rect(ax, ex, gy + 3.5, 4.4, 0.85, fc=T.SLATE_L, ec=T.INK2, lw=1.6, z=2)
    for k in range(5):
        T.arrow(ax, (ex + 0.4 + k * 0.95, gy + 3.92), (ex + 0.85 + k * 0.95, gy + 3.92), color=T.ROSE, lw=2.4, scale=13)
    ax.text(ex, gy + 3.15, "电流密度 J 过大 → 金属原子被“吹”走 → 断路/短路", ha="left", color=T.INK2, fontsize=12.5)
    T.rect(ax, ex, gy + 1.3, 4.4, 1.2, fc=T.TEAL_L, ec=T.TEAL, lw=1.6, z=2)
    ax.text(ex + 2.2, gy + 1.9, "加宽金属 / 多 via → 降低 J", ha="center", color=T.TEAL_D, fontsize=13.5, fontweight="bold")
    ax.text(ex, gy + 0.7, "缓解：更密 mesh、更宽干线、更多 via、合理 pad 分布", ha="left", va="top", color=T.MUTED, fontsize=12)
    return T.save(fig, OUT, "f09_irem")


# F10 ---------------------------------------------------------------------- #
def f10_mv():
    fig, ax = T.canvas(12, 7); T.plate(ax)
    T.rect(ax, 0.6, 1.2, 4.9, 4.6, fc=T.BLUE_L, ec=T.BLUE, lw=1.8, z=1, rounding=0.12, alpha=0.5)
    T.rect(ax, 6.7, 1.2, 4.7, 4.6, fc=T.VIOLET_L, ec=T.VIOLET, lw=1.8, z=1, rounding=0.12, alpha=0.5)
    ax.text(3.05, 5.45, "Domain A · VDD1 (always-on)", ha="center", color=T.BLUE_D, fontsize=13.5, fontweight="bold")
    ax.text(9.05, 5.45, "Domain B · VDD2 (switchable)", ha="center", color=T.VIOLET_D, fontsize=13.5, fontweight="bold")
    la = T.node(ax, 1.0, 2.9, 2.4, 1.5, "Logic A", role="logic", z=4, fs=15)
    T.node(ax, 1.0, 1.4, 2.4, 1.1, "Always-on Buf", role="neutral", z=4, fs=11.5)
    lb = T.node(ax, 9.0, 2.9, 2.1, 1.5, "Logic B", role="clock", z=4, fs=15)
    T.node(ax, 9.0, 1.4, 2.1, 1.1, "Retention FF", role="neutral", z=4, fs=11.5)
    ls = T.node(ax, 5.55, 3.1, 1.3, 1.1, "LS", sub="电平转换", role="io", z=5, fs=14, sub_fs=9)
    iso = T.node(ax, 7.05, 3.1, 1.15, 1.1, "ISO", sub="隔离", role="memory", z=5, fs=13, sub_fs=9)
    T.arrow(ax, la["right"], ls["left"], color=T.INK, lw=2.4)
    T.arrow(ax, ls["right"], iso["left"], color=T.INK, lw=2.4)
    T.arrow(ax, iso["right"], lb["left"], color=T.INK, lw=2.4)
    psw = T.node(ax, 6.7, 6.0, 2.6, 0.9, "Power Switch", sub="header / MTCMOS", role="power", z=5, fs=12.5, sub_fs=9)
    ax.text(psw["cx"], psw["y"] + psw["h"] + 0.32, "VDD", ha="center", color=T.INK, fontsize=12.5, fontweight="bold")
    T.arrow(ax, (psw["cx"], psw["y"] + psw["h"] + 0.2), psw["top"], color=T.MUTED, lw=1.8)
    T.arrow(ax, psw["bottom"], (9.0, 5.5), color=T.AMBER, lw=2.4)
    ax.text(6.0, 0.7, "UPF：create_power_domain · set_isolation · set_level_shifter · 关断时 retention FF 保状态",
            ha="center", color=T.MUTED, fontsize=12)
    return T.save(fig, OUT, "f10_mv")


# F11 ---------------------------------------------------------------------- #
def f11_budget():
    fig, ax = T.canvas(12.5, 6.4); T.plate(ax)
    a = T.node(ax, 0.8, 3.2, 3.3, 2.3, "Block A", sub="partition", role="memory", variant="outline", z=3, fs=16, sub_fs=11)
    b = T.node(ax, 8.4, 3.2, 3.3, 2.3, "Block B", sub="partition", role="memory", variant="outline", z=3, fs=16, sub_fs=11)
    T.rect(ax, 0.5, 2.8, 11.5, 3.3, fc="none", ec=T.LINE, lw=1.5, ls=(0, (4, 3)), z=1)
    ax.text(6.25, 5.85, "Top 顶层", ha="center", color=T.INK2, fontsize=13)
    T.arrow(ax, a["right"], (b["x"], 4.35), color=T.BLUE, lw=2.8)
    ax.text(6.25, 4.7, "跨块路径", ha="center", color=T.BLUE_D, fontsize=12.5, fontweight="bold")
    ax.text(6.25, 3.7, "顶层与各块并行实现、\n各自满足分到的预算\n→ 收敛更快、可复用", ha="center", va="center", color=T.INK2, fontsize=12.5, linespacing=1.6)
    by, bh, bx0, bx1 = 1.1, 0.85, 0.8, 11.9
    segs = [("Block A\n0.8ns", T.TEAL, 0.34), ("interface\n0.2", T.AMBER, 0.12), ("Top route\n0.4", T.BLUE, 0.18),
            ("interface\n0.2", T.AMBER, 0.12), ("Block B\n0.8ns", T.TEAL, 0.24)]
    x = bx0
    for label, col, frac in segs:
        w = (bx1 - bx0) * frac
        T.rect(ax, x, by, w, bh, fc=col, ec=T.WHITE, lw=1.6, z=3)
        ax.text(x + w / 2, by + bh / 2, label, ha="center", va="center", color=T.WHITE, fontsize=11, fontweight="bold", zorder=4)
        x += w
    ax.text(bx0, by + bh + 0.32, "整条路径预算 = 2.0 ns，按层级切分给各段（含接口 / feedthrough 余量）",
            ha="left", color=T.INK2, fontsize=12.5)
    return T.save(fig, OUT, "f11_budget")


# F12 ---------------------------------------------------------------------- #
def f12_io():
    fig, ax = T.canvas(13, 6); T.plate(ax)
    ins = ["Gate-level Netlist (.v)", "Tech / Cell LEF (.lef)", "Timing Libs (.lib)",
           "SDC 时序约束", "UPF 功耗意图", "Partition / 时序预算"]
    y = 5.3
    in_nodes = []
    for label in ins:
        nd = T.node(ax, 0.5, y - 0.72, 3.6, 0.72, label, role="neutral", fs=12, z=3, shadow=False)
        in_nodes.append(nd); y -= 0.86
    eng = T.node(ax, 5.4, 2.1, 3.4, 1.9, "Floorplan", sub="ICC2 / Innovus", role="logic", variant="solid", z=4, fs=19, sub_fs=12)
    outs = [("DEF：宏摆放 + PG + blockage", "memory"), ("Floorplan DB (NDM / OA)", "memory"), ("可布线性 / 时序 初评", "io")]
    y = 4.6
    for label, role in outs:
        nd = T.node(ax, 9.4, y - 0.95, 3.5, 0.95, label, role=role, fs=12, z=3)
        T.arrow(ax, eng["right"], nd["left"], color=T.INK2, lw=2.2, rad=0.05); y -= 1.4
    for nd in in_nodes:
        T.arrow(ax, nd["right"], (eng["x"], eng["cy"] + (nd["cy"] - eng["cy"]) * 0.25), color=T.LINE, lw=1.6, scale=13)
    return T.save(fig, OUT, "f12_io")


def main():
    figs = [f01_position, f02_why, f03_geometry, f04_util, f05_rows, f06_macro,
            f07_halo, f08_power, f09_irem, f10_mv, f11_budget, f12_io]
    print("Output:", OUT)
    for fn in figs:
        print("  saved:", os.path.basename(fn()))
    print("done:", len(figs))


if __name__ == "__main__":
    main()
