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


def split(t, sub, fig, bullets, style="bullet", diagram=None, credit=None, caption=None, figs=None, figs_v=False):
    d = {"kind": "split", "title": t, "sub": sub, "figure": fig, "bullets": bullets, "accent": PRIMARY, "style": style}
    if diagram:                 # 右栏改用 PPT 原生框图（可编辑形状）；fig 仍保留供笔记 md 与预览回退
        d["diagram"] = diagram
    if credit:                  # 单图来源标注（图下小字「来源：…」）；见 refs 页与 tools/extract_figs.py
        d["credit"] = credit
    if caption:                 # 单图图注（图下「图 N · …」）
        d["caption"] = caption
    if figs:                    # 多图：[fg(路径,图注,来源)]，右栏渲染、各带图注
        d["figs"] = figs
    if figs_v:                  # 多图上下堆叠（宽图用），默认左右并排
        d["figs_v"] = True
    return d


def fg(f, cap, credit=None):    # 多图条目助手
    d = {"f": f, "cap": cap}
    if credit:
        d["credit"] = credit
    return d


# 正文混合体裁助手（对齐笔记结构）：散文段 P、引导句 L（均无标记、整段）；并列 B(▪)；有序 N(①)
def P(t): return ("p", t)
def L(t): return ("lead", t)
def B(t): return ("b", t)
def N(t): return ("n", t)


def bl(t, sub, bullets, two=False):
    return {"kind": "bullets", "title": t, "sub": sub, "bullets": bullets, "accent": PRIMARY, "two_col": two}


def tbl(t, sub, headers, rows, col_align=None, note=None):
    tab = {"headers": headers, "rows": rows}
    if col_align:
        tab["col_align"] = col_align
    d = {"kind": "table", "title": t, "sub": sub, "accent": PRIMARY, "table": tab}
    if note:                    # 表下说明文字（取自笔记的引言/定义/结论），见 deck._table
        d["note"] = note
    return d


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
    split("1.1 从逻辑网表到物理骨架", "进入物理世界的第一层承诺", "ext_die_486_ccby.jpg", [
        P("综合后的门级网表（gate-level netlist）只说明实例（instance）与网络（net），不含任何单元、宏、IO 或电源结构的物理位置；布图规划（floorplan）就是把它落成可实现的**物理骨架**。"),
        L("这层骨架至少包括："),
        B("晶粒（die）边界与核心区（core）"),
        B("IO / 焊盘（pad）/ 凸点（bump）的大致位置"),
        B("硬宏（hard macro）的位置、朝向与固定状态；标准单元可放置区"),
        B("电源环 / 条带 / 网格 / 供电轨；阻挡（blockage）/ 留边（halo）/ 区域（region）约束"),
        P("后续布局、CTS、布线与电源签核都沿此骨架细化；此阶段改动成本低，签核再改则牵一发而动全身。"),
    ], figs=[
        fg("ext_die_486_ccby.jpg", "真实 486 裸片：7 个功能块构成物理骨架", "Smial · CC BY 3.0 · Wikimedia"),
        fg("ext_wafer_6inch_ccbysa.jpg", "晶圆上成片裸片：一颗 die 即一份 floorplan", "A. Kübelbeck · CC BY-SA 3.0 · Wikimedia"),
    ]),
    tbl("1.2 沿主线反查：现象 → 优先方向", "本讲路线：按工程决策顺序展开，遇问题沿同一路径反查", ["现象", "优先反查"], [
        ["布线拥塞", "利用率、宏通道、引脚可达性、布线阻挡"],
        ["时序变差", "宏单元 / 引脚位置、层次化时序预算、长绕线"],
        ["IR 压降超标", "电源焊盘、电源网格、过孔（via）、高功耗宏单元位置"],
        ["EM 风险", "电流密度、金属宽度、过孔阵列、高功耗集中区"],
    ], note="本章按工程决策顺序展开：先定位 / 目标 / 输入输出 / 设计导入（design import）前提，再到尺寸 / IO 环 / 利用率（utilization）/ 试布线（trial route）/ 宏 / 区域 / 阻挡，随后层次化时序预算（timing budget）/ ILM / 引脚 / 穿通（feedthrough），最后电源 / IR / EM / 网格与 Innovus 流程；**遇问题沿同一路径反查**。"),
    split("1.3 Floorplan 的目标", "本质是逻辑→物理的映射", "f01_position.png", [
        P("Floorplan 本质是一个**映射**：把「谁连谁」的逻辑网表，落成实例、IO、宏单元与电源网络在芯片上如何摆放、连接与供电。"),
        L("它要同时服务三个目标："),
        N("减小芯片面积"),
        N("减小关键路径延迟"),
        N("减小布线拥塞"),
        P("但三者**天然冲突**：面积压太紧会拥塞，通道（channel）留太宽会浪费面积，电源网格做太强又抢走信号布线资源。因此 Floorplan 是在面积、时序、拥塞与供电可靠性之间做的**第一轮工程取舍**。"),
    ], diagram="pnr"),
    tbl("1.4 全芯片设计视角", "floorplan 要同时回答的 8 类问题，它们互相抢空间", ["对象", "Floorplan 阶段要回答的问题"], [
        ["芯片尺寸", "晶粒 / 模块有多大，长宽比（aspect ratio）如何"],
        ["核心放置区", "标准单元可放置区在哪里，利用率多少"],
        ["对外接口", "IO 焊盘 / 凸点 / 封装引脚（package pin）如何对应"],
        ["Hard IP / Macros", "SRAM、ROM、PLL、模拟 IP 等硬块放在哪里"],
        ["电源传输", "电源焊盘数量和位置，电源网格、环、条带怎么建"],
        ["多电压", "电源域（power domain）、电压岛（voltage island）、always-on 资源如何预留"],
        ["时钟方案", "时钟分布（clock distribution）是否需要特殊通道或宏单元位置配合"],
        ["扁平 / 层次化", "整颗芯片一次实现，还是切成多个模块（block）实现"],
    ], note="**越早把这些结构决定清楚，修改成本越低**；拖到 CTS、布线或签核阶段才发现问题，返工成本会迅速上升。"),
    split("1.5 输入、输出与导入前提", "输入各有作用，输出须可继续用", "f12_io.png", [
        L("输入至少需要 6 项，各有作用："),
        B("__设计网表（design netlist）__：提供实例与连接关系"),
        B("__面积需求（area requirements）__：估算核心区尺寸、利用率与宏单元空间"),
        B("__电源需求（power requirements）__：决定电源焊盘、网格、高功耗宏位置"),
        B("__时序约束（timing constraints）__：影响模块划分、引脚分配、宏数据流"),
        B("__物理分区（physical partitioning）__：给层次化的模块边界与约束；IO / 宏提示减少初期迭代"),
        L("输出须具体到工具数据库可继续使用："),
        B("晶粒或模块面积已定，IO 已摆放，硬宏已摆放并固定"),
        B("电源网格初步设计、必要电源预布线（power pre-routing）完成，标准单元可放置区已定义"),
        B("阻挡 / 留边 / 区域约束入库，可布线性（routability）/ 时序 / 电源完整性已有早期评估"),
    ], diagram="io"),

    # ===== 第 2 章 几何与空间约束 =====
    section("2", "几何与空间约束", "尺寸、利用率、宏、区域与阻挡",
            ["2.1 IO 环与芯片尺寸", "2.2 利用率与试布线", "2.3 网表唯一化", "2.4 硬宏摆放",
             "2.5 布局区域", "2.6 阻挡与留边", "2.7 布线阻挡与好 Floorplan"]),
    split("2.1 IO 环与芯片尺寸", "由外到内 + 核心受限 / 焊盘受限", "ext_die_i9_cc0.jpg", [
        P("芯片几何**由外到内**（外层含内层）：晶粒 Die ＞ IO / 焊盘环（Pad Ring）＞ 核心区 Core ＞（宏单元 + 标准单元行）。"),
        L("IO 引脚分配常由前端、系统或封装侧先提出，但物理设计（physical design）必须参与评审，原因有二："),
        N("IO 不像逻辑晶体管那样随工艺快速缩小，IO 单元与焊盘面积非常贵"),
        N("IO 不只传信号还负责供电，电源焊盘（power pad）与地焊盘（ground pad）的数量、位置直接影响 IR 压降与 EM"),
        L("选芯片尺寸先判断**核心受限还是焊盘受限**："),
        B("核心受限（core limited）：逻辑规模、宏单元与布线资源决定芯片大小，重点优化利用率、宏单元摆放与布线资源"),
        B("焊盘受限（pad limited）：IO 数量、焊盘间距（pad pitch）与封装引脚分配决定晶粒已不能再小，重点优化 IO 环、焊盘 / 凸点分配与封装协同"),
    ], figs=[
        fg("f03_geometry.png", "芯片几何：Die ＞ IO/焊盘环 ＞ Core ＞ 标准单元行"),
        fg("ext_die_i9_cc0.jpg", "真实多核 die：核心 / 缓存 / GPU 等功能块", "Fritzchens Fritz / JmsDoug · CC0 · Wikimedia"),
    ]),
    split("2.2 利用率与试布线", "两个口径 + 必须试布线验证", "ext_congest_verihgn_ccby.png", [
        P("利用率（utilization）通常指**标准单元占核心区面积的比例**，常见初值约 70%。"),
        L("利用率太高会导致五方面问题："),
        B("布线拥塞上升；布局合法化（placement legalization）与优化自由度不足"),
        B("引脚密集单元（pin-dense cell）周围局部拥塞；电源网格与信号布线抢资源"),
        B("时序优化难以插入缓冲器（buffer）或调整位置"),
        P("太低则浪费晶粒 / 模块面积、拉长平均互连。工程上区分两个口径：**总利用率** =（Σ标准单元 ＋ Σ宏单元）/ 核心区；**有效利用率** = Σ标准单元 /（核心区 − 阻挡 − 宏留边 − 禁布区 − …）。"),
        P("但不能只凭利用率定尺寸：完成初始面积估算后，还要跑快速试布线或全局布线（global routing）估拥塞，再决定是否放大核心区、调整综合、移动宏单元、修改引脚分配或重分配布线资源。"),
    ], figs_v=True, figs=[
        fg("ext_congest_verihgn_ccby.png", "拥塞如何形成：逻辑块→布线竞争→热力图", "VeriHGN, Hu et al. · arXiv:2603.11075 · CC BY 4.0"),
        fg("ext_congest_heatmap_ccby.jpg", "真实版图上的拥塞预测热力图（jet 配色）", "Tsai et al. · arXiv:2510.15872 · CC BY 4.0"),
    ]),
    split("2.3 网表唯一化", "物理实现前每个子模块只引用一次", "f16_uniquify.png", [
        P("进入物理域前，网表必须**唯一化**——每个子模块只被引用一次。这是因为物理优化要按实例独立移动、插缓冲器、做优化。"),
        P("如果两个实例共享同一个模块定义（module definition），工具想优化 m1/u1 时就可能**同时改变 m2/u1**，物理优化边界不清晰。"),
        P("综合后的网表必须在**布局之前**完成唯一化：可以由综合工具完成，也可以在设计导入阶段完成。"),
    ], diagram="uniquify"),
    split("2.4 硬宏摆放", "把大宏推到边角，留完整大矩形", "f06_macro.png", [
        P("硬宏（hard macro）含 SRAM、ROM、PLL、模拟 IP、第三方 hard IP：面积大、形状 / 引脚固定，内部不可被摆放器（placer）拆开；**主线是把大宏推到边缘或角落**，让标准单元区保持完整大矩形。"),
        L("常用原则："),
        N("沿边 / 沿角：大宏靠核心区边界或角落，不在中心挖洞"),
        N("按数据流（dataflow）就近：用飞线（flyline）看连接权重"),
        N("保留布线通道：宏与宏、宏与边界留足信号 / 电源 / 时钟通道"),
        N("改善引脚可达性（pin accessibility）：旋转宏，避免引脚对着窄通道或角落"),
        N("摆好后固定：硬宏位置确定后标记为固定"),
        P("引线键合（wire-bond）下高功耗宏勿放中心太深——电源焊盘多在边缘，供电路径越长 IR 压力越大。"),
    ], style="num", figs=[
        fg("ext_die_ultrasparc_ccbysa.jpg", "真实 die：8 核 + L2 缓存等存储宏沿核区分布",
           "UltraSPARC T1 · ZyMOS / Fritzchens Fritz · CC BY-SA 3.0"),
        fg("ext_floorplan_compare_ccbysa.png", "宏摆放对比：人工分区 vs 规则 AI",
           "Copparihollmann · CC BY-SA 4.0 · Wikimedia"),
        fg("ext_sram_hitachi_ccbysa.jpg", "存储宏内部：规则的 SRAM 位单元阵列",
           "Seanriddle · CC BY-SA 4.0 · Wikimedia"),
    ]),
    tbl("2.5 布局区域：表达放置意图", "帮 P&R 工具表达放置意图：从软引导到围栏，约束由软到硬", ["类型", "含义", "强度"], [
        ["软引导 soft guide", "希望这些单元聚在一起，但无固定区域", "最软"],
        ["引导区域 guide", "尽量放在指定区域", "较软"],
        ["区域约束 region", "指定单元必须放该区域，其他单元也可进入", "较硬"],
        ["围栏约束 fence", "指定单元必须放该区域，其他单元不可进入", "最硬"],
    ], col_align=["l", "l", "c"], note="布局区域（placement region）是帮助布局布线工具（P&R tool）表达设计意图的方式，用来引导或限制某些单元的摆放区域。越硬的约束越容易制造局部拥塞，因此区域约束 / 围栏约束应**只用于必要的结构性意图**，而不是用来「替工具做布局」。"),
    split("2.6 阻挡与留边", "布局阻挡限制放置（三种），留边给宏通道留活路", "ext_blockage_floorset_ccby.png", [
        P("布局阻挡（placement blockage）用于**限制标准单元摆放**。"),
        L("按强度分三种："),
        B("__硬阻挡（hard）__：完全禁止放置标准单元"),
        B("__软阻挡（soft）__：初始布局禁用，优化阶段可放缓冲器（buffer）/ 反相器（inverter）"),
        B("__部分阻挡（partial）__：限制区域最大密度，例如最多 40%"),
        P("留边（halo，又叫 padding / keepout margin）是宏单元外围一圈空白，主要改善宏引脚可达性，并为缓冲器 / 反相器插入、电源与信号布线留近宏通道。"),
        P("关键区别：留边跟随宏单元移动，而阻挡多为固定坐标区域。"),
    ], caption="在版图上逐步叠加约束：边界 = keepout / 留边，预置 = 固定 / 硬阻挡",
        credit="FloorSet, Mallappa et al. · arXiv:2405.05480 · CC BY 4.0"),
    split("2.7 布线阻挡与好 Floorplan", "用途清单 + 好 floorplan 的图上可见特征", "f07_halo.png", [
        P("布线阻挡（routing blockage）**限制走线而非单元摆放**，可指定布线层（routing layer）或层范围，例如禁 M1–M3 在某区域走线。"),
        L("常见用途："),
        B("保护宏单元上方的特殊区域，并为电源结构预留布线资源"),
        B("避免低层金属被不合适的信号占用，保护噪声敏感的模拟区"),
        L("好 floorplan 的图上可见特征："),
        B("保持单个大的核心放置区，RAM 这类大块放在角落或边缘"),
        B("保留宽布线通道，避免收缩出狭窄通道，不让大量引脚对着窄通道"),
        B("必要时旋转宏改善引脚可达性、引脚不挤在角落；用阻挡 / 留边提前保护可布线性（routability）"),
    ], caption="通道 channel / 留边 halo / 阻挡 blockage：给布线留出活路"),

    # ===== 第 3 章 层次化接口与时序预算 =====
    section("3", "层次化接口与时序预算", "扁平 / 层次、时序预算、引脚与穿通",
            ["3.1 扁平 vs 层次化设计", "3.2 时序预算与 ILM", "3.3 引脚分配与穿通"]),
    split("3.1 扁平 vs 层次化设计", "扁平 flat 一次跑完，层次化 hierarchical 切块实现", "f17_hier.png", [
        P("设计太大时，扁平流程（flat flow）一次跑完整颗芯片，会遇到运行时间（runtime）与内存压力。"),
        P("应对办法是**层次化设计（hierarchical design）把全芯片切成多个模块（block）**：各模块独立做布局布线（P&R），再在顶层做全芯片时序与验证。"),
        L("优点："),
        B("__EDA 运行时间__：更短，内存占用更少"),
        B("__ECO 周期__：更快，迭代更轻"),
        B("__设计复用__：模块可跨项目重用"),
        L("代价：换来的是更重的边界规划——层次化不会让问题消失，只是把「大问题」拆成更清楚的「边界问题」："),
        B("__全芯片时序收敛__：跨模块更难收敛，需提前做时序预算（timing budget）"),
        B("__穿通与中继器__：要提前处理穿通（feedthrough）生成与中继器插入"),
        B("__模块抽象__：ILM / 抽取时序模型（ETM）等接口模型需维护"),
    ], diagram="hier"),
    split("3.2 时序预算与 ILM", "顶层约束映射到模块边界", "ext_block_floorplan_parsac_ccbysa.png", [
        P("**芯片级约束（chip-level constraints）必须映射成模块级约束（block-level constraints）**。例如顶层某输入到模块的路径预算为 1.5 ns，模块实现时就要在模块边界建立对应的输入延迟（input delay）、输出延迟（output delay）、时钟不确定性（clock uncertainty）、负载（load）与驱动单元（driving cell）等约束。"),
        P("**预算合理**时，各模块独立收敛后全芯片才容易收敛；预算不合理时，单个模块看似通过，全芯片仍可能失败。"),
        P("**接口逻辑模型（Interface Logic Model，ILM）**保留模块边界附近与接口时序相关的逻辑、隐藏内部细节；抽取时序模型（Extracted Timing Model，ETM）也提供模块的抽象时序模型。二者都让全芯片时序分析**更快、更可控**。"),
    ], figs_v=True, figs=[
        fg("ext_pdflow_parsac_ccbysa.png", "物理设计流程：分区 → 层次化布图 → … → 时序收敛", "PARSAC · arXiv:2405.05495 · CC BY-SA 4.0"),
        fg("ext_block_floorplan_parsac_ccbysa.png", "层次化分块布图：块边界 b1–b11 + B*-tree", "PARSAC · arXiv:2405.05495 · CC BY-SA 4.0"),
    ]),
    split("3.3 引脚分配与穿通", "顶层 IO 与模块引脚影响点不同，穿通是层次化关键", "ext_wirebond_ccbysa.jpg", [
        P("顶层 IO 摆放决定芯片对外接口位置，模块级引脚分配（pin assignment）决定层次化模块之间如何连接；**两者都属于 floorplan，但影响点不同**："),
        B("__顶层 IO__：影响封装、静电防护（ESD）、电源焊盘与芯片边界"),
        B("__模块引脚__：影响模块间布线、时序预算、穿通（feedthrough）与全芯片收敛"),
        P("模块级引脚的约束常包括布线层、引脚间距与尺寸、重叠规则、网络分组、引脚引导区域（pin guide）、数据流方向，以及试布线的边界穿越情况。"),
        P("无通道（channel-less）或通道资源紧张的设计中**穿通很关键**：信号从分区 A 经 B 到 C，若 B 没有穿通，信号可能被迫绕过整个模块。解法是在 B 上生成穿通引脚 / 穿通网络，把跨越 B 的连接拆成几段。"),
    ], figs=[
        fg("ext_wirebond_ccbysa.jpg", "引线键合特写：金线焊到封装", "Mister rf · CC BY-SA 4.0 · Wikimedia"),
        fg("ext_wirebond_pkg_ccbysa.jpg", "开盖芯片：裸片经键合线接到封装引脚", "Mister rf · CC BY-SA 4.0 · Wikimedia"),
    ]),

    # ===== 第 4 章 电源规划与完整性 =====
    section("4", "电源规划与完整性", "PDN、IR / EM、电源网格与宏摆放",
            ["4.1 电源规划：功耗与可靠性", "4.2 IR 压降", "4.3 电迁移 EM", "4.4 PDN 的基本取舍",
             "4.5 电源 / 地布线方式", "4.6 电源网格创建", "4.7 电源网格与宏摆放"]),
    split("4.1 电源规划：功耗与可靠性", "电源规划（Power Planning）：PDN 不只是连上 VDD/GND", "ext_pdn_bitfury_ccby.jpg", [
        P("电源规划（Power Planning）要解决的**不只是「连上 VDD/GND」**，它同时关系到动态功耗（dynamic power）、静态漏电（static leakage）、IR 压降、电压跌落（voltage drop）、电迁移（electromigration）与自热磨损（self-heating wearout）。"),
        L("**电源分布网络（Power Distribution Network，PDN）**需要："),
        B("把电流从焊盘 / 凸点送到晶体管，保持稳定、低噪声的电压"),
        B("提供平均和峰值功耗需求，为信号提供返回路径"),
        B("避免电迁移和自热磨损，合理占用芯片面积与布线资源"),
        P("电源规划**从 floorplan 阶段就开始**，而不是布线后的补救。"),
    ], caption="真实芯片顶层金属：几乎整层用于供电网", credit="Bitfury 顶层金属供电网 · ZeptoBars · CC BY 3.0 · Wikimedia"),
    split("4.2 IR 压降", "ΔV=I·R，细长低层线扛不住", "ext_irdrop_waca_ccby.png", [
        P("IR 压降是供电线上的电压下降，**ΔV = I·R**。芯片电源网格是个巨大网络，工具建立电阻矩阵、结合每个门的平均电流，求解每个节点的电压。"),
        P("若实际电压**低于容差下限**，单元延迟会增加、时序可能失败，严重时功能错误。"),
        L("一个典型估算说明问题——1 mm 长、100 nm 宽的 M1 电源轨："),
        B("方块电阻（sheet resistance）0.1 Ω/□ 时线阻约 1000 Ω；承载约 0.1 mA 时 IR 压降可达约 100 mV"),
        P("可见**细而长的低层电源线无法单独供电**，必须用更宽、更厚、更高层、多路径、多过孔的结构。"),
    ], caption="静态 IR 压降颜色图 + 热点掩码", credit="WACA-UNet, Seo et al. · arXiv:2507.19197 · CC BY 4.0"),
    split("4.3 电迁移 EM", "长期电流密度能不能扛住", "f09_irem.png", [
        L("**电迁移（EM）**是**电流长期流过导体、电子动量推动金属原子迁移**，可能导致："),
        B("__开路（open）__：单根线上形成空洞（void）"),
        B("__短路（short）__：相邻线之间桥接（bridging）"),
        B("__RC 改变__：即使没开 / 不短路，也可能造成性能退化"),
        P("IR 更偏**「瞬时电压够不够」**，EM 更偏**「长期电流密度能不能扛住」**。"),
        P("二者都与 floorplan 有关：电源焊盘、高功耗宏位置、网格宽度 / 间距 / 过孔都在早期就定。"),
    ], figs=[
        fg("ext_em_void_ccbysa.jpg", "铜互连电迁移失效 SEM：断裂 / 空洞", "P.-E. Zörner · CC BY-SA 3.0 · Wikimedia"),
        fg("ext_em_alcu_ccby.jpg", "AlCu M2 连续性空洞 SEM（加速 EM 测试）", "Liu et al. · doi:10.3390/mi16040458 · CC BY 4.0"),
    ]),
    tbl("4.4 PDN 的基本取舍", "电源越强越可靠，但越抢信号资源", ["选择", "好处", "代价"], [
        ["更宽电源线", "降低电阻与 IR 压降", "占用布线轨道"],
        ["更多电源条带", "提供更多电流路径", "增加信号拥塞"],
        ["更多过孔阵列", "降低垂直连接电阻与 EM 风险", "占用局部布线资源"],
        ["更靠近电源焊盘", "缩短供电路径", "可能牺牲数据流"],
    ], note="电源线越强，IR / EM 风险越低，但信号布线资源越紧张。所以一个好的**电源分布网络（PDN）**要让电源轨尽量宽、尽量厚、尽量多路径，但**不能把信号布线资源全部吃光**。"),
    tbl("4.5 电源 / 地布线方式", "自上而下的六种结构：从电源焊盘 / 凸点到标准单元供电轨", ["结构", "作用"], [
        ["电源焊盘 / 凸点（power pads / bumps）", "从封装引入 VDD/VSS"],
        ["电源环（power ring）", "围绕芯片 / 核心区 / hard IP 的主干环"],
        ["电源条带（power stripe）", "横跨核心区分担电流"],
        ["电源网格（power mesh）", "纵横条带互连，降低等效电阻"],
        ["标准单元供电轨（std-cell rail）", "沿标准单元行连接每个单元的 VDD/VSS"],
        ["专用布线（special route）", "连接焊盘、环、条带、模块引脚、核心区引脚和 follow-pin rail，并打过孔"],
    ], col_align=["l", "l"], note="标准做法是用**上层厚金属做网格或条带，下层连接到标准单元 follow-pin rail**，中间用多重过孔和过孔堆栈（via stack）连起来。"),
    bl("4.6 电源网格创建", "在 IR / EM 与布线资源间取舍", [
        "本质是**在 IR 压降、EM 与布线资源之间取舍**；开始前要功耗预算与初始估算（平均电流、最大电流密度），再定总体网格结构",
        "决定：总体网格结构；是否有电源门控（power gating）或多电压；各电压域（voltage domain）的电源焊盘数量与位置",
        "决定：用哪些金属层；电源条带的宽度 / 间距；过孔堆栈如何放、占掉多少布线轨道",
        "决定：要不要电源环；层次化模块是否需要屏蔽（shielding）；最后做初始电源网络分析",
        "Innovus 命令骨架：globalNetConnect（映射 VDD/VSS）→ addRing（环）→ addStripe（条带）→ sroute（专用布线打过孔）",
    ]),
    split("4.7 电源网格与宏摆放", "高功耗宏要看供电路径", "ext_irlayout_cfirstnet_ccby.png", [
        P("高性能、高功耗模块的宏单元摆放**不能只看数据流，还要看供电路径**。"),
        L("实用规则："),
        B("高功耗模块靠近边界电源焊盘"),
        B("高功耗模块之间不要过度集中"),
        B("宏通道不仅给信号布线，也要给电源条带、过孔、时钟预留空间"),
        B("电源焊盘、宏单元位置和网格密度必须一起迭代"),
        P("IR 压降通常用颜色图（color map）找热点（hot spot）；修复常是热点附近加电源线 / 加过孔阵列 / 加宽条带 / 移高功耗宏 / 增加或重分配电源焊盘。"),
    ], caption="版图上的 IR 压降热点图（红 = 高压降，预测 vs 金标）",
        credit="CFIRSTNET, Liu et al. · arXiv:2502.12168 · CC BY 4.0"),

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
    ], note="判断标准：好 floorplan 要让下游布局（placement）/ CTS / 布线（routing）/ 电源签核（signoff）**都有路可走**。工作方式是**迭代闭环**：布图规划 → 试布局 → 评估拥塞 / 时序 / IR → 调利用率 / 宏 / 通道 / 引脚 / PG → 收敛后进详细布局；之后不再回答“骨架是什么”。"),

    # ===== 第 6 章 布图规划算法（对齐笔记 §6；图 f2* 由 figures 单元产出，本 worktree 暂缺属预期）=====
    section("6", "布图规划算法", "从发展脉络到具体算法：表示法 + 优化",
            ["6.1 发展脉络", "6.2 切片式布图与模拟退火", "6.3 非切片表示",
             "6.4 现代布图规划", "6.5 工业布图与原型"]),
    split("6.1 发展脉络", "四十年主线：从切片构造到固定轮廓与解析法", "f20_devthread.png", [
        P("布图规划算法要回答两件事：**拓扑生成（topology generation）定谁挨着谁、尺寸确定（sizing）定每块多大**；目标是面积、线长（wirelength）与长宽比，模块分硬块（hard）/ 软块（soft）。"),
        L("沿四十年发展分五个阶段（详见右侧时间轴）："),
        N("__早期构造法__（1980s）：min-cut、矩形对偶，先分可切片 / 不可切片"),
        N("__切片 + 模拟退火__（1986）：切片树 + Polish + 形状曲线 + SA"),
        N("__非切片表示__（1995–2005）：SP / B*-tree / TCG 表达任意紧致布局"),
        N("__现代布图__（2000s）：固定轮廓 + 拥塞 / 缓冲 / 功耗感知"),
        N("__工业布图与原型__：层次预算、可行性闸门"),
        P("驱动力：**表示法越来越通用，目标从「最小面积」转向「塞进给定轮廓且可收敛」**。"),
    ], caption="发展脉络时间轴：早期构造 → 切片+SA → 非切片表示 → 现代固定轮廓 / 解析 / 工业"),

    split("6.2a 切片树与 Polish 表达式", "用一棵二叉树和一个后序串编码切片布图", "f21_slicing.png", [
        P("可切片布图能被一刀刀水平 / 垂直切分到底，天然对应一棵**切片树（slicing tree）**：内部节点是 H（水平割）或 V（垂直割），叶节点是模块。"),
        P("把切片树后序遍历（postorder）写出来，就得到 **Polish 表达式（Polish expression）**——一个长度为 2n−1 的串，例如 `12V3H`，运算符 H/V 紧跟在它要合并的两棵子树之后。"),
        L("为去掉冗余、让串与布图一一对应，要求表达式**规范化（normalized）**："),
        B("对应的切片树是 skewed（无两个连续同号运算符），从而同号链不会有多种等价写法"),
        B("规范化 Polish 表达式与切片布图严格一一对应，是 Wong–Liu 搜索的状态编码"),
        P("切片表示的优点是编码紧凑、打包（packing）快；代价是它**无法表达全部紧致布局**——这正是后来非切片表示出现的原因。"),
    ], caption="切片布图 + 对应 slicing tree（H/V 节点、模块叶）+ 后序 Polish 表达式"),

    split("6.2b Stockmeyer 形状曲线", "软块 / 可旋转块的面积最优靠自底向上合并曲线", "f22_shapecurve.png", [
        P("软块或可旋转块有多种「宽×高」选择，怎样组合才让总面积最小？**Stockmeyer 形状曲线（shape curve）** 用动态规划（DP）给出切片布图的最优解。"),
        P("每个模块的可行形状画成一条**阶梯状的 Pareto 曲线**（宽增则高减）；沿切片树自底向上，把两个子块的曲线合并成父节点曲线。"),
        L("合并规则跟着割的方向走："),
        B("__H 割（水平割）__：两块上下叠放，**高相加、宽取最大** —— 曲线在高度方向相加"),
        B("__V 割（垂直割）__：两块左右并排，**宽相加、高取最大** —— 曲线在宽度方向相加"),
        P("根节点曲线上每个拐点都是一个候选整体形状，挑面积最小且满足长宽比的点即可。Shi 把合并复杂度改进到最优的 O(m log m)。"),
    ], caption="两子块 Pareto 阶梯曲线：H 割竖加（高相加）/ V 割横加（宽相加）→ 父曲线"),

    split("6.2c Wong–Liu 模拟退火", "在规范化 Polish 表达式上做三种局部扰动", "f23_wongliu.png", [
        P("Wong–Liu（1986）用**模拟退火（simulated annealing，SA）**搜索最优切片布图：状态是一条规范化 Polish 表达式，代价函数取 **A + λ·W**（面积加权线长）。"),
        L("从当前状态用三种移动跳到邻居状态："),
        B("__M1（换相邻模块）__：交换 Polish 串里相邻的两个模块操作数"),
        B("__M2（补一段割链）__：把一段连续的运算符整体取反（V 与 H 互换）"),
        B("__M3（换相邻模块与割）__：交换相邻的一个模块操作数与一个运算符（须检查仍合法且规范化）"),
        P("每次移动只动切片树的一小棵子树，**只需增量重算受影响子树的形状曲线**，这让 SA 每步都很便宜——实用的关键。"),
    ], caption="一条 Polish 串上的 M1 / M2 / M3 三种移动前后小例"),

    split("6.3a Sequence Pair", "一对序列 → 约束图 → 最长路定坐标", "f24_seqpair.png", [
        P("**序列对（Sequence Pair，SP）** 是最经典的通用（general）非切片表示：用一对模块排列（正序列 + 负序列，记作 P+ / P−）编码任意布局，解空间大小为 (n!) 的平方。"),
        L("两个序列里的先后顺序唯一确定每对模块的相对位置："),
        B("两块在 P+、P− 中**同序**（都是 a 在 b 前）：a 在 b 左边（水平关系）"),
        B("两块在两序列里**反序**：a 在 b 下边（垂直关系）"),
        P("据此建**水平 / 垂直约束图**（边权=宽 / 高），各跑一次**最长路（longest path）**即得全部坐标，O(n²)（用 LCS 可 O(n log log n)）。"),
        P("SP 通用、能表达任意紧致布局，缺点是**几何关系不透明**——必须真正打包一次才知道布局长什么样。"),
    ], caption="一个 packing + 序列对（P+,P−）+ 水平 / 垂直约束图（源 / 汇 + 最长路）"),

    split("6.3b B*-tree", "单棵有序二叉树 + contour 轮廓线，O(n) 打包", "f25_bstar.png", [
        P("**B\\*-tree** 用单棵有序二叉树编码紧凑布局（admissible placement，即所有块都向左下压实），与这类布局一一对应，因此搜索空间无冗余。"),
        L("树的结构直接编码几何关系（设父块 i、子块 j）："),
        B("__根节点__：左下角的模块，坐标 (0, 0)"),
        B("__左孩子__：右邻块，x 坐标 x_j = x_i + w_i（紧挨在父块右侧）"),
        B("__右孩子__：同 x 上邻块，x_j = x_i（在父块正上方）"),
        P("DFS 一次定出全部 x；y 坐标用**轮廓线（contour）** 在线维护天际线，整体打包 **O(n)** 线性时间。与 O-tree 等价，但单树、实现更简单，故更常用。"),
    ], caption="一个 packing + B*-tree（根=左下，左孩=右邻 x_j=x_i+w_i，右孩=上邻 x_j=x_i）+ contour"),

    split("6.3c TCG 传递闭包图", "用两张闭包图把几何关系做到「打包前可判」", "f26_tcg.png", [
        P("**TCG（传递闭包图，Transitive Closure Graph）** 用两张有向图显式表达关系：水平图 Cₕ（权=宽）放「左于」，垂直图 Cᵥ（权=高）放「下于」。"),
        L("可行 TCG 的三条性质："),
        B("两图都**无环**；每对模块恰由其中一图一条边相连（保证不重叠）"),
        B("每张图的**传递闭包等于自身**（消冗余）"),
        P("打包仍在两图上跑最长路（O(n²)）。卖点是**关系透明**：reverse / move 扰动在**打包前**就知道会如何改变几何关系，利于收敛。"),
        P("**SP ↔ TCG 等价**；**TCG-S** 配一条打包序列把打包降到 O(n log n)。"),
    ], caption="水平 / 垂直传递闭包图 Cₕ / Cᵥ：节点权=宽 / 高，边=左于 / 下于关系"),

    tbl("6.3d 表示法对比", "解空间越大越通用，但打包越慢、关系越不透明——按场景权衡",
        ["表示法", "解空间", "打包复杂度", "通用性", "关系透明"], [
            ["Polish（切片树）", "约切片子集", "O(n)", "仅可切片", "透明"],
            ["Sequence Pair", "(n!)^2", "O(n^2)（可 O(n log log n)）", "通用", "不透明"],
            ["B*-tree / O-tree", "约 O(n! 4^n / n^1.5)", "O(n)", "紧致布局", "半透明"],
            ["CBL（角块列表）", "镶嵌子集", "O(n)", "镶嵌（mosaic）", "半透明"],
            ["TCG", "(n!)^2", "O(n^2)", "通用", "透明（打包前可判）"],
            ["TCG-S", "(n!)^2", "O(n log n)", "通用", "透明"],
            ["BSG", "较大", "O(n^2)", "通用", "不透明"],
        ], col_align=["l", "l", "l", "l", "l"],
        note="选表示法看四个维度：**解空间大小、打包复杂度、是否通用、几何关系是否透明**。切片表示快但只覆盖可切片布图；SP / BSG 通用但需打包后才知布局；**TCG（传递闭包图，Transitive Closure Graph）** 用水平 / 垂直两张闭包图把关系做到打包前可判，TCG-S 再配一条打包序列把复杂度降到 O(n log n)。SP 与 TCG 等价，B\\*-tree 与 O-tree 等价。"),

    split("6.4a 固定轮廓 floorplanning", "现代目标不是最小面积，而是塞进给定轮廓", "f27_fixedoutline.png", [
        P("经典算法追求**最小面积**，但真实芯片的外形和尺寸往往**事先就被封装、IP 与上层规划定死**。固定轮廓布图规划（fixed-outline floorplanning，Adya–Markov）因此改变目标：把所有块塞进一个**给定的矩形轮廓**，并优化线长等指标。"),
        P("引导块往轮廓内塞的关键量是**裕量（slack）**：一个块在「全部向左下压实」与「全部向右上压实」两种极限位置之间的可移动余地。"),
        L("用 slack 引导优化："),
        B("零-slack 块在关键路径上、几乎动不了，是布局的瓶颈"),
        B("把零-slack 块挪到高-slack 块旁边，借后者的余地腾出空间"),
        P("代表工具有 Parquet（底层用 SP 或 B\\*-tree）与 Fast-SA；另有一支走**解析 / 数学规划**（min-cost max-flow、非线性规划 MINP）的路线。"),
    ], caption="经典最小面积结果 vs 固定轮廓（目标 outline + slack / whitespace）"),

    bl("6.4b 现代 floorplanning 要点", "目标从「压到最小」转为「在给定轮廓里把各项指标做好」", [
        "**解析 / 数学规划法**：把布图写成可优化数学问题（min-cost max-flow、非线性规划），大规模比纯 SA 更可扩展",
        "**空白（whitespace）当资源**：留给布线、缓冲器与时序裕量，而非一味压到最小",
        "**拥塞感知**：用网格估布线拥塞，把拥塞代价并入优化目标，避免布局阶段才发现绕不出去",
        "**缓冲规划**：为长互连预留缓冲器位置与通道，保证布线后时序仍可收敛",
        "**吞吐 / 微架构感知**：吞吐率 ≈ 频率 / CPI，过长流水互连抬高 CPI，需兼顾数据通路长度",
        "**功耗感知**：高功耗块靠近电源焊盘降 IR；并为 FPGA / 模拟对称 / 3D 等专用约束留位",
    ]),

    split("6.5 工业布图与原型", "floorplanning 诊断可行性，prototyping 做签核前闸门", "f28_hier.png", [
        P("工业把这步分两段：**早期 floorplanning** 诊断可行性、容忍不完整数据、欢迎人工介入；**后期 prototyping** 验证 RTL 可实现，是签核前的可行性闸门。"),
        L("扁平（flat）与层次化（hierarchical）的取舍："),
        B("层次化靠**预算切块**拆开大设计，但一个不可行的块预算就可能拖垮整片"),
        B("工业常用：先 flat 摆布线一次、在跨边界处定引脚，保证可行后再切块"),
        P("配套：**引脚分配 + 时序预算**（零-slack 算法）与**可布线性分析**（全局 / 试布线估拥塞）。"),
    ], caption="工业：flat vs hierarchical（顶层切块 + 引脚 + 预算）与 floorplanning→prototyping 流程"),

    # ===== 课后自测（题 + 参考答案，对齐笔记 §7）；借 refs 页型得 [n] 编号 + 两栏布局，答案 [n] 对应题 [n] =====
    {"kind": "refs", "title": "课后自测", "sub": "检验是否真懂；参考答案见下页，详解见笔记 §7", "accent": PRIMARY, "refs": [
        "floorplan 的目标为何不是单纯「面积最小」？",
        "core limited 与 pad limited 的优化方向有何不同？",
        "IO 不随摩尔定律缩小，为何会影响芯片尺寸？",
        "利用率为何不能单独证明 floorplan 可实现？",
        "总利用率与有效利用率的分母差在哪？",
        "hard macro 为何通常靠边 / 靠角摆放？",
        "macro placement 为何也属于 power planning？",
        "placement region / placement blockage / routing blockage 各限制什么？",
        "halo 与 placement blockage 的核心区别是什么？",
        "feedthrough 解决的是哪类层次化布线问题？",
        "timing budget 为何与 pin assignment 强相关？",
        "ILM / ETM 为何能加速全芯片时序？",
        "IR drop 与 EM 各对应「短期电压」还是「长期可靠性」？",
        "power grid 为何不能无限加宽加密？",
        "多电压 / 门控 floorplan 为何要预留 always-on 资源？",
        "网表唯一化为何必须在布局之前完成？",
        "defIn 与 floorPlan 的语义为何不能混用？",
        "（算法）切片表示为何要规范化 Polish 表达式，又有何固有局限？",
        "（算法）B*-tree 的左孩 / 右孩各编码什么几何关系，打包为何是 O(n)？",
        "（算法）固定轮廓布图为何引入 slack，零-slack 块该怎么处理？",
    ]},
    {"kind": "refs", "title": "课后自测 · 参考答案", "sub": "编号对应上页", "accent": PRIMARY, "refs": [
        "面积 / 延迟 / 拥塞要平衡、三者冲突；是第一轮工程取舍，非单目标最优。",
        "核心受限调利用率 / 宏 / 布线；焊盘受限调 IO 环 / 焊盘 / 凸点 / 封装。",
        "IO 贵且不随工艺缩小，数量多反把晶粒撑大（焊盘受限）。",
        "利用率只是面积估算、不反映拥塞；须跑试布线 / 全局布线验证。",
        "总利用率除核心区面积；有效利用率再扣阻挡 / 宏留边 / 禁布区。",
        "留完整大矩形、不切碎核心；高功耗宏靠边、近电源焊盘降 IR。",
        "宏位置决定供电路径与电流密度，直接影响 IR / EM。",
        "region：放哪个区域；placement blockage：能否放单元；routing blockage：能否走线。",
        "halo 随宏移动（贴身留边）；placement blockage 多为固定坐标。",
        "信号跨越中间模块：B 无穿通则绕行，需在 B 生成穿通引脚 / 网络。",
        "芯片级约束映射到模块边界，引脚位置即定边界约束与可收敛性。",
        "保留接口时序、隐藏内部细节，用抽象模型加速全芯片分析。",
        "IR = 短期 / 瞬时电压；EM = 长期电流密度可靠性。",
        "越宽越多越抢信号布线轨道、加剧拥塞；须与 IR / EM 权衡。",
        "部分逻辑在其他域关断时仍需持续供电，须预留 always-on 电源域 / 网络。",
        "物理优化按实例独立进行；共享模块定义会优化一个牵连另一个。",
        "（拓展）floorPlan = 从零新建布图；defIn = 读入已有 DEF，混用有覆盖风险。",
        "规范化（skewed、无连续同号）让串与布图一一对应、去冗余；固有局限是只能表达可切片布图，覆盖不了全部紧致布局。",
        "左孩 = 右邻块 x_j=x_i+w_i，右孩 = 同 x 上邻块 x_j=x_i；DFS 一次定 x，y 用 contour 在线维护，故 O(n) 线性打包。",
        "现代目标是塞进给定轮廓；slack = 块在左下压实与右上压实间的余地，把零-slack 关键块挪到高-slack 块旁腾空间。",
    ]},
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
    {"kind": "refs", "title": "参考文献 References", "sub": "本讲内容来源", "accent": PRIMARY, "refs": [
        "Adam Teman. Digital VLSI Design (DVD), Lecture 6 — Import Design and Floorplan. Bar-Ilan University (83-612). enicslabs.com/academic-courses/dvd-english",
        "J. M. Rabaey, A. Chandrakasan, B. Nikolić. Digital Integrated Circuits: A Design Perspective. Prentice Hall.",
        "N. H. E. Weste, D. M. Harris. CMOS VLSI Design: A Circuits and Systems Perspective. Addison-Wesley.",
        "IDESA / EPFL — Digital IC design tutorials.",
        "Cadence Innovus / Synopsys ICC2 / Fusion Compiler User Guides（命令与流程参考）.",
    ]},
    {"kind": "refs", "title": "图片来源 Image Credits", "sub": "全部开放许可（CC0/CC BY/CC BY-SA/PD），署名经来源页核验", "accent": PRIMARY, "refs": [
        "图 1.1 486 die — Smial, CC BY 3.0；晶圆 — A. Kübelbeck, CC BY-SA 3.0.",
        "图 2.1 i9-13900K die — Fritzchens Fritz / JmsDoug, CC0.",
        "图 2.2 拥塞形成 — Hu et al., arXiv:2603.11075；热力图 — Tsai et al., arXiv:2510.15872（CC BY 4.0）.",
        "图 2.4 UltraSPARC die — ZyMOS, CC BY-SA 3.0；摆放对比 — Copparihollmann；SRAM — Seanriddle（CC BY-SA 4.0）.",
        "图 2.6 放置约束 — Mallappa et al., FloorSet, arXiv:2405.05480, CC BY 4.0.",
        "图 3.2 层次化布图/流程 — Mostafa et al., PARSAC, arXiv:2405.05495, CC BY-SA 4.0.",
        "图 3.3 引线键合 — Mister rf, CC BY-SA 4.0.",
        "图 4.1 Bitfury 顶层供电网 — ZeptoBars, CC BY 3.0.",
        "图 4.2 IR 压降图 — Seo et al., WACA-UNet, arXiv:2507.19197, CC BY 4.0.",
        "图 4.3 EM SEM — P.-E. Zörner, CC BY-SA 3.0；AlCu 空洞 — Liu et al., doi:10.3390/mi16040458, CC BY 4.0.",
        "图 4.7 IR-on-layout — Liu et al., CFIRSTNET, arXiv:2502.12168, doi:10.1145/3676536.3676756, CC BY 4.0.",
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
