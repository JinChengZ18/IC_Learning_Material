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
    T.sechead(ax, 0.4, 6.4, "①", "Floorplan 在 PnR 流程中的位置")
    items = [("逻辑综合", "Synth", "neutral", False), ("布图规划", "Floorplan", "clock", True),
             ("布局", "Place", "neutral", False), ("时钟树", "CTS", "neutral", False), ("布线", "Route", "neutral", False)]
    T.flowrow(ax, items, y=4.6, x0=0.4, x1=8.6, h=1.25, gap=0.42, title_fs=BODY + 1, sub_fs=9)
    ax.text(0.4, 3.85, "Floorplan 主要任务", ha="left", va="center", color=T.INK, fontsize=BODY, fontweight="bold")
    tasks = ["① die / core 几何", "② 宏摆放 & 朝向", "③ 电源规划 PG", "④ 多电压 / blockage"]
    for i, t in enumerate(tasks):
        x = 0.4 + (i % 2) * 4.25
        y = 2.45 - (i // 2) * 1.3
        T.infocard(ax, x, y, 4.0, 1.1, t, role="clock", title_fs=BODY)
    return T.save(fig, OUT, "f01_position")


# F02 为什么重要（4:3）----------------------------------------------------- #
def f02_why():
    fig, ax = T.canvas(9.2, 6.8)
    # 左：修改成本曲线
    ox, oy, pw, ph = 1.0, 0.9, 3.9, 5.4
    T.line(ax, ox, oy, ox, oy + ph + 0.15, color=T.INK2, lw=2)
    T.line(ax, ox, oy, ox + pw + 0.15, oy, color=T.INK2, lw=2)
    ax.text(ox - 0.05, oy + ph + 0.42, "修改成本", ha="center", color=T.INK, fontsize=H2, fontweight="bold")
    stages = ["FP", "Place", "CTS", "Route", "Signoff"]
    xs = [ox + 0.35 + i * (pw - 0.45) / 4 for i in range(5)]
    ys = [oy + v for v in (0.5, 1.55, 2.8, 4.1, 5.1)]
    ax.fill_between(xs, [oy] * 5, ys, color=T.ROSE_L, zorder=1)
    ax.plot(xs, ys, color=T.ROSE, lw=3.4, zorder=3, solid_capstyle="round")
    for xx, yy in zip(xs, ys):
        ax.plot([xx], [yy], "o", color=T.ROSE, ms=9, zorder=4, mec="white", mew=1.4)
    for i, xx in enumerate(xs):
        ax.text(xx, oy - 0.3, stages[i], ha="center", color=T.INK2, fontsize=CAP - 0.5)
    T.annotate(ax, (xs[0], ys[0] + 0.05), (xs[0] + 0.45, ys[0] + 1.2), "改在此\n≈ 免费", color=T.TEAL_D, rad=-0.2, fs=CAP)
    T.annotate(ax, (xs[4], ys[4]), (xs[4] - 1.9, ys[4] + 0.3), "改在此\n≈ 重来", color=T.ROSE_D, rad=0.25, fs=CAP)
    # 右：PPA 三角（上）+ 三类代价卡（下）
    cx, cy, r = 7.1, 5.2, 1.25
    ax.fill([cx, cx - r, cx + r], [cy + r, cy - r * 0.85, cy - r * 0.85], color=T.BLUE_L, ec=T.BLUE, lw=1.8, zorder=2, alpha=0.65)
    T.tag(ax, cx, cy + r + 0.28, "Performance", role="logic", fs=CAP - 0.5)
    T.tag(ax, cx - r + 0.1, cy - r * 0.85 - 0.28, "Power", role="power", fs=CAP - 0.5)
    T.tag(ax, cx + r - 0.1, cy - r * 0.85 - 0.28, "Area", role="memory", fs=CAP - 0.5)
    ax.text(cx, cy - r * 0.05, "PPA\n权衡", ha="center", va="center", color=T.INK, fontsize=H2, fontweight="bold", zorder=3)
    costs = [("利用率高 → 拥塞", "io"), ("宏乱放 → 时序差", "power"), ("PG 不足 → IR/EM", "clock")]
    for i, (t, role) in enumerate(costs):
        T.infocard(ax, 5.3, 2.45 - i * 0.78, 3.7, 0.66, t, role=role, title_fs=CAP)
    return T.save(fig, OUT, "f02_why")


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


# F04 利用率与长宽比（4:3）------------------------------------------------ #
def _fill_core(ax, x, y, s, density, color):
    cell, gap = 0.34, 0.11
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
    fig, ax = T.canvas(9, 6.8)
    ax.text(0.5, 6.45, "利用率 Utilization", ha="left", color=T.INK, fontsize=H2, fontweight="bold")
    T.rect(ax, 0.5, 3.5, 2.5, 2.5, fc=T.WHITE, ec=T.BLUE, lw=2.0, z=2)
    _fill_core(ax, 0.5, 3.5, 2.5, 0.45, T.BLUE_L)
    ax.text(1.75, 3.15, "≈ 50% 宽松", ha="center", va="top", color=T.BLUE_D, fontsize=BODY, fontweight="bold")
    T.rect(ax, 3.2, 3.5, 2.5, 2.5, fc=T.WHITE, ec=T.ROSE, lw=2.0, z=2)
    _fill_core(ax, 3.2, 3.5, 2.5, 0.85, T.ROSE_L)
    ax.text(4.45, 3.15, "≈ 85% 拥塞", ha="center", va="top", color=T.ROSE_D, fontsize=BODY, fontweight="bold")
    # 右：长宽比（瘦高 vs 方正）
    ax.text(6.0, 6.45, "长宽比 H/W", ha="left", color=T.TEAL_D, fontsize=H2, fontweight="bold")
    T.rect(ax, 6.2, 3.5, 0.75, 2.5, fc=T.SLATE_L, ec=T.MUTED, lw=1.8, z=2)
    ax.text(6.57, 3.15, "瘦高·差", ha="center", va="top", color=T.INK2, fontsize=CAP)
    T.rect(ax, 7.4, 4.25, 1.4, 1.4, fc=T.TEAL_L, ec=T.TEAL, lw=2.0, z=2)
    ax.text(8.1, 3.9, "方正·推荐", ha="center", va="top", color=T.TEAL_D, fontsize=CAP, fontweight="bold")
    T.infocard(ax, 0.5, 1.0, 8.3, 1.5, "利用率两个口径",
               "Total = (Σ单元+Σ宏)/Core      Effective = Σ单元/(Core − blockage − halo)", role="neutral", title_fs=BODY, detail_fs=CAP)
    return T.save(fig, OUT, "f04_util")


# F05 行 / site / 翻转供电轨（4:3）---------------------------------------- #
def f05_rows():
    fig, ax = T.canvas(9, 6.8)
    x0, x1 = 1.0, 6.4
    rows, rh, y = 4, 1.05, 2.2
    for i in range(rows):
        yy = y + i * rh
        T.rect(ax, x0, yy, x1 - x0, rh, fc=(T.SLATE_L if i % 2 == 0 else T.WHITE), ec=T.LINE, lw=1.0, z=2)
        ax.text(x1 + 0.2, yy + rh / 2, f"Row {i}·{'翻转 FS' if i % 2 else '正放 R0'}", ha="left", va="center", color=T.INK2, fontsize=CAP)
        for c in range(4):
            T.rect(ax, x0 + 0.45 + c * 1.28, yy + 0.17, 0.95, rh - 0.34, fc=T.BLUE_L, ec=T.BLUE, lw=1.0, z=3, rounding=0.05)
    for i in range(rows + 1):
        yy = y + i * rh
        col = T.AMBER if i % 2 == 0 else T.INK
        T.line(ax, x0 - 0.3, yy, x1, yy, color=col, lw=3.2, z=4)
        ax.text(x0 - 0.42, yy, "VDD" if i % 2 == 0 else "VSS", ha="right", va="center", color=col, fontsize=CAP, fontweight="bold")
    ax.text(x0, y - 0.32, "↑ site 栅格（行内最小放置单位，LEF 定义）", ha="left", color=T.MUTED, fontsize=CAP - 0.5)
    T.infocard(ax, 0.6, 0.45, 7.8, 1.05,
               "翻转共享供电轨", "相邻行镜像翻转(FS) → 同名轨落行边界、被两行共享 → 条数减半、面积省", role="power", title_fs=BODY, detail_fs=CAP)
    return T.save(fig, OUT, "f05_rows")


# F06 宏摆放原则（4:3）---------------------------------------------------- #
def f06_macro():
    fig, ax = T.canvas(9.4, 6.8)
    cx, cy, cw, ch = 0.4, 0.5, 4.7, 5.8
    T.rect(ax, cx, cy, cw, ch, fc=T.WHITE, ec=T.INK2, lw=1.8, z=1)
    T.rect(ax, cx + 0.2, cy + 0.2, cw - 0.4, ch - 0.4, fc=T.BLUE_L, ec="none", z=1, alpha=0.4)
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


# F08 电源网格（4:3）------------------------------------------------------ #
def f08_power():
    fig, ax = T.canvas(9.4, 6.8)
    cx, cy, cw, ch = 0.4, 0.5, 5.2, 5.8
    T.rect(ax, cx, cy, cw, ch, fc=T.WHITE, ec=T.INK2, lw=1.6, z=1)
    T.rect(ax, cx + 0.16, cy + 0.16, cw - 0.32, ch - 0.32, fc="none", ec=T.AMBER, lw=4.5, z=3)
    T.rect(ax, cx + 0.45, cy + 0.45, cw - 0.9, ch - 0.9, fc="none", ec=T.INK, lw=4.5, z=3)
    x0, x1 = cx + 0.45, cx + cw - 0.45
    y0, y1 = cy + 0.45, cy + ch - 0.45
    vx = [x0 + (i + 1) * (x1 - x0) / 6 for i in range(5)]
    hy = [y0 + (j + 1) * (y1 - y0) / 5 for j in range(4)]
    for i, xx in enumerate(vx):
        T.line(ax, xx, y0, xx, y1, color=T.AMBER if i % 2 == 0 else T.INK, lw=2.6, z=2)
    for j, yy in enumerate(hy):
        T.line(ax, x0, yy, x1, yy, color=T.INK if j % 2 == 0 else T.AMBER, lw=2.2, z=2)
    for xx in vx:
        for yy in hy:
            ax.plot([xx], [yy], "o", color=T.ROSE, ms=4, zorder=5)
    bx = cx + cw + 0.4
    pw = 9.4 - bx - 0.3
    layers = [("Power Ring 环", "power"), ("Power Stripe 条", "power"), ("Power Mesh 网", "neutral"),
              ("Std-cell Rail M1", "neutral"), ("via 连接层", "io")]
    for i, (t, role) in enumerate(layers):
        T.infocard(ax, bx, 5.55 - i * 1.16, pw, 0.98, t, role=role, title_fs=BODY)
    return T.save(fig, OUT, "f08_power")


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


# F10 多电压域（4:3）------------------------------------------------------ #
def f10_mv():
    fig, ax = T.canvas(9.4, 6.6)
    T.rect(ax, 0.4, 1.2, 3.7, 4.0, fc=T.BLUE_L, ec=T.BLUE, lw=1.6, z=1, rounding=0.12, alpha=0.5)
    T.rect(ax, 5.3, 1.2, 3.7, 4.0, fc=T.VIOLET_L, ec=T.VIOLET, lw=1.6, z=1, rounding=0.12, alpha=0.5)
    ax.text(2.25, 4.9, "Domain A · always-on", ha="center", color=T.BLUE_D, fontsize=BODY, fontweight="bold")
    ax.text(7.15, 4.9, "Domain B · switchable", ha="center", color=T.VIOLET_D, fontsize=BODY, fontweight="bold")
    la = T.node(ax, 0.8, 2.7, 1.9, 1.4, "Logic A", role="logic", z=4, fs=BODY)
    T.node(ax, 0.8, 1.4, 1.9, 1.0, "Always-on Buf", role="neutral", z=4, fs=CAP - 1)
    lb = T.node(ax, 6.7, 2.7, 1.9, 1.4, "Logic B", role="clock", z=4, fs=BODY)
    T.node(ax, 6.7, 1.4, 1.9, 1.0, "Retention FF", role="neutral", z=4, fs=CAP - 1)
    ls = T.node(ax, 4.2, 2.85, 1.0, 1.05, "LS", role="io", z=5, fs=BODY)
    isoc = T.node(ax, 5.28, 2.85, 1.0, 1.05, "ISO", role="memory", z=5, fs=BODY)
    T.arrow(ax, la["right"], ls["left"], color=T.INK, lw=2.2)
    T.arrow(ax, ls["right"], isoc["left"], color=T.INK, lw=2.2)
    T.arrow(ax, isoc["right"], lb["left"], color=T.INK, lw=2.2)
    psw = T.node(ax, 5.3, 5.3, 2.4, 0.85, "Power Switch", role="power", z=5, fs=CAP)
    T.arrow(ax, psw["bottom"], (7.15, 5.2), color=T.AMBER, lw=2.2)
    ax.text(4.7, 0.55, "UPF：power_domain · isolation · level_shifter · retention", ha="center", color=T.MUTED, fontsize=CAP - 0.5)
    return T.save(fig, OUT, "f10_mv")


# F11 时序预算（4:3）------------------------------------------------------ #
def f11_budget():
    fig, ax = T.canvas(9, 6.4)
    a = T.node(ax, 0.5, 3.6, 2.7, 2.0, "Block A", sub="partition", role="memory", variant="outline", z=3, fs=H2, sub_fs=CAP - 1)
    b = T.node(ax, 5.8, 3.6, 2.7, 2.0, "Block B", sub="partition", role="memory", variant="outline", z=3, fs=H2, sub_fs=CAP - 1)
    T.rect(ax, 0.3, 3.2, 8.4, 3.0, fc="none", ec=T.LINE, lw=1.4, ls=(0, (4, 3)), z=1)
    ax.text(4.5, 5.95, "Top 顶层", ha="center", color=T.INK2, fontsize=CAP)
    T.arrow(ax, a["right"], (b["x"], 4.6), color=T.BLUE, lw=2.6)
    ax.text(4.5, 4.85, "跨块路径", ha="center", color=T.BLUE_D, fontsize=CAP, fontweight="bold")
    ax.text(4.5, 4.0, "各块并行实现\n各自满足预算", ha="center", va="center", color=T.INK2, fontsize=CAP, linespacing=1.5)
    by, bh, bx0, bx1 = 1.5, 0.85, 0.5, 8.5
    segs = [("Block A\n0.8", T.TEAL, 0.34), ("if 0.2", T.AMBER, 0.12), ("Top 0.4", T.BLUE, 0.18), ("if 0.2", T.AMBER, 0.12), ("Block B\n0.8", T.TEAL, 0.24)]
    x = bx0
    for label, col, frac in segs:
        w = (bx1 - bx0) * frac
        T.rect(ax, x, by, w, bh, fc=col, ec=T.WHITE, lw=1.5, z=3)
        ax.text(x + w / 2, by + bh / 2, label, ha="center", va="center", color=T.WHITE, fontsize=CAP - 1, fontweight="bold", zorder=4)
        x += w
    ax.text(bx0, by + bh + 0.3, "整条路径预算 2.0 ns 按层级切分（含接口 / feedthrough 余量）", ha="left", color=T.INK2, fontsize=CAP)
    ax.text(bx0, 0.95, "→ 顶层与各块并行收敛、可复用", ha="left", color=T.MUTED, fontsize=CAP)
    return T.save(fig, OUT, "f11_budget")


# F12 输入 / 输出（~1:1，纵向）-------------------------------------------- #
def f12_io():
    fig, ax = T.canvas(7.6, 7)
    ins = ["Netlist (.v)", "LEF", "Liberty (.lib)", "SDC", "UPF", "Partition / 预算"]
    for i, label in enumerate(ins):
        x = 0.4 + (i % 2) * 2.0
        y = 6.0 - (i // 2) * 0.95
        T.node(ax, x, y - 0.78, 1.85, 0.78, label, role="neutral", fs=CAP - 0.5, z=3, shadow=False)
    eng = T.node(ax, 4.7, 4.0, 2.6, 1.6, "Floorplan", sub="ICC2 / Innovus", role="logic", variant="solid", z=4, fs=H2, sub_fs=CAP)
    ax.text(2.3, 3.2, "↓ 吃进", ha="center", color=T.MUTED, fontsize=CAP)
    outs = [("DEF：宏 + PG + blockage", "memory"), ("Floorplan DB (NDM/OA)", "memory"), ("可布线性 / 时序初评", "io")]
    for i, (label, role) in enumerate(outs):
        T.infocard(ax, 0.4, 2.4 - i * 0.92, 6.9, 0.78, label, role=role, title_fs=CAP)
    T.arrow(ax, (3.3, 4.0), eng["left"], color=T.LINE, lw=1.6, scale=12)
    T.arrow(ax, eng["bottom"], (3.85, 2.95), color=T.INK2, lw=2.0, rad=-0.1)
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
