# -*- coding: utf-8 -*-
"""
_SlideKit/decks/floorplan.py  (v4 · 24 页·内容回填)
==================================================
Floorplan 24 页幻灯片，与教案 05_Floorplan.md 逐页对应；知识点写在页面上，
论文插图作配图插入。产出可编辑 .pptx + 逐页版面预览。
运行：python decks/floorplan.py
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
BLUE, TEAL, AMBER, ROSE, VIOLET = "2563EB", "14B8A6", "F59E0B", "DB2777", "7C3AED"


def split(t, sub, fig, bullets, acc):
    return {"kind": "split", "title": t, "sub": sub, "figure": fig, "bullets": bullets, "accent": acc}


def bl(t, sub, bullets, acc, two=False):
    return {"kind": "bullets", "title": t, "sub": sub, "bullets": bullets, "accent": acc, "two_col": two}


SPECS = [
    {"kind": "title", "title": "Floorplan 布图规划", "sub": "数字 IC 后端 · 从 RTL 到 GDS · DVD Lecture 6", "src": SRC, "accent": BLUE},
    {"kind": "cols2", "title": "本讲导览  Agenda", "sub": "24 页 · 每节一图/一题，知识点写在页面上", "accent": BLUE, "cols": [
        ("基础与几何", ["定位与意义、为什么决定 PPA", "Die / Core / IO 几何", "利用率与长宽比", "Row / site / 翻转供电轨"], BLUE),
        ("实现要素", ["宏摆放、halo/blockage、专用单元", "IO/Pad/Bump 与引脚分配", "电源/IR/EM、门控、多电压", "时序预算、拥塞闭环、命令/考点"], TEAL),
    ]},
    split("什么是 Floorplan", "物理实现的第一步", "f01_position.png", [
        "物理实现(P&R)第一个确定版图骨架的步骤",
        "位置：综合出门级网表后、详细布局前",
        "之前有“设计导入”：读库/网表/SDC/UPF",
        "任务①：die / core 几何",
        "任务②③：宏的位置朝向、IO/Pad/Bump",
        "任务④⑤⑥：PG 骨架、多电压域、blockage",
        "本质：逻辑网表 → 物理布局骨架",
    ], BLUE),
    split("为什么重要：一步错，步步错", "决定 PPA 上限", "f02_why.png", [
        "决定芯片 PPA(性能/功耗/面积)的上限",
        "利用率定高 → 再优秀的布局也拥塞绕不出",
        "宏乱放 → 关键路径绕远，时序收不回",
        "PG 不足 → 签核才发现 IR drop / EM 超标",
        "FP 阶段改≈免费，越往后改成本急剧上升",
        "“七分布局三分布线”是经验俗语、非量化",
    ], ROSE),
    split("芯片几何：Die / IO / Core / Rows", "各区域从属关系", "f03_geometry.png", [
        "Die：芯片最外边界，含 scribe 切割道",
        "Core：放标准单元与宏的内部区域",
        "IO / Pad Ring：Die 与 Core 间的环形区",
        "Core-to-IO 间距：走电源环 / IO 走线",
        "Core 内切成等高的标准单元行 Rows",
        "嵌套：Die ＞ Pad Ring ＞ Core ＞ Macro+Rows",
    ], BLUE),
    split("标准单元行 / site / 翻转共享供电轨", "面积更省的小机关", "f05_rows.png", [
        "Row：等高水平行；行高=库单元高度(9T/7T)",
        "行高 ≈ track 数 × M2 pitch",
        "Site：行内最小放置栅格，定义于 LEF",
        "单元宽度必须是 site 宽度的整数倍",
        "相邻行镜像翻转(FS) → 同名轨落在行边界",
        "上下两行共享同名轨 → 供电轨条数减半",
    ], TEAL),
    split("利用率与长宽比", "两个口径要分清", "f04_util.png", [
        "Total Util = (Σ单元+Σ宏) / Core 面积",
        "Effective Util 扣除 blockage/halo，工具多报此",
        "经验初值 0.5–0.8，看 macro/拥塞/裕量",
        "目标利用率 ≠ placement 后局部密度",
        "长宽比 H/W ≈ 1 最利于布线与时钟树",
        "长宽比约定各工具可能相反，以手册为准",
    ], AMBER),
    split("宏单元摆放原则", "Macro Placement", "f06_macro.png", [
        "宏 = SRAM/PLL/IP，尺寸大、形状/引脚固定",
        "① 沿边/沿角，中间留给标准单元",
        "② 按数据流就近(flyline、auto placer)",
        "③ 留 channel；或 channel-less 紧贴",
        "④ 引脚朝 core，避免绕过宏本体",
        "⑤ 朝向(8 种)与对称背靠背、规整阵列",
    ], TEAL),
    split("halo / keepout 与各类 blockage", "给布线留活路", "f07_halo.png", [
        "Halo/Keepout：宏四周禁放边带，跟随宏移动",
        "Placement Blockage：固定坐标的禁放区",
        "  hard 全禁 / soft 优化阶段可放 buffer",
        "  partial 按密度上限(≈density screen 不等价)",
        "Routing Blockage：禁某些层布线，可指定层",
        "宏引脚侧加 halo 给 pin access 留空间",
    ], ROSE),
    bl("物理专用单元：endcap / well-tap / filler", "physical-only cell，floorplan 早期就要规划", [
        "physical-only cell：不参与逻辑，但关乎 row/well 连续",
        "Endcap / Boundary：放每行两端及 macro 边界，保 well/implant 连续与 DRC",
        "Well-tap：周期插入提供 well 偏置接触",
        "  间距须满足 max well-tap distance(DRC)，否则 latch-up 风险",
        "Filler：末期填行内空隙，保供电轨与 well 连续；时机晚于 tap/endcap",
    ], VIOLET),
    split("IO / Pad、Bump（封装相关）", "wire-bond vs flip-chip", "f13_iopad.png", [
        "Wire-bond：IO Pad 沿 die 四周排成 Pad Ring",
        "考虑信号/电源 Pad 交替、ESD、Corner Pad",
        "Flip-Chip：信号经 Bump 面阵列引出",
        "常配 RDL；是否需要取决封装/凸点布局",
        "bump 对齐 bump map，控间距与比例",
    ], ROSE),
    bl("引脚分配 Pin Assignment", "pin 位置决定块间走线与时序", [
        "顶层：IO buffer 位置决定芯片对外引脚",
        "块级：partition 端口分配到块边界具体位置",
        "pin 须落合法 routing track、与该层布线方向一致",
        "沿数据流方向分布，避免长绕线",
        "注意 feedthrough：信号穿无关 block 需预留穿通端口",
        "工具可自动优化，关键总线常需手工约束",
    ], BLUE),
    split("电源规划：Ring → Stripe → Mesh → Rails", "PG 网络自上而下", "f08_power.png", [
        "Power Ring：绕 core/macro 的闭合环(顶层金属)",
        "Power Stripe：横跨 core 的粗金属条",
        "Power Mesh：stripe 纵横交织成网，降等效电阻",
        "Std-cell Rail：沿行的 M1 供电轨(follow-pin)",
        "Special Route(sroute)：连接 ring/stripe/pin/pad 打 via",
        "sroute 范围广，是 PG 成型的关键步骤",
    ], AMBER),
    split("IR drop 与 电迁移 EM", "签核要过的两关", "f09_irem.png", [
        "IR drop：ΔV=I·R，离电源越远压降越大",
        "压降过大 → 时序变差甚至功能失效",
        "预算常为 VDD 的百分之几，静/动分别约束",
        "EM：电流密度 J 过大，金属原子迁移致断/短路",
        "PG 与高翻转信号线的 EM 机理不同，分别评估",
        "签核：Voltus(Cadence)/RedHawk(Ansys)/PrimeRail(Synopsys)",
    ], AMBER),
    split("电源门控：power switch / header / footer", "对可关断模块做 Power Gating", "f14_gating.png", [
        "可关断模块插 Power Switch 实现 Power Gating",
        "Header(PMOS)：门控 VDD—VVDD，更常用",
        "Footer(NMOS)：门控 VVSS—VSS，较少单独用",
        "floorplan 规划 switch 阵列与 enable 菊花链",
        "菊花链分时开启 → 控冲击电流、规划 always-on PG",
    ], VIOLET),
    split("多电压域与 UPF", "Multi-Voltage", "f10_mv.png", [
        "不同区域不同电压(或可关断) → 省功耗",
        "Level Shifter：跨电压域信号电平转换",
        "Isolation：关断域输出钳位，防下游浮空",
        "Retention FF：关断期间保状态",
        "Always-on Buffer：关断域内接常开电源",
        "UPF(IEEE 1801)/CPF 描述意图，floorplan 落地电压区域",
    ], VIOLET),
    split("时序预算与模块划分", "分而治之", "f11_budget.png", [
        "层次化设计按层级切成 Block / partition",
        "把顶层路径约束拆到各 block 边界 → 各自 SDC",
        "预算合理 → 各块独立收敛后顶层收敛",
        "pin 离逻辑越远，块内走线越长、budget 越紧",
        "自动预算：allocate_budgets / deriveTimingBudget / ETM",
        "budget 含 IO delay + 时钟不确定度 + 驱动/负载",
    ], BLUE),
    split("拥塞 / IR 早期预估与迭代闭环", "Floorplan 不是一遍过", "f15_loop.png", [
        "拥塞早估：GR 估 GCell 需求/资源 → 拥塞图",
        "全局拥塞 vs 局部 / pin-access 拥塞",
        "热点：macro notch、窄 channel、pin 密集",
        "缓解：降利用率、加宽 channel、partial blockage",
        "IR 早估：静态 PG 分析定位高压降区，加密 mesh",
        "迭代闭环：floorplan → 试布局/GR → 评估 → 回退",
    ], AMBER),
    split("输入 / 输出 与 文件作用", "吃什么、吐什么", "f12_io.png", [
        "输入：netlist、LEF、lib、SDC、UPF、预算",
        "输出：带宏摆放+PG+blockage 的 DEF",
        "输出 Floorplan DB(NDM/OA)、可布线性/时序初评",
        "LEF：site/layer/规则/单元抽象",
        "DEF：die/core/row/macro/pin/PG 交换",
        "工具：Synopsys ICC2/FC、Cadence Innovus",
    ], BLUE),
    {"kind": "cols2", "title": "衡量指标与常见问题", "sub": "收敛看指标，出问题反查", "accent": TEAL, "cols": [
        ("关键指标", ["Core Utilization 0.5–0.8", "Aspect Ratio ≈ 1.0", "Congestion Overflow → 0", "WNS / TNS ≥ 0", "Static/Dynamic IR：VDD 百分之几", "EM margin：满足 foundry 规则"], BLUE),
        ("问题 → 对策", ["绕不出 → 降 util / 加宽 channel", "时序差 → 重摆 macro / 优 pin", "IR 超标 → 加密 mesh / via", "EM 违例 → 加宽线 / 并联 via", "Pin 拥塞 → 加 halo / 调层", "唤醒冲击 → 菊花链分时开"], AMBER),
    ]},
    {"kind": "cards2", "title": "EDA 命令速查（ICC2 / Innovus）", "sub": "选项随版本而异；坑：Innovus margin 四值为 LBRT", "accent": BLUE, "cards": [
        ("Synopsys · ICC2 / Fusion Compiler", [
            "initialize_floorplan \\",
            "  -core_utilization 0.70 -side_ratio {1 1}",
            "create_keepout_margin -outer {l b r t}",
            "create_placement_blockage -type hard/soft/partial",
            "create_pg_ring/mesh_pattern + compile_pg",
            "place_pins / set_block_pin_constraints",
            "create_voltage_area      # multi-VDD domain",
        ], BLUE),
        ("Cadence · Innovus", [
            "floorPlan -r 1.0 0.7 <L> <B> <R> <T>",
            "addHaloToBlock {l b r t}",
            "createPlaceBlockage -type hard/soft/partial",
            "addRing / addStripe / sroute",
            "editPin / assignIoPins",
            "createPowerDomain        # multi-VDD domain",
            "defIn != floorPlan  (read DEF vs create)",
        ], TEAL),
    ]},
    {"kind": "bullets", "title": "本章小结", "sub": "8 句话带走", "accent": TEAL, "two_col": True, "bullets": [
        "FP = P&R 第一步，定 die/core/macro/PG/电压域，决定 PPA",
        "几何：总/有效利用率(0.5–0.8)、长宽比≈1、行翻转共享轨",
        "宏：沿边/dataflow/朝向、channel、halo、blockage、专用单元",
        "IO/bump 与 pin：pad ring vs bump array、track/feedthrough",
        "电源：ring→stripe→mesh→rail→sroute，控 IR/EM、门控",
        "多电压：LS/ISO/retention/always-on/switch，UPF/CPF 落地",
        "时序预算：拆到各 block，pin 与 budget 耦合",
        "迭代闭环：GR 估拥塞、静态 PG 估 IR，回退收敛再进 placement",
    ]},
    {"kind": "cols2", "title": "易混淆点 / 面试高频考点", "sub": "16 题课后自测", "accent": AMBER, "cols": [
        ("面试题 1–8", ["Utilization 过高 vs 过低", "Halo vs Placement Blockage", "Hard / Soft / Partial Blockage", "Placement vs Routing Blockage", "Level Shifter vs Isolation", "Retention FF vs Always-on Buffer", "Header vs Footer Switch", "IR Drop vs EM"], BLUE),
        ("面试题 9–16", ["Ring/Stripe/Mesh/Rail/sroute 区别", "Flylines 的作用", "Core Util vs Placement Density", "UPF vs CPF", "Aspect Ratio 为何偏好 1.0", "为什么相邻行要翻转", "defIn vs floorPlan", "签核工具厂商归属"], AMBER),
    ]},
    {"kind": "close", "title": "谢谢 · Thanks", "sub": "下一讲：Placement 布局（DVD Lec 7）", "src": SRC, "accent": BLUE},
]


def main():
    D.build_previews(SPECS, PREV, TOTAL, asset_dir=ASSETS)
    print("previews ->", PREV, "(", len(SPECS), "pages )")
    tmpl = os.path.abspath(os.path.join(_SK, "..", "local-doc", "PPT-template.pptx"))
    if os.path.exists(tmpl):  # 基于模板母版的对比版本
        try:
            print("pptx(tmpl) ->", D.build_pptx(SPECS, PPTX.replace(".pptx", "_tmpl.pptx"), TOTAL, asset_dir=ASSETS, template=tmpl))
        except Exception as e:
            print("tmpl build failed:", e)
    try:  # 主版本（干净白底，可被 PowerPoint 锁住）
        print("pptx ->", D.build_pptx(SPECS, PPTX, TOTAL, asset_dir=ASSETS))
    except Exception as e:
        print("main pptx skipped (locked?):", e)


if __name__ == "__main__":
    main()
