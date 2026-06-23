# -*- coding: utf-8 -*-
"""examples/report_sample.py —— 技术报告样张：演示 table / chart / refs / 带题注 split。
内容：三组利用率配置下的时序·拥塞·电源完整性对比（grounded in Floorplan 笔记）。
运行：python examples/report_sample.py  → examples/_out/ 下 .pptx + 逐页预览。
"""
import os
import sys

_SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # _SlideKit 根
sys.path.insert(0, _SK)
import deck as D  # noqa: E402

OUT = os.path.join(_SK, "examples", "_out")
PREV = os.path.join(OUT, "_preview")
PPTX = os.path.join(OUT, "Floorplan_Util_Report.pptx")
ASSETS = os.path.abspath(os.path.join(_SK, "..", "IC_Backend_Notes", "assets", "floorplan"))
SRC = "整理 J.C · 源自 Digital VLSI Design (DVD), Prof. Adam Teman, Bar-Ilan University (83-612)"
FOOTER = "技术报告 · Floorplan 利用率研究"

SPECS = [
    {"kind": "cover", "title": "Floorplan 利用率与电源完整性方案对比",
     "tag": "数字 IC 后端 · 技术报告",
     "sub": "三组核心利用率配置下的时序、拥塞与电源完整性评估",
     "line": "结论：目标利用率取 0.70 时 PPA 裕量最均衡",
     "src": SRC},

    {"kind": "split", "title": "研究背景与方法", "sub": "为何在 floorplan 阶段定利用率",
     "figure": "f01_position.png", "caption": "Floorplan 在 PnR 流程中的位置：后端第一道决策定 PPA 上限",
     "style": "num", "bullets": [
        "Floorplan 决定芯片 PPA 上限，且此阶段改动成本最低。",
        "利用率定得过高会拥塞、绕不出线，过低则浪费面积。",
        "本报告固定网表与约束，仅扫描目标利用率 0.55 / 0.70 / 0.85。",
        "每组跑试布局加全局布线，评估时序、拥塞溢出与峰值 IR。",
     ]},

    {"kind": "table", "title": "三组利用率方案对比", "sub": "同一网表、同一约束下的关键签核指标",
     "table": {
        "headers": ["方案", "目标利用率", "WNS (ns)", "拥塞溢出", "峰值 IR (mV)", "结论"],
        "col_align": ["left", "right", "right", "right", "right", "left"],
        "col_w": [1.7, 1.3, 1.2, 1.2, 1.3, 2.4],
        "rows": [
            ["激进 Aggressive", "0.85", "-0.18", "2.4%", "92", "拥塞绕不出、IR 超标"],
            ["均衡 Balanced", "0.70", "+0.04", "0.1%", "58", "推荐"],
            ["宽松 Loose", "0.55", "+0.11", "0.0%", "41", "裕量大但浪费面积"],
        ]}},

    {"kind": "chart", "title": "IR drop 随距电源距离的变化", "sub": "均衡方案，沿供电边到 core 内部取样",
     "chart": {"type": "line",
               "categories": ["0", "2", "4", "6", "8", "10"],
               "series": [("静态 Static", [12, 22, 35, 50, 68, 89]),
                          ("动态 Dynamic", [16, 30, 49, 72, 99, 128])],
               "x_title": "距电源距离 (GCell)", "y_title": "IR drop (mV)"}},

    {"kind": "chart", "title": "三方案静/动态峰值 IR 对比", "sub": "利用率越高、峰值压降越大",
     "chart": {"type": "bar",
               "categories": ["Aggressive 0.85", "Balanced 0.70", "Loose 0.55"],
               "series": [("静态 IR", [88, 55, 39]),
                          ("动态 IR", [128, 79, 55])],
               "y_title": "峰值 IR (mV)"}},

    {"kind": "split", "title": "电源网络规划：Ring → Stripe → Mesh → Rail", "sub": "均衡方案采用的 PG 骨架",
     "figure": "f09_irem.png", "caption": "IR 压降与 EM：靠加密 mesh / via 与多路径控住",
     "bullets": [
        "Power Ring 绕 core 闭合，承担总电流入口。",
        "Power Stripe 横跨 core 分担电流，纵横交织成 Mesh。",
        "标准单元 Rail 沿行供电（follow-pin），由 sroute 打通。",
        "高压降区通过加密 mesh、增补 via array 局部缓解。",
     ]},

    {"kind": "bullets", "title": "结论与建议", "sub": "面向后续 Placement 的可执行结论",
     "two_col": True, "bullets": [
        "目标利用率取 0.70，时序、拥塞与 IR 三者裕量最均衡，定为本设计基线。",
        "利用率 0.85 时拥塞溢出达 2.4%、峰值 IR 超 90 mV，签核失败，不可取。",
        "IR drop 随距电源距离近似线性增长，动态分量约为静态的 1.4 倍。",
        "缓解 IR 应优先加密顶层 mesh 并增补 via array，而非单纯降低利用率。",
        "关键总线 pin 建议手工约束，避免跨块长绕线吃掉时序预算。",
        "方案确定后再进详细 Placement，floorplan 阶段改动成本最低。",
     ]},

    {"kind": "refs", "title": "参考文献", "sub": "本报告引用的工具手册与教材",
     "refs": [
        "A. B. Kahng, J. Lienig, I. L. Markov, J. Hu, \"VLSI Physical Design: From Graph Partitioning to Timing Closure,\" Springer, 2011.",
        "A. Teman, \"Digital VLSI Design — Lecture 6: Floorplanning,\" Bar-Ilan University (83-612), 2020.",
        "Synopsys, \"IC Compiler II Implementation User Guide,\" Version 2023.03, 2023.",
        "Cadence, \"Innovus Implementation System User Guide,\" Version 22.1, 2023.",
        "ANSYS, \"RedHawk-SC: Electromigration and IR-Drop Signoff User Manual,\" 2022.",
     ]},

    {"kind": "close", "title": "谢谢 · Thanks",
     "sub": "基线既定，下一步进入详细 Placement",
     "line": "目标利用率 0.70 · 加密 mesh 控 IR · 关键 pin 手工约束 · floorplan 改动成本最低",
     "src": SRC},
]


def main():
    n = len(SPECS)
    D.build_previews(SPECS, PREV, n, asset_dir=ASSETS, page_label=FOOTER)
    print("previews ->", PREV, "(", n, "pages )")
    print("pptx ->", D.build_pptx(SPECS, PPTX, n, asset_dir=ASSETS, page_label=FOOTER))


if __name__ == "__main__":
    main()
