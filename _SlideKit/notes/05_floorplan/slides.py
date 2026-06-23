# -*- coding: utf-8 -*-
"""
_SlideKit/notes/05_floorplan/slides.py  (v5 · IEEE 靛蓝学术 · 浅母版)
====================================================================
Floorplan 24 页幻灯片，与教案 05_Floorplan.md 逐页对应；知识点写在页面上（完整句、
非速记），论文插图作配图插入。封面/导览/收尾用独立版式，不套内容页分栏。
配色：全篇统一靛蓝主色 + 暖橙仅作强调（不每页换色）。
运行：python slides.py  → 产出可编辑 .pptx + 逐页版面预览。
"""
import os
import sys

_SK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # _SlideKit 根
sys.path.insert(0, _SK)
import deck as D  # noqa: E402

ROOT = os.path.abspath(os.path.join(_SK, "..", "IC_Backend_Notes"))
ASSETS = os.path.join(ROOT, "assets", "floorplan")
PREV = os.path.join(ROOT, "slides", "_preview")
PPTX = os.path.join(ROOT, "slides", "05_Floorplan.pptx")
TOTAL = 24
SRC = "整理 J.C  ·  源自 Digital VLSI Design (DVD), Prof. Adam Teman, Bar-Ilan University (83-612)"
FOOTER = "Floorplan · 布图规划"   # 左下页脚标签（随笔记而变）；页码用母版 slidenum 字段自动生成

# 统一配色：主色靛蓝，暖橙仅强调（全篇一致）。复用引擎调色板，避免第三处硬编码（单一真源 theme.py）
PRIMARY = D.PRIMARY
ACCENT = D.ACCENT
BLUE = TEAL = AMBER = ROSE = VIOLET = PRIMARY  # 内容页一律靛蓝；橙色只出现在封面/导览/收尾


def split(t, sub, fig, bullets, acc=PRIMARY, style="bullet"):
    # style: "bullet"=并列(▪)；"num"=递进/有序(①②③)
    return {"kind": "split", "title": t, "sub": sub, "figure": fig, "bullets": bullets, "accent": acc, "style": style}


def bl(t, sub, bullets, acc=PRIMARY, two=False):
    return {"kind": "bullets", "title": t, "sub": sub, "bullets": bullets, "accent": acc, "two_col": two}


SPECS = [
    {"kind": "cover", "title": "Floorplan 布图规划",
     "tag": "数字 IC 后端 · 从 RTL 到 GDS · DVD Lecture 6",
     "sub": "物理实现的第一步：把逻辑网表映射成版图骨架",
     "line": "一步错，步步错 —— Floorplan 决定 PPA 上限",
     "src": SRC},

    {"kind": "agenda", "title": "本讲导览  Agenda", "sub": "从定位与意义，到电源完整性与迭代收敛",
     "sections": [
        ("1", "定位与意义", "Floorplan 为何决定后端 PPA 上限"),
        ("2", "芯片几何", "Die / Core / IO、行与翻转共享供电轨"),
        ("3", "利用率与长宽比", "两个利用率口径与方正取向"),
        ("4", "宏与阻挡", "宏摆放、halo / blockage、专用单元"),
        ("5", "IO 与引脚", "Pad / Bump、引脚分配与 feedthrough"),
        ("6", "电源完整性", "PG 网络、IR / EM、门控、多电压域"),
        ("7", "收敛闭环", "时序预算、拥塞预估、迭代回退"),
     ],
     "line": "主线：Floorplan 决定后端天花板，是“试布局→评估→回退”的迭代闭环，并非一遍过"},

    split("什么是 Floorplan", "综合之后、详细布局之前，把网表落成版图骨架的六项任务", "f01_position.png", [
        "确定 die 与 core 的整体几何尺寸",
        "决定各 macro 硬核的位置与朝向",
        "规划 IO / Pad / Bump 与引脚分配",
        "搭建 PG 电源骨架：环 / 条 / 网 / 轨",
        "划分多电压域与电压岛边界",
        "预留各类 blockage 与 halo / keepout",
    ], style="num"),
    split("为什么重要：一步错，步步错", "决定 PPA 上限", "f02_why.png", [
        "Floorplan 决定芯片 PPA（性能/功耗/面积）的上限",
        "利用率定得过高，再好的布局也会拥塞、绕不出线",
        "macro 摆放不合理，关键路径绕远，时序难以收回",
        "PG 规划不足，签核时才暴露 IR drop 或 EM 超标",
        "此阶段改动几乎免费，越往后改成本急剧上升",
        "“七分布局三分布线”是经验俗语，并非量化指标",
    ]),
    split("芯片几何：Die / IO / Core / Rows", "各区域从属关系", "f03_geometry.png", [
        "Die 是芯片最外边界，含 scribe 切割道，包住一切",
        "Core 是放置标准单元与 macro 的内部核心区域",
        "IO 区 Pad Ring 是 Die 与 Core 之间的环形地带",
        "Core 到 IO 的间距留给电源环与 IO 走线",
        "Core 内被切成等高的水平标准单元行 Rows",
        "几何层层嵌套：Die 包 Pad Ring，Pad Ring 包 Core",
    ]),
    split("标准单元行 / site / 翻转共享供电轨", "等高行、site 栅格与翻转共享供电轨", "f05_rows.png", [
        "Row 是 Core 切出的等高水平行，行高等于库单元高度",
        "行高约等于 track 数乘以 M2 pitch（9T 比 7T 高）",
        "Site 是行内最小放置栅格，定义在 LEF 文件中",
        "单元宽度必须是 site 宽度的整数倍",
        "相邻行镜像翻转 FS，让同名供电轨落在行边界上",
        "上下两行共享供电轨，使轨数减半、更省面积",
    ]),
    split("利用率与长宽比", "两种利用率口径与长宽比取向", "f04_util.png", [
        "总利用率 =（标准单元面积 + macro 面积）÷ Core 面积",
        "有效利用率扣除 blockage 与 halo，工具多报此口径",
        "经验初值取 0.5–0.8，视 macro 占比、拥塞与裕量而定",
        "目标利用率不等于 placement 之后的局部实际密度",
        "长宽比接近 1 最利于布线与时钟树平衡",
        "长宽比定义各工具可能相反，须以官方手册为准",
    ]),
    split("宏单元摆放原则", "宏 = 大尺寸硬核（SRAM/PLL/IP），五条摆放原则", "f06_macro.png", [
        "沿边沿角摆放，中间连续区留给标准单元",
        "按数据流就近放置，用 flyline 或 auto placer 指导",
        "宏间预留 channel 走线，或采用 channel-less 紧贴",
        "引脚朝向 core，避免信号绕过宏本体",
        "从 8 种朝向中选定，对称背靠背、对齐成阵列",
    ], style="num"),
    split("halo / keepout 与各类 blockage", "halo 与三类 blockage，为布线预留空间", "f07_halo.png", [
        "Halo/Keepout 是 macro 四周禁放边带，随 macro 一起移动",
        "Placement Blockage 是固定坐标的禁放区，钉在版图上",
        "hard 类型完全禁放，soft 类型优化阶段仍可放 buffer",
        "partial 类型按密度上限限制，近似 density screen",
        "Routing Blockage 禁止某些层布线，可指定具体层范围",
        "在 macro 引脚一侧加 halo，为 pin access 留出空间",
    ]),
    bl("物理专用单元：endcap / well-tap / filler", "不参与逻辑，却关乎 row 与 well 连续", [
        "physical-only cell 不参与逻辑，却关乎 row 与 well 连续",
        "Endcap 放在每行两端与 macro 边界，保 well/implant 连续",
        "Well-tap 周期性插入，为衬底提供 well 偏置接触",
        "tap 间距须满足 max well-tap distance，否则有 latch-up 风险",
        "Filler 在流程末期填满行内空隙，保供电轨与 well 连续",
        "Filler 的引入时机晚于 tap 与 endcap",
    ]),
    split("IO / Pad、Bump（封装相关）", "wire-bond vs flip-chip", "f13_iopad.png", [
        "Wire-bond 方式下，IO Pad 沿 die 四周排成 Pad Ring",
        "需考虑信号与电源 Pad 交替、ESD 防护和 Corner Pad",
        "Flip-Chip 方式下，信号经 Bump 面阵列从 die 表面引出",
        "Flip-Chip 常配 RDL，是否需要取决于封装与凸点布局",
        "Bump 须对齐封装 bump map，控制间距与电源信号比例",
    ]),
    bl("引脚分配 Pin Assignment", "pin 位置决定块间走线与时序", [
        "顶层设计中，IO buffer 位置决定芯片对外引脚位置",
        "块级设计中，partition 端口要分配到块边界具体位置",
        "pin 须落在合法 routing track 上，并与该层布线方向一致",
        "pin 应沿数据流方向分布，避免块间产生长绕线",
        "信号穿过无关 block 时，须预留 feedthrough 穿通端口",
        "工具可自动优化 pin，但关键总线常需手工约束",
    ]),
    split("电源规划：Ring → Stripe → Mesh → Rails", "自上而下、由粗到细，逐级连成 PG 网络", "f08_power.png", [
        "Power Ring：绕 core 或 macro 的闭合环，多用顶层粗金属",
        "Power Stripe：横跨 core 的粗金属条，用来分担电流",
        "Power Mesh：stripe 纵横交织成网，降低等效电阻",
        "Std-cell Rail：沿标准单元行的 M1 供电轨（follow-pin）",
        "Special Route：连接 ring/stripe/pin/pad 并打 via 成型",
    ], style="num"),
    split("IR drop 与 电迁移 EM", "电源完整性的两大约束", "f09_irem.png", [
        "IR drop 即 ΔV=I·R，离电源越远的单元压降越大",
        "压降过大使单元延迟增大、时序变差，甚至功能失效",
        "IR 预算常为 VDD 的百分之几，静态与动态分别约束",
        "EM 指电流密度过大使金属原子迁移，导致开路或短路",
        "PG 网络与高翻转信号线的 EM 机理不同，需分别评估",
        "签核常用 Voltus、RedHawk、PrimeRail 等工具",
    ]),
    split("多电压域与 UPF", "多电压域与 UPF 功耗意图", "f10_mv.png", [
        "让不同区域采用不同电压或可关断，从而降低整体功耗",
        "Level Shifter 转换跨电压域信号电平，如 0.8V 与 1.0V 互转",
        "Isolation 在关断域输出端钳位，防止下游电路浮空",
        "Retention FF 在模块关断期间保持寄存器状态",
        "Always-on Buffer 在关断域内却接常开电源以维持通路",
        "UPF（IEEE 1801）或 CPF 描述功耗意图，floorplan 据此落地",
    ]),
    split("电源门控：power switch / header / footer", "多电压域里可关断模块的实现手段", "f14_gating.png", [
        "对可关断模块插入 Power Switch，实现 Power Gating 门控",
        "Header 是 PMOS 开关，置于 VDD 与虚拟 VVDD 之间，更常用",
        "Footer 是 NMOS 开关，置于虚拟 VVSS 与 VSS 之间，较少单用",
        "floorplan 阶段要规划 switch 阵列布局与 enable 菊花链",
        "菊花链分时开启可抑制唤醒冲击电流 inrush",
    ]),
    split("时序预算与模块划分", "层次化划分与时序预算分配", "f11_budget.png", [
        "层次化设计把芯片按层级切成若干 Block 或 partition",
        "将顶层路径约束拆到各 block 边界，各自生成独立 SDC",
        "预算分配合理时，各块独立收敛再带动顶层收敛",
        "pin 离逻辑越远，块内走线越长，时序 budget 越紧",
        "可用 allocate_budgets、deriveTimingBudget 或 ETM 自动分配",
        "预算含 IO delay、时钟不确定度以及驱动与负载等因素",
    ]),
    split("拥塞 / IR 早期预估与迭代闭环", "拥塞与 IR 的早期预估、迭代收敛", "f15_loop.png", [
        "用全局布线 GR 估算各 GCell 的需求资源比，得到拥塞图",
        "拥塞分两类：区域整体超资源，与引脚密集处 pin-access",
        "热点常出现在 macro notch、窄 channel 与 pin 密集区",
        "缓解手段包括降利用率、加宽 channel、加 partial blockage",
        "用静态 PG 分析早估 IR drop，定位高压降区并加密 mesh",
        "迭代闭环：floorplan、试布局加 GR、评估，再回退调整",
    ]),
    split("输入 / 输出 与 文件作用", "输入、输出与关键文件作用", "f12_io.png", [
        "输入含门级 netlist、LEF、Liberty、SDC、UPF 与预算",
        "输出是带 macro 摆放、PG 与 blockage 的 DEF 文件",
        "还输出 Floorplan 数据库 NDM/OA 及可布线性与时序初评",
        "LEF 提供 site、layer、布线规则及单元与 macro 抽象",
        "DEF 用于交换 die/core、row、macro 位置、pin 与 PG",
        "常用工具为 Synopsys ICC2/FC 与 Cadence Innovus",
    ]),
    {"kind": "cols2", "title": "衡量指标与常见问题", "sub": "关键收敛指标与常见问题对策", "accent": PRIMARY, "cols": [
        ("关键指标", [
            "Core Utilization 核心利用率保持在 0.5–0.8 区间",
            "Aspect Ratio 长宽比接近 1.0，版图尽量方正",
            "Congestion Overflow 拥塞溢出趋近 0，无大片红区",
            "WNS / TNS 均大于等于 0，时序已收敛",
            "Static 与 Dynamic IR 压降各占标称 VDD 百分之几",
            "EM 裕量满足 foundry 的电流密度规则",
        ], PRIMARY),
        ("问题 → 对策", [
            "布线绕不出：降低利用率，或加宽 macro 间 channel",
            "时序收不回：按 dataflow 重摆 macro，并优化 pin",
            "IR drop 超标：加密电源 mesh，并增补 via array",
            "EM 违例：加宽金属线，并联多个 via 分流",
            "Pin 拥塞：增加 halo，调整 pin 所在层与间距",
            "唤醒冲击大：enable 菊花链分时开启 power switch",
        ], PRIMARY),
    ]},
    {"kind": "cards2", "title": "EDA 命令速查（ICC2 / Innovus）", "sub": "选项随版本而异；坑：Innovus margin 四值为 LBRT", "accent": PRIMARY, "cards": [
        ("Synopsys · ICC2 / Fusion Compiler", [
            "initialize_floorplan \\",
            "  -core_utilization 0.70 -side_ratio {1 1}",
            "create_keepout_margin -outer {l b r t}",
            "create_placement_blockage -type hard/soft/partial",
            "create_pg_ring/mesh_pattern + compile_pg",
            "place_pins / set_block_pin_constraints",
            "create_voltage_area      # multi-VDD domain",
        ], PRIMARY),
        ("Cadence · Innovus", [
            "floorPlan -r 1.0 0.7 <L> <B> <R> <T>",
            "addHaloToBlock {l b r t}",
            "createPlaceBlockage -type hard/soft/partial",
            "addRing / addStripe / sroute",
            "editPin / assignIoPins",
            "createPowerDomain        # multi-VDD domain",
            "defIn != floorPlan  (read DEF vs create)",
        ], PRIMARY),
    ]},
    {"kind": "bullets", "title": "本章小结", "sub": "八条核心要点回顾", "accent": PRIMARY, "two_col": True, "bullets": [
        "Floorplan 是 P&R 第一步，定 die/core 几何、macro、PG 与电压域",
        "几何上要分清总利用率与有效利用率（0.5–0.8），长宽比约为 1",
        "macro 沿边沿角按 dataflow 摆放，配 channel、halo、blockage",
        "IO 与 bump 用 pad ring 或 bump array，块级 pin 须落合法 track",
        "电源依 ring→stripe→mesh→rail→sroute 成型，控住 IR/EM",
        "多电压域用 LS/ISO/retention/always-on/switch，由 UPF/CPF 描述",
        "时序预算把顶层约束拆到各 block，pin 位置与 budget 强耦合",
        "迭代闭环：GR 估拥塞、静态 PG 估 IR，收敛后再进 placement",
    ]},
    {"kind": "cols2", "title": "易混淆点 · 课后自测", "sub": "16 题自测：逐题回想要点", "accent": PRIMARY, "cols": [
        ("课后自测 1–8", [
            "Utilization 过高、过低各有何后果？",
            "Halo 与 Placement Blockage 有何区别？",
            "Hard / Soft / Partial Blockage 各限制什么？",
            "Placement 与 Routing Blockage 分别限制什么？",
            "Level Shifter 与 Isolation 各解决什么？",
            "Retention FF 与 Always-on Buffer 各保什么？",
            "Header 与 Footer 各门控哪条电源？",
            "IR Drop 与 EM 各影响什么？",
        ], PRIMARY),
        ("课后自测 9–16", [
            "Ring / Stripe / Mesh / Rail / sroute 各起何作用？",
            "Flyline 飞线在 floorplan 起什么作用？",
            "Core Utilization 与 Placement Density 有何区别？",
            "UPF 与 CPF 分别归属哪两家？",
            "Aspect Ratio 为何偏好接近 1.0？",
            "为什么相邻标准单元行要上下翻转？",
            "defIn 与 floorPlan 语义有何不同？",
            "Voltus / RedHawk / PrimeRail 各属哪家厂商？",
        ], PRIMARY),
    ]},
    {"kind": "close", "title": "谢谢 · Thanks",
     "sub": "下一讲：Placement 标准单元布局（DVD Lecture 7）",
     "line": "绕不出看利用率/channel · 时序差看 macro/pin · IR 超标看 mesh/via · Floorplan 是迭代回环",
     "src": SRC},
]


def main():
    D.build_previews(SPECS, PREV, TOTAL, asset_dir=ASSETS, page_label=FOOTER)
    print("previews ->", PREV, "(", len(SPECS), "pages )")
    try:  # 主版本（干净浅母版）；仅当文件被 PowerPoint 锁住时跳过保存，其余错误照常抛出
        print("pptx ->", D.build_pptx(SPECS, PPTX, TOTAL, asset_dir=ASSETS, page_label=FOOTER))
    except PermissionError as e:
        print("main pptx skipped (file locked by PowerPoint?):", e)


if __name__ == "__main__":
    main()
