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


def main():
    figs = [f01_position, f03_geometry, f06_macro,
            f07_halo, f09_irem, f12_io,
            f15_loop, f16_uniquify, f17_hier]
    print("Output:", OUT)
    for fn in figs:
        print("  saved:", os.path.basename(fn()))
    print("done:", len(figs))


if __name__ == "__main__":
    main()
