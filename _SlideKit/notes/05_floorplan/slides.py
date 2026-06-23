# -*- coding: utf-8 -*-
"""
_SlideKit/notes/05_floorplan/slides.py  (v6 · 对齐教案 5 章结构)
================================================================
与教案 05_Floorplan.md 的【5 章 / 各小节】逐节对应——一小节≈一张 PPT。
小节有图用 split；小节是表用 table（原生可编辑表格）；纯文字用 bullets。
配色：鲜明 IC 学术（靛蓝主色 + 暖橙强调，复用 theme.py 单一真源）。
运行：python slides.py → 可编辑 .pptx + 逐页版面预览。
"""
import os
import sys

_SK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _SK)
import deck as D  # noqa: E402

ROOT = os.path.abspath(os.path.join(_SK, "..", "IC_Backend_Notes"))
ASSETS = os.path.join(ROOT, "assets", "floorplan")
PREV = os.path.join(ROOT, "slides", "_preview")
PPTX = os.path.join(ROOT, "slides", "05_Floorplan.pptx")
SRC = "整理 J.C  ·  源自 Digital VLSI Design (DVD), Prof. Adam Teman, Bar-Ilan University (83-612)"
FOOTER = "Floorplan · 布图规划"   # 左下页脚标签（随笔记而变）；页码用母版 slidenum 字段

PRIMARY = D.PRIMARY
ACCENT = D.ACCENT


def split(t, sub, fig, bullets, style="bullet"):
    return {"kind": "split", "title": t, "sub": sub, "figure": fig, "bullets": bullets, "accent": PRIMARY, "style": style}


def bl(t, sub, bullets, two=False):
    return {"kind": "bullets", "title": t, "sub": sub, "bullets": bullets, "accent": PRIMARY, "two_col": two}


def tbl(t, sub, headers, rows, col_align=None):
    tab = {"headers": headers, "rows": rows}
    if col_align:
        tab["col_align"] = col_align
    return {"kind": "table", "title": t, "sub": sub, "accent": PRIMARY, "table": tab}


def section(num, title, sub, items):
    return {"kind": "section", "num": num, "title": title, "sub": sub, "items": items}


SPECS = [
    {"kind": "cover", "title": "Floorplan 布图规划",
     "tag": "数字 IC 后端 · 从 RTL 到 GDS · DVD Lecture 6",
     "sub": "把逻辑网表落成可实现的物理骨架",
     "line": "一步错，步步错 —— Floorplan 决定 PPA 上限",
     "src": SRC},

    {"kind": "agenda", "title": "本讲导览  Agenda", "sub": "按工程决策顺序展开的五章",
     "sections": [
        ("1", "认识 Floorplan", "定位、目标、输入输出与导入前提"),
        ("2", "几何与空间约束", "尺寸、利用率、宏、区域与阻挡"),
        ("3", "层次化接口", "扁平/层次、时序预算、引脚与穿通"),
        ("4", "电源规划与完整性", "PDN、IR/EM、电源网格与宏摆放"),
        ("5", "工具流程与收束", "Innovus 流程、判断一个好 Floorplan"),
     ],
     "line": "主线：Floorplan 决定后端天花板，是“试布局→评估→回退”的迭代闭环"},

    # ===== 第 1 章 认识 Floorplan =====
    section("1", "认识 Floorplan", "从逻辑网表到物理骨架，做后端第一层承诺",
            ["1.1 从逻辑网表到物理骨架", "1.2 沿主线反查", "1.3 Floorplan 的目标",
             "1.4 全芯片设计视角", "1.5 输入、输出与导入前提"]),
    bl("1.1 从逻辑网表到物理骨架", "进入物理世界的第一层承诺", [
        "综合后的门级网表只说明实例与连接，不含任何物理位置",
        "Floorplan 把逻辑网表落成可实现的物理骨架，至少包括：",
        "晶粒 die 边界与核心区 core；IO / 焊盘 / 凸点的大致位置",
        "硬宏的位置、朝向与固定状态；标准单元可放置区",
        "电源环 / 条带 / 网格 / 供电轨；阻挡 / 留边 / 区域约束",
        "此阶段改动成本低，签核阶段再改则牵一发而动全身",
    ]),
    tbl("1.2 沿主线反查：现象 → 优先方向", "遇到问题沿同一条路径排查", ["现象", "优先反查"], [
        ["布线拥塞", "利用率、宏通道、引脚可达性、布线阻挡"],
        ["时序变差", "宏单元 / 引脚位置、层次化时序预算、长绕线"],
        ["IR 压降超标", "电源焊盘、电源网格、过孔（via）、高功耗宏单元位置"],
        ["EM 风险", "电流密度、金属宽度、过孔阵列、高功耗集中区"],
    ]),
    split("1.3 Floorplan 的目标", "本质是逻辑→物理的映射", "f01_position.png", [
        "映射：netlist（谁连谁）→ floorplan（谁放哪、怎么连、怎么供电）",
        "同时服务三个目标：减小芯片面积",
        "减小关键路径延迟",
        "减小布线拥塞",
        "三者天然冲突：压面积→拥塞，留宽通道→浪费，强网格→抢信号",
        "因此是面积/时序/拥塞/供电的第一轮工程取舍",
    ], style="num"),
    tbl("1.4 全芯片设计视角", "floorplan 要同时回答的 8 类问题", ["对象", "Floorplan 阶段要回答的问题"], [
        ["芯片尺寸", "晶粒 / 模块有多大，长宽比如何"],
        ["核心放置区", "标准单元可放置区在哪里，利用率多少"],
        ["对外接口", "IO 焊盘 / 凸点 / 封装引脚如何对应"],
        ["Hard IP / Macros", "SRAM、ROM、PLL、模拟 IP 等硬块放在哪里"],
        ["电源传输", "电源焊盘数量与位置，电源网格 / 环 / 条带怎么建"],
        ["多电压", "电源域、电压岛、always-on 资源如何预留"],
        ["时钟方案", "时钟分布是否需要特殊通道或宏单元位置配合"],
        ["扁平 / 层次化", "整颗一次实现，还是切成多个模块实现"],
    ]),
    split("1.5 输入、输出与导入前提", "吃什么，吐出可继续用的数据库", "f12_io.png", [
        "输入：设计网表、面积需求、电源需求",
        "输入：时序约束、物理分区、IO / 宏单元提示（可选，省迭代）",
        "输出：晶粒 / 模块面积，IO 已摆放，硬宏已摆放并固定",
        "输出：电源网格初步设计、必要的电源预布线",
        "输出：标准单元可放置区，阻挡 / 留边 / 区域约束入库",
        "输出：可布线性、时序与电源完整性的早期评估",
    ]),

    # ===== 第 2 章 几何与空间约束 =====
    section("2", "几何与空间约束", "尺寸、利用率、宏、区域与阻挡",
            ["2.1 IO 环与芯片尺寸", "2.2 利用率与试布线", "2.3 网表唯一化", "2.4 硬宏摆放",
             "2.5 布局区域", "2.6 阻挡与留边", "2.7 布线阻挡与好 Floorplan"]),
    split("2.1 IO 环与芯片尺寸", "由外到内 + 核心受限 / 焊盘受限", "f03_geometry.png", [
        "几何由外到内：Die ＞ IO/Pad Ring ＞ Core ＞（宏 + 标准单元行）",
        "IO 引脚由前端 / 系统 / 封装提出，但物理设计必须参与评审",
        "IO 不随工艺缩小、面积贵；还兼供电，直接影响 IR 与 EM",
        "核心受限：尺寸由逻辑规模 / 宏 / 布线资源决定 → 优化利用率与摆放",
        "焊盘受限：尺寸由 IO 数量 / 焊盘间距 / 封装决定 → 优化 IO 环与协同",
    ]),
    split("2.2 利用率与试布线", "两个口径 + 必须试布线验证", "f04_util.png", [
        "Floorplan 利用率 = 标准单元占核心区比例，常见初值约 70%",
        "太高 → 拥塞上升、合法化 / 优化自由度不足、局部拥塞、抢 PG 资源",
        "太低 → 浪费晶粒面积、平均互连变长",
        "总利用率 =（Σ单元 + Σ宏）/ 核心区面积",
        "有效利用率 = Σ单元 /（核心区 − 阻挡 − 宏留边 − 禁布区）",
        "不能只凭利用率定尺寸：先跑试布线 / 全局布线估拥塞再决定",
    ]),
    split("2.3 网表唯一化", "物理实现前每个子模块只引用一次", "f16_uniquify.png", [
        "进入物理域前网表必须唯一化：每个子模块只被引用一次",
        "物理优化要按实例独立移动、插缓冲、优化",
        "若两实例共享模块定义，优化 m1/u1 会牵连 m2/u1",
        "唯一化后各实例有清晰的物理优化边界",
        "由综合工具或设计导入阶段完成，必须在布局之前",
    ]),
    split("2.4 硬宏摆放", "把大宏推到边角，留完整大矩形", "f06_macro.png", [
        "硬宏 = SRAM/ROM/PLL/模拟 IP：面积大、形状 / 引脚固定、不可拆",
        "沿边 / 沿角摆放，不在核心中心挖洞",
        "按数据流就近，用飞线 flyline 看连接权重",
        "宏间 / 宏与边界留足信号、电源、时钟通道",
        "必要时旋转宏改善引脚可达性，引脚避开窄通道 / 角落",
        "摆好后标记固定；高功耗宏勿放芯片中心太深（供电路径长）",
    ]),
    tbl("2.5 布局区域：表达放置意图", "越硬越易局部拥塞，仅用于必要结构性意图", ["类型", "含义", "强度"], [
        ["软引导 soft guide", "希望这些单元聚在一起，但无固定区域", "最软"],
        ["引导区域 guide", "尽量放在指定区域", "较软"],
        ["区域约束 region", "指定单元必须放该区域，其他单元也可进入", "较硬"],
        ["围栏约束 fence", "指定单元必须放该区域，其他单元不可进入", "最硬"],
    ], col_align=["l", "l", "c"]),
    split("2.6 阻挡与留边", "限制放置 + 给布线留活路", "f07_halo.png", [
        "布局阻挡限制标准单元摆放，分三种：",
        "hard 完全禁放；soft 初始禁、优化阶段可放 buffer / inverter",
        "partial 限制区域最大密度（例如最多 40%）",
        "留边 halo（padding / keepout）：宏外围一圈空白，改善引脚可达性",
        "关键区别：halo 跟随宏移动，blockage 多为固定坐标",
    ]),
    bl("2.7 布线阻挡与好 Floorplan", "限制走线 + 图上可见的好特征", [
        "布线阻挡限制走线（非摆放），可指定层或层范围（如禁 M1–M3）",
        "用途：保护宏上方特区、给电源预留资源、护噪声敏感模拟区",
        "好 floorplan：保持单个大的核心放置区",
        "大块 RAM 放角落 / 边缘，保留宽布线通道",
        "避免收缩狭窄通道，不让大量引脚对着窄通道",
        "必要时旋转宏改善引脚可达性，引脚不挤在模块角落",
        "用阻挡 / 留边提前保护可布线性",
    ], two=True),

    # ===== 第 3 章 层次化接口与时序预算 =====
    section("3", "层次化接口与时序预算", "扁平 / 层次、时序预算、引脚与穿通",
            ["3.1 扁平 vs 层次化设计", "3.2 时序预算与 ILM", "3.3 引脚分配与穿通"]),
    split("3.1 扁平 vs 层次化设计", "大芯片切块换运行时间 / 复用", "f17_hier.png", [
        "扁平流程一次跑完整颗芯片 → 运行时间与内存压力大",
        "层次化把全芯片切成多个模块，各自 P&R，顶层再做全芯片时序 / 验证",
        "优点：EDA 运行更快、内存更少、ECO 更快、利于复用",
        "代价：全芯片时序收敛更难",
        "代价：引脚分配 / 穿通更关键，时序约束预算更复杂",
        "代价：模块抽象 ILM / ETM 需要维护",
    ]),
    split("3.2 时序预算与 ILM", "顶层约束映射到模块边界", "f11_budget.png", [
        "芯片级约束必须映射成模块级约束",
        "在模块边界建立输入 / 输出延迟、时钟不确定度、负载、驱动单元",
        "预算合理 → 各模块独立收敛后全芯片才容易收敛",
        "预算不合理 → 单模块看似通过，全芯片仍可能失败",
        "ILM 只保留接口相关逻辑、隐藏模块内部细节",
        "ETM 提供抽象时序模型；二者都让全芯片分析更快、更可控",
    ]),
    split("3.3 引脚分配与穿通", "顶层 IO 与模块 pin 影响点不同", "f13_iopad.png", [
        "顶层 IO 摆放决定对外接口，影响封装 / ESD / 电源焊盘 / 边界",
        "模块级引脚决定层次化模块间连接、布线、时序预算与收敛",
        "模块 pin 约束：布线层、间距、尺寸、重叠、网络分组、引导区、数据流方向",
        "无通道 / 通道紧张的设计中 feedthrough 很关键",
        "信号穿过无 feedthrough 的中间分区，会被迫绕过整块",
        "解法：在中间分区生成 feedthrough 引脚 / 网络，把跨越拆成几段",
    ]),

    # ===== 第 4 章 电源规划与完整性 =====
    section("4", "电源规划与完整性", "PDN、IR / EM、电源网格与宏摆放",
            ["4.1 电源规划：功耗与可靠性", "4.2 IR 压降", "4.3 电迁移 EM", "4.4 PDN 的基本取舍",
             "4.5 电源 / 地布线方式", "4.6 电源网格创建", "4.7 电源网格与宏摆放"]),
    split("4.1 电源规划：功耗与可靠性", "PDN 不只是连上 VDD/GND", "f08_power.png", [
        "电源规划关系动态功耗、静态漏电、IR、电压跌落、EM、自热磨损",
        "PDN 要把电流从焊盘 / 凸点送到晶体管",
        "保持稳定低噪声电压，提供平均与峰值功耗需求",
        "为信号提供返回路径，避免 EM 与自热磨损",
        "合理占用芯片面积与布线资源",
        "从 floorplan 阶段就开始，而非布线后补救",
    ]),
    split("4.2 IR 压降", "ΔV=I·R，细长低层线扛不住", "f09_irem.png", [
        "IR 压降是供电线上的电压下降：ΔV = I · R",
        "工具建电阻矩阵 + 各门平均电流，求解每个节点电压",
        "实际电压低于容差 → 延迟增大、时序失败，严重时功能错误",
        "估算：1mm×100nm 的 M1 轨（0.1Ω/□）线阻约 1000Ω",
        "承载约 0.1mA 时 IR 压降可达约 100mV",
        "结论：必须用更宽 / 更厚 / 更高层 / 多路径 / 多过孔的结构",
    ]),
    bl("4.3 电迁移 EM", "长期电流密度能不能扛住", [
        "EM：电流长期流过导体，电子动量推动金属原子迁移",
        "开路：单根线上形成空洞（void）",
        "短路：相邻线之间桥接（bridging）",
        "RC 改变：即使不开 / 不短路，也可能造成性能退化",
        "IR 偏“瞬时电压够不够”，EM 偏“长期电流密度扛不扛”",
        "二者都与 floorplan 有关：焊盘、高功耗宏位置、网格宽度 / 间距 / 过孔早期就定",
    ], two=True),
    tbl("4.4 PDN 的基本取舍", "电源越强越可靠，但越抢信号资源", ["选择", "好处", "代价"], [
        ["更宽电源线", "降低电阻与 IR 压降", "占用布线轨道"],
        ["更多电源条带", "提供更多电流路径", "增加信号拥塞"],
        ["更多过孔阵列", "降低垂直连接电阻与 EM 风险", "占用局部布线资源"],
        ["更靠近电源焊盘", "缩短供电路径", "可能牺牲数据流"],
    ]),
    tbl("4.5 电源 / 地布线方式", "自上而下的六层结构", ["结构", "作用"], [
        ["电源焊盘 / 凸点", "从封装引入 VDD/VSS"],
        ["电源环 power ring", "围绕芯片 / 核心区 / hard IP 的主干环"],
        ["电源条带 power stripe", "横跨核心区分担电流"],
        ["电源网格 power mesh", "纵横条带互连，降低等效电阻"],
        ["标准单元供电轨 rail", "沿标准单元行连接每个单元的 VDD/VSS"],
        ["专用布线 special route", "连接焊盘 / 环 / 条带 / 引脚 / follow-pin 并打过孔"],
    ]),
    bl("4.6 电源网格创建", "在 IR / EM 与布线资源间取舍", [
        "本质是在 IR、EM 与布线资源之间取舍",
        "先要功耗预算与初始估算：平均电流、最大电流密度",
        "决定：总体网格结构、是否门控 / 多电压、各域电源焊盘数量与位置",
        "决定：用哪些金属层、条带宽度 / 间距、过孔堆栈占多少轨道",
        "决定：要不要电源环、层次化模块是否需要屏蔽",
        "命令骨架：globalNetConnect → addRing → addStripe → sroute，先做初始电源网络分析",
    ]),
    split("4.7 电源网格与宏摆放", "高功耗宏要看供电路径", "f18_pgmacro.png", [
        "高功耗模块摆放不能只看数据流，还要看供电路径",
        "高功耗模块靠近边界电源焊盘",
        "高功耗模块之间不要过度集中",
        "宏通道不只给信号，也给电源条带、过孔、时钟预留",
        "电源焊盘、宏位置与网格密度必须一起迭代",
        "IR 用颜色图找热点；修复常是热点加线 / 加过孔 / 加宽条带 / 移宏",
    ]),

    # ===== 第 5 章 工具流程与收束 =====
    section("5", "工具流程与调试收束", "Innovus 流程、判断一个好 Floorplan",
            ["5.1 Innovus 流程：从初始化到阻挡", "5.2 判断一个好 Floorplan"]),
    split("5.1 Innovus 流程：从初始化到阻挡", "工具无关的流程骨架", "f15_loop.png", [
        "初始化设计：读网表 / LEF / MMMC / SDC / IO 摆放",
        "指定布图规划：尺寸、长宽比、目标利用率",
        "摆放硬宏：绝对 / 相对坐标，标记固定，定义留边与阻挡",
        "定义区域与阻挡：布局区域、布局阻挡、布线阻挡",
        "定义全局电源网：顶层 VDD/GND 映射到 IP 电源 / 地引脚",
        "电源环 → 电源网格 → 分配引脚，形成反复调整的闭环",
    ], style="num"),
    tbl("5.2 判断一个好 Floorplan", "让下游布局 / CTS / 布线 / 签核都有路可走", ["问题", "反查方向", "常见动作"], [
        ["布线绕不出", "利用率、宏通道、引脚可达性", "降利用率、拓宽通道、调引脚、改阻挡"],
        ["时序收不回", "宏单元 / 引脚位置、时序预算", "按数据流重摆宏，重新预算接口路径"],
        ["IR 压降超标", "电源焊盘、网格、过孔、高功耗宏", "加密网格、增加过孔、移动高功耗宏"],
        ["EM 违例", "电流密度、金属宽度、过孔阵列", "加宽金属、并联过孔、分散高功耗模块"],
        ["PG 未连通", "全局电源名、宏电源 / 地引脚、专用布线", "校正 VDD/GND 命名并补专用布线"],
    ]),
    {"kind": "cards2", "title": "附录 · EDA 命令速查（ICC2 / Innovus）", "sub": "选项随版本而异；坑：Innovus margin 四值为 LBRT", "accent": PRIMARY, "cards": [
        ("Synopsys · ICC2 / Fusion Compiler", [
            "initialize_floorplan \\",
            "  -core_utilization 0.70 -side_ratio {1 1}",
            "create_keepout_margin -outer {l b r t}",
            "create_placement_blockage -type hard/soft/partial",
            "create_pg_ring / mesh_pattern + compile_pg",
            "place_pins / set_block_pin_constraints",
            "create_voltage_area   # multi-VDD domain",
        ], PRIMARY),
        ("Cadence · Innovus", [
            "floorPlan -r <ar> <util> <L> <B> <R> <T>",
            "addHaloToBlock {l b r t}",
            "createPlaceBlockage -type hard/soft/partial",
            "globalNetConnect VDD -type pgpin -pin VDD -all",
            "addRing / addStripe / sroute",
            "editPin / assignIoPins",
            "defIn != floorPlan  (read DEF vs create)",
        ], ACCENT),
    ]},
    {"kind": "close", "title": "谢谢 · Thanks",
     "sub": "下一讲：Placement 标准单元布局（DVD Lecture 7）",
     "line": "Floorplan 是迭代回环：试布局 → 评估拥塞/时序/IR → 回退调整 → 收敛后再进详细布局",
     "src": SRC},
]

TOTAL = len(SPECS)


def main():
    D.build_previews(SPECS, PREV, TOTAL, asset_dir=ASSETS, page_label=FOOTER)
    print("previews ->", PREV, "(", len(SPECS), "pages )")
    try:
        print("pptx ->", D.build_pptx(SPECS, PPTX, TOTAL, asset_dir=ASSETS, page_label=FOOTER))
    except Exception as e:
        print("main pptx skipped (locked?):", e)


if __name__ == "__main__":
    main()
