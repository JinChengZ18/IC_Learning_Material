# _SlideKit — 笔记 → 论文插图 → 可编辑 PPT + 讲稿 流水线

把一篇学习笔记（如 [`IC_Backend_Notes/05_Floorplan.md`](../IC_Backend_Notes/05_Floorplan.md)）配成一套**论文/图书级插图**、一份**可编辑演示文稿**和一份**口语讲稿**。与 `_BiliKit`（B站→字幕）同级，是本仓库的第二个可复用引擎。

> 风格：**现代 IC 语义多色 (Vibrant)** + **参考信息图卡片风**。语义配色：电蓝 `#2563EB`=逻辑，青绿 `#14B8A6`=存储/Macro，琥珀 `#F59E0B`=电源，品红 `#DB2777`=IO，紫 `#7C3AED`=时钟，石板灰=中性；墨色 `#1E293B` 文字、白底。
> 图幅统一 **~4:3 / 1:1**，便于作为 16:9 幻灯片右栏侧插图。

---

## 1. 目录结构（按笔记分桶）

```
_SlideKit/
├─ theme.py            # 主题引擎：配色 + 字号层级 + 图元(node/infocard/flowrow/sechead/legend/save…)
├─ deck.py             # 幻灯片版面 + build_pptx(python-pptx) + build_previews(matplotlib 校对)
├─ tools/thumbs.py     # 把大图缩成 <=1280px 缩略图(<dir>/_qa)，便于肉眼校对
├─ notes/              # ★ 每篇笔记一个桶（project management）
│   └─ 05_floorplan/
│       ├─ figures.py  # 该笔记的全部插图函数 → assets/floorplan/f01..f15
│       └─ slides.py   # 该笔记的幻灯片规格 → slides/05_Floorplan.pptx
│   (将来：02_rtl/、03_inputs/、04_sdc/、06_placement/ …)
├─ requirements.txt    # matplotlib + python-pptx + Pillow
└─ README.md

产物（落在对应笔记目录下，便于 md 相对路径引用）：
IC_Backend_Notes/
├─ assets/floorplan/   # f01..f15 .png(插 PPT) + .svg(嵌 md)，_qa/ 为缩略图
├─ slides/05_Floorplan.pptx   # 可编辑 PPT（原生文本 + 插图），_preview/ 为版面预览
├─ 05_Floorplan.md            # 教案（知识点在页、备注精简）
└─ lecture_scripts/05_Floorplan.md   # 口语讲稿（可照念）
```

---

## 2. 两步流水线（以 floorplan 桶为例）

```bash
python -m pip install -r requirements.txt                       # 首次
python notes/05_floorplan/figures.py                            # ① 出图（PNG + SVG，~4:3/1:1）
python tools/thumbs.py ../IC_Backend_Notes/assets/floorplan     #   生成缩略图供校对
python notes/05_floorplan/slides.py                             # ② 出片：可编辑 .pptx + 逐页预览
```

> **① 图**：论文级独立插图（无外框、字号分层、占满画框），供插入 PPT 与嵌 md；一次导出 `.png`+`.svg`。
> **② 片**：`slides.py` 写一份「页面规格」，`deck.py` 同时产出 ⓐ `build_pptx`（python-pptx **可编辑**：原生标题/要点文本框 + `add_picture` 插图，已设中文 ea 字体）和 ⓑ `build_previews`（matplotlib 按同坐标渲染预览——本机无 LibreOffice，预览是**唯一**版面校对手段）。

---

## 3. theme.py 速查

| 类 | 函数 |
|----|------|
| 画布/保存 | `canvas(w,h)`（白底、关 autoscale）· `save(fig,outdir,name)`（png+svg） |
| 图块 | `node(role,variant)`（soft/solid/outline 两段色块）· `rect/line/arrow` |
| **卡片风** | `infocard(title,detail,role,highlight)`（浅底+粗标题+同色细节）· `flowrow(items)`（chevron 流程带高亮）· `sechead(num,text)`（①带圈分节标题） |
| 标注 | `legend / annotate / tag / bracket / heading / caption` |

- 字号层级：`FS_H1=19 > FS_H2=15 > FS_BODY=13 > FS_CAP=11.5`（图内严格分层，避免“字乱”）。
- 配色：`BLUE/TEAL/AMBER/ROSE/VIOLET`（带 `_L`/`_D`）、`INK/INK2/MUTED/LINE/SLATE_L/WHITE`；`SOFT`(卡片浅底)、`ROLE`/`MAIN`(角色映射)。
- 代码块文字必须 ASCII（等宽字体无 CJK）；YaHei 缺字符（⊃ ↔ ≠）改用 ＞ / — / !=。

---

## 4. 复用到别的主题（如 Placement / SDC）

1. 复制 `notes/05_floorplan/` → `notes/06_placement/`。
2. 改 `figures.py`：`OUT` 指向 `assets/placement/`，用 `theme` 图元（优先 `infocard/flowrow` 卡片风）写若干 `fXX_*()`，图幅取 ~4:3/1:1。
3. 改 `slides.py`：`PPTX/ASSETS` 指向该笔记，编辑 `SPECS`（`split` 图文页 / `bullets·cols2·cards2` 文本页）。
4. 教案 md 每小节配 `![](assets/<topic>/fXX.png)`，与幻灯片一一对应。

> 原则：**一个笔记一个 `notes/<NN_name>/` 桶；所有视觉规范只在 `theme.py` / `deck.py` 里定义一次。**

---

## 5. 设计约定

- 颜色**语义固定**，相同含义跨图同色；图幅 **~4:3/1:1**、占满画面、字号分层、无装饰外框。
- 列表/流程类用 `infocard`/`flowrow` 卡片风（对齐参考信息图）；空间概念（die/core、mesh、IR 热力图）保留为图、仅统一风格。
- 图自包含（白底、必要处图例），单独导出也成立；校对用 `tools/thumbs.py`（避免大图超出查看上限）。

---

> 出处：图示内容对应 *Digital VLSI Design (DVD)*, Prof. Adam Teman, Bar-Ilan University (Course 83-612)。整理：**J.C**。
