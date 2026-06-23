# -*- coding: utf-8 -*-
"""
_SlideKit/notes/05_floorplan/slides.py  (v6 · 对齐教案 5 章结构)
================================================================
与教案 05_Floorplan.md 的【5 章 / 各小节】逐节对应——一小节≈一张 PPT。
小节有图用 split；小节是表用 table（原生可编辑表格）；纯文字用 bullets。
配色：深清华紫主色 + 暖橙强调（复用 theme.py 单一真源；图/框图用深色实填，不靠浅色透明）。
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
BYLINE = "整理 J.C"   # 封面/封底署名（作者水印）。课程出处等引用统一放参考文献(refs)页，不硬编码进标题页
FOOTER = "Floorplan · 布图规划"   # 左下页脚标签（随笔记而变）；页码用母版 slidenum 字段

PRIMARY = D.PRIMARY
ACCENT = D.ACCENT


def split(t, sub, fig, bullets, style="bullet", diagram=None, credit=None):
    d = {"kind": "split", "title": t, "sub": sub, "figure": fig, "bullets": bullets, "accent": PRIMARY, "style": style}
    if diagram:                 # 右栏改用 PPT 原生框图（可编辑形状）；fig 仍保留供笔记 md 与预览回退
        d["diagram"] = diagram
    if credit:                  # 引用文献插图时的来源标注（图下小字「来源：…」）；见 refs 页与 tools/extract_figs.py
        d["credit"] = credit
    return d


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
     "tag": "数字 IC 后端 · 从 RTL 到 GDS",
     "sub": "把逻辑网表落成可实现的物理骨架",
     "line": "一步错，步步错 —— Floorplan 决定 PPA 上限",
     "src": BYLINE},

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
        "综合后的门级网表只说明实例与连接，不含任何单元、宏、IO 或电源结构的物理位置",
        "Floorplan 把这张逻辑网表落成可实现的物理骨架，是从逻辑世界进入物理世界的第一层承诺",
        "骨架至少包括：晶粒 die 边界与核心区 core，IO / 焊盘 / 凸点的大致位置",
        "硬宏的位置、朝向与固定状态，以及标准单元可放置区",
        "电源环 / 条带 / 网格 / 供电轨，以及阻挡 / 留边 / 区域约束等物理约束",
        "后续布局、CTS、布线与电源签核都沿这个骨架继续细化",
        "此阶段改动成本低，签核阶段再改则可能牵一发而动全身",
    ]),
    tbl("1.2 沿主线反查：现象 → 优先方向", "遇到问题沿同一条路径排查", ["现象", "优先反查"], [
        ["布线拥塞", "利用率、宏通道、引脚可达性、布线阻挡"],
        ["时序变差", "宏单元 / 引脚位置、层次化时序预算、长绕线"],
        ["IR 压降超标", "电源焊盘、电源网格、过孔（via）、高功耗宏单元位置"],
        ["EM 风险", "电流密度、金属宽度、过孔阵列、高功耗集中区"],
    ]),
    split("1.3 Floorplan 的目标", "本质是逻辑→物理的映射", "f01_position.png", [
        "Floorplan 本质是一个映射：把“谁连谁”的逻辑网表，落成实例、IO、宏单元与电源网络在芯片上如何摆放、连接与供电。",
        "它要同时服务三个目标——减小芯片面积、减小关键路径延迟、减小布线拥塞。",
        "但三者天然冲突：面积压太紧会拥塞，通道留太宽会浪费面积，电源网格做太强又抢走信号布线资源。",
        "因此 Floorplan 是在面积、时序、拥塞与供电可靠性之间做的第一轮工程取舍。",
    ], style="prose", diagram="pnr"),
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
    split("1.5 输入、输出与导入前提", "每项输入各有作用，输出须可继续用", "f12_io.png", [
        "输入·设计网表给实例与连接；面积需求 → 估核心尺寸、利用率与宏空间",
        "输入·电源需求 → 定电源焊盘 / 网格 / 高功耗宏位置；时序约束 → 影响划分 / 引脚 / 数据流",
        "输入·物理分区给层次化的模块边界与约束；IO / 宏提示可选，省初期迭代",
        "输出须具体到工具数据库可继续用：晶粒 / 模块面积，IO 与硬宏已摆放并固定",
        "输出：电源网格初步设计、必要电源预布线完成，标准单元可放置区已定义",
        "输出：阻挡 / 留边 / 区域约束入库，可布线性 / 时序 / 电源完整性有早期评估",
    ], diagram="io"),

    # ===== 第 2 章 几何与空间约束 =====
    section("2", "几何与空间约束", "尺寸、利用率、宏、区域与阻挡",
            ["2.1 IO 环与芯片尺寸", "2.2 利用率与试布线", "2.3 网表唯一化", "2.4 硬宏摆放",
             "2.5 布局区域", "2.6 阻挡与留边", "2.7 布线阻挡与好 Floorplan"]),
    split("2.1 IO 环与芯片尺寸", "由外到内 + 核心受限 / 焊盘受限", "ext_die_i9_cc0.jpg", [
        "芯片几何由外到内：晶粒 Die ＞ IO / 焊盘环 ＞ 核心区 Core ＞（宏单元 + 标准单元行）。IO 引脚常由前端、系统或封装侧先提出，但物理设计必须参与评审。",
        "原因有二：一是 IO 不像逻辑晶体管随工艺快速缩小，IO 单元与焊盘面积非常贵；二是 IO 不只传信号还负责供电，电源 / 地焊盘的数量与位置直接影响 IR 压降与 EM。",
        "选尺寸先判断是核心受限还是焊盘受限：核心受限由逻辑规模、宏与布线资源决定芯片大小，重点优化利用率与摆放；焊盘受限由 IO 数量、焊盘间距与封装引脚决定、晶粒已不能再小，重点优化 IO 环与封装协同。",
    ], style="prose", credit="Intel i9-13900K die · Fritzchens Fritz / JmsDoug · CC0 · Wikimedia"),
    split("2.2 利用率与试布线", "两个口径 + 必须试布线验证", "f04_util.png", [
        "Floorplan 阶段的利用率通常指标准单元占核心区面积的比例，常见初值约 70%。",
        "利用率太高会带来布线拥塞、合法化与优化自由度不足、引脚密集处局部拥塞，以及电源网格与信号抢资源；太低则浪费面积、拉长平均互连。",
        "工程上要区分总利用率（含宏）与有效利用率（扣除阻挡、宏留边、禁布区）；但不能只凭利用率定尺寸——完成初始估算后还要跑试布线或全局布线估拥塞，再决定是否放大核心、调综合、移宏或改引脚。",
    ], style="prose"),
    split("2.3 网表唯一化", "物理实现前每个子模块只引用一次", "f16_uniquify.png", [
        "进入物理域前，网表必须唯一化——每个子模块只被引用一次。这是因为物理优化要按实例独立移动、插缓冲器、做优化。",
        "如果两个实例共享同一个模块定义，工具想优化 m1/u1 时就可能同时改变 m2/u1，物理优化边界不清晰。",
        "综合后的网表必须在布局之前完成唯一化：可以由综合工具完成，也可以在设计导入阶段完成。",
    ], style="prose", diagram="uniquify"),
    split("2.4 硬宏摆放", "把大宏推到边角，留完整大矩形", "f06_macro.png", [
        "硬宏含 SRAM/ROM/PLL/模拟 IP / 第三方 hard IP：面积大、形状 / 引脚固定，内部不可被摆放器拆开",
        "主线：把大宏推到边缘或角落，让标准单元区保持一个尽量完整的大矩形",
        "按数据流就近摆放，让强连接的宏与逻辑靠近，用飞线 flyline 看连接权重",
        "宏与宏、宏与边界之间留足信号、电源、时钟通道",
        "必要时旋转宏改善引脚可达性，并避免引脚对着窄通道或角落",
        "位置确定后标记为固定；引线键合下高功耗宏勿放中心太深，否则供电路径长、IR 压力大",
    ], style="num"),
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
        "留边还为缓冲器 / 反相器插入、电源与信号布线留近宏通道",
        "关键区别：halo 跟随宏移动，blockage 多为固定坐标",
    ]),
    bl("2.7 布线阻挡与好 Floorplan", "限制走线 + 图上可见的好特征", [
        "布线阻挡限制走线（非摆放），可指定层或层范围（如禁 M1–M3 在某区域走线）",
        "用途：保护宏单元上方特殊区域，给电源结构预留资源",
        "用途：避免低层金属被不合适的信号占用，保护噪声敏感模拟区",
        "好 floorplan：保持单个大的核心放置区，大块 RAM 放角落 / 边缘",
        "保留宽布线通道，避免收缩狭窄通道，不让大量引脚对着窄通道",
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
    ], diagram="hier"),
    split("3.2 时序预算与 ILM", "顶层约束映射到模块边界", "f11_budget.png", [
        "芯片级约束必须映射成模块级约束。例如顶层某输入到模块的路径预算为 1.5 ns，模块实现时就要在模块边界建立对应的输入 / 输出延迟、时钟不确定性、负载与驱动单元约束。",
        "预算合理时，各模块独立收敛后全芯片才容易收敛；预算不合理时，单个模块看似通过，全芯片仍可能失败。",
        "接口逻辑模型（ILM）保留模块边界附近与接口相关的逻辑、隐藏内部细节；抽取时序模型（ETM）也提供模块的抽象时序模型。二者都让全芯片时序分析更快、更可控。",
    ], style="prose"),
    split("3.3 引脚分配与穿通", "顶层 IO 与模块 pin 影响点不同", "ext_wirebond_ccbysa.jpg", [
        "顶层 IO 摆放决定芯片对外接口位置，影响封装、ESD、电源焊盘与芯片边界；模块级引脚分配则决定层次化模块之间如何连接，影响模块间布线、时序预算、feedthrough 与全芯片收敛。",
        "模块级引脚的约束常包括布线层、引脚间距与尺寸、重叠规则、网络分组、引脚引导区域、数据流方向，以及试布线的边界穿越情况。",
        "在无通道或通道资源紧张的设计中 feedthrough 很关键：若信号从分区 A 经分区 B 到分区 C，而 B 没有 feedthrough，信号可能被迫绕过整个模块。解法是在 B 上生成 feedthrough 引脚 / 网络，把跨越 B 的连接拆成几段。",
    ], style="prose", credit="Wire-bond 实拍 · Mister rf · CC BY-SA 4.0 · Wikimedia"),

    # ===== 第 4 章 电源规划与完整性 =====
    section("4", "电源规划与完整性", "PDN、IR / EM、电源网格与宏摆放",
            ["4.1 电源规划：功耗与可靠性", "4.2 IR 压降", "4.3 电迁移 EM", "4.4 PDN 的基本取舍",
             "4.5 电源 / 地布线方式", "4.6 电源网格创建", "4.7 电源网格与宏摆放"]),
    split("4.1 电源规划：功耗与可靠性", "PDN 不只是连上 VDD/GND", "f08_power.png", [
        "电源规划要解决的不只是“连上 VDD/GND”，它同时关系到动态功耗、静态漏电、IR 压降、电压跌落、电迁移和自热磨损。",
        "电源分布网络（PDN）需要把电流从焊盘 / 凸点送到晶体管，保持稳定低噪声的电压，提供平均与峰值功耗，为信号提供返回路径，避免电迁移与自热，并合理占用面积与布线资源。",
        "因此电源规划从 floorplan 阶段就开始，而不是等布线之后再补救。",
    ], style="prose"),
    split("4.2 IR 压降", "ΔV=I·R，细长低层线扛不住", "f09_irem.png", [
        "IR 压降是供电线上的电压下降，ΔV = I·R。芯片电源网格是个巨大网络，工具建立电阻矩阵、结合每个门的平均电流，求解每个节点的电压。",
        "若实际电压低于容差下限，单元延迟会增加、时序可能失败，严重时功能错误。",
        "一个典型估算：1 mm 长、100 nm 宽的 M1 电源轨，方块电阻 0.1 Ω/□ 时线阻约 1000 Ω，承载约 0.1 mA 时 IR 压降可达约 100 mV——细而长的低层电源线无法单独供电，必须用更宽、更厚、更高层、多路径、多过孔的结构。",
    ], style="prose"),
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
    tbl("4.5 电源 / 地布线方式", "标准做法：上层厚金属做网格 / 条带，下层连 follow-pin，过孔堆栈贯通", ["结构（自上而下）", "所在层 / 位置", "作用"], [
        ["电源焊盘 / 凸点 pad / bump", "封装边界 / 芯片表面", "从封装引入 VDD/VSS"],
        ["电源环 power ring", "上层厚金属，绕芯片 / 核心 / hard IP", "构成供电主干环"],
        ["电源条带 power stripe", "上层厚金属，横跨核心区", "分担电流、缩短供电路径"],
        ["电源网格 power mesh", "纵横条带互连", "互连成网，降低等效电阻"],
        ["标准单元供电轨 follow-pin", "下层金属，沿标准单元行", "把 VDD/VSS 送到每个单元"],
        ["专用布线 special route", "贯穿各层，多重过孔 / 堆栈", "连焊盘 / 环 / 条带 / 引脚 / rail 并打过孔"],
    ], col_align=["l", "l", "l"]),
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
    split("5.1 Innovus 流程：从初始化到阻挡", "工具无关的八步流程骨架", "f15_loop.png", [
        "初始化设计：读入网表 / LEF / MMMC / SDC / IO 摆放信息",
        "指定布图规划：确定布图尺寸、长宽比与目标利用率",
        "摆放硬宏：绝对 / 相对坐标摆放，标记固定，并定义留边与阻挡",
        "定义区域与阻挡：布局区域、布局阻挡、布线阻挡",
        "定义全局电源网：把顶层 VDD/GND 名称映射到 IP 的电源 / 地引脚",
        "创建电源环：建芯片外围电源环，必要时再为 hard IP 单独建环",
        "建立电源网格：含 follow-pin 供电轨、条带 / 网格，并可靠连接 hard IP 电源",
        "分配引脚：定义层次化模块的边界引脚，形成反复调整的闭环",
    ], style="num", diagram="loop"),
    tbl("5.2 判断一个好 Floorplan", "让下游布局 / CTS / 布线 / 签核都有路可走", ["问题", "反查方向", "常见动作"], [
        ["布线绕不出", "利用率、宏通道、引脚可达性", "降利用率、拓宽通道、调引脚、改阻挡"],
        ["时序收不回", "宏单元 / 引脚位置、时序预算", "按数据流重摆宏，重新预算接口路径"],
        ["IR 压降超标", "电源焊盘、网格、过孔、高功耗宏", "加密网格、增加过孔、移动高功耗宏"],
        ["EM 违例", "电流密度、金属宽度、过孔阵列", "加宽金属、并联过孔、分散高功耗模块"],
        ["PG 未连通", "全局电源名、宏电源 / 地引脚、专用布线", "校正 VDD/GND 命名并补专用布线"],
    ]),
    {"kind": "cards2", "title": "附录 · EDA 命令速查（ICC2 / Innovus）", "sub": "选项随工具版本而异；Innovus margin 四值顺序为 L / B / R / T", "accent": PRIMARY, "cards": [
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
    {"kind": "refs", "title": "参考文献 References", "sub": "本讲内容与图示来源", "accent": PRIMARY, "refs": [
        "Adam Teman. Digital VLSI Design (DVD), Lecture 6 — Import Design and Floorplan. Bar-Ilan University, Course 83-612. https://enicslabs.com/academic-courses/dvd-english/",
        "J. M. Rabaey, A. Chandrakasan, B. Nikolić. Digital Integrated Circuits: A Design Perspective. Prentice Hall.",
        "N. H. E. Weste, D. M. Harris. CMOS VLSI Design: A Circuits and Systems Perspective. Addison-Wesley.",
        "IDESA / EPFL — Digital IC design tutorials.",
        "Cadence Innovus User Guide; Synopsys IC Compiler II / Fusion Compiler User Guide（命令与流程参考）.",
        "图（2.1）Intel Core i9-13900K labelled die shot — Fritzchens Fritz / JmsDoug, CC0 公有领域, via Wikimedia Commons.",
        "图（3.3）Aluminium wire-bonding close-up — Mister rf, CC BY-SA 4.0, via Wikimedia Commons.",
    ]},
    {"kind": "close", "title": "谢谢 · Thanks",
     "sub": "下一讲：Placement 标准单元布局",
     "line": "Floorplan 是迭代回环：试布局 → 评估拥塞/时序/IR → 回退调整 → 收敛后再进详细布局",
     "src": BYLINE},
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
