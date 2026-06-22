# _SlideKit — 笔记 → 架构图 → 幻灯片 流水线

把一篇学习笔记（如 [`IC_Backend_Notes/02_Floorplan.md`](../IC_Backend_Notes/02_Floorplan.md)）变成一套**论文/图书级架构·原理图**和一份**逐页对齐的演示文稿**。
与 `_BiliKit`（B站→字幕）同级，是本仓库的第二个可复用引擎。

> 风格（v2）：**现代 IC 语义多色 (Vibrant)** —— 每类元素一个专属色相以提高辨识度：
> 电蓝 `#2563EB`=逻辑/信号，青绿 `#14B8A6`=存储/Macro，琥珀 `#F59E0B`=电源/PG，品红 `#DB2777`=IO/高亮，紫 `#7C3AED`=时钟，石板灰=衬底/中性；墨色 `#1E293B` 文字、白底。
> 同一套图既能贴进 PPT 版面，也能嵌进 `.md`（白底自包含，深浅主题都清晰）。

---

## 1. 目录结构

```
_SlideKit/
├─ theme.py            # 主题引擎(v2)：语义配色 + 字体 + 图元(node/arrow/flow/legend/annotate/save...)
├─ deck.py             # 幻灯片版面 + build_pptx(python-pptx)
├─ diagrams/
│   └─ floorplan.py    # 示例：Floorplan 主题的 12 张论文级图(f01..f12)
├─ decks/
│   └─ floorplan.py    # 示例：18 页讲稿幻灯片(每页对应讲稿一小节)
├─ tools/thumbs.py     # 把大图缩成 <=1280px 缩略图(<dir>/_qa)，便于校对
├─ requirements.txt    # matplotlib + python-pptx + Pillow
└─ README.md

产物（落在对应笔记目录下，便于 md 相对路径引用）：
IC_Backend_Notes/
├─ assets/floorplan/   # f01..f12 .png(插入 PPT/讲稿) + .svg(嵌 md)，_qa/ 为缩略图
├─ slides/02_Floorplan.pptx   # 可编辑 PPT（原生文本 + 插图），_preview/ 为版面预览
├─ 02_Floorplan.md            # 教案（知识点在页、备注精简）
└─ lecture_scripts/02_Floorplan.md   # 口语讲稿（可照念）
```

---

## 2. 两步流水线

### Step ① 画图（Python / matplotlib）

```bash
python -m pip install -r requirements.txt          # 首次
python diagrams/floorplan.py                        # 生成 12 张图(PNG + SVG)
python tools/thumbs.py ../IC_Backend_Notes/assets/floorplan   # 可选：生成缩略图供肉眼校对
```

- 图为**论文级独立插图**（无图内大标题/署名，占满画框、字号大、信息密），供**插入 PPT** 与嵌 md。
- 每张图**一次导出两种格式**：`.png`（插 PPT/讲稿）+ `.svg`（嵌 md / 可无限放大）。
- 配色与图元全部来自 `theme.py`，改一处即可全局换肤。

### Step ② 出片（可编辑 PPT + 版面预览）

```bash
python decks/floorplan.py     # 产出可编辑 slides/02_Floorplan.pptx + 逐页版面预览 _preview/
```

> `deck.py` 由一份「幻灯片规格」(specs) **同时**产出两样东西：① `build_pptx` 用 **python-pptx** 写**可编辑** PPT（原生标题/要点文本框 + `add_picture` 插入论文插图，已设中文 ea 字体）；② `build_previews` 用 matplotlib 按**同一套坐标**渲染逐页版面 PNG——因为本机无 LibreOffice 无法渲染 pptx，预览就是**唯一的版面校对手段**（预览看着对，pptx 版面就对）。
> 教案模型：**知识点写在 PPT 页面上**（specs 的 `bullets`），插图作配图；逐页讲解的口播稿单独放 `lecture_scripts/`。

---

## 3. theme.py(v2) 速查

| 函数 | 作用 |
|------|------|
| `canvas(w,h,grid=False)` | 新建画布（等比坐标 0..w/0..h，白底；已关 autoscale） |
| `node(ax,x,y,w,h,title,sub,role,variant)` | 两段色圆角块；`role` ∈ logic/memory/power/io/clock/neutral/ink；`variant` ∈ soft/solid/outline；`header=True` 加芯片式标题条 |
| `rect / line / arrow` | 矩形(可圆角/虚线/投影)、直线、箭头 |
| `flow(ax,items,...)` | 横向流程：一串块自动等分 + 箭头串联 |
| `heading / caption / tag / bracket` | 图标题(小色块+粗字) / 右下署名 / 标签气泡 / 范围括号 |
| `legend / annotate` | 语义色图例 / 带引线标注 |
| `save(fig,outdir,name)` | 同时存 `name.png` + `name.svg` |

配色常量：`BLUE/TEAL/AMBER/ROSE/VIOLET`（各带 `_L` 浅 / `_D` 深）、`INK/INK2/MUTED/LINE/SLATE_L/WHITE`；角色映射 `ROLE`、`MAIN`。

---

## 4. 复用到别的主题（如 Placement / SDC）

1. 复制 `diagrams/floorplan.py` → `diagrams/placement.py`，改 `OUT` 指向 `IC_Backend_Notes/assets/placement/`，用 `theme` 图元写若干 `fXX_*()`。
2. 复制 `decks/floorplan.py` → `decks/placement.py`，改 `DIAS` 列表(图↔要点)与文本页，跑出 `slides/<note>.pptx`。
3. 讲稿 md 里按「每小节一页 + `![](assets/<topic>/fXX.png)` + 讲者备注」组织，与幻灯片一一对应。

> 原则：**一个主题一个 diagrams/ + decks/ 文件；所有视觉规范只在 theme.py / deck.py 里定义一次。**

---

## 5. 设计约定

- 颜色**语义固定**（见顶部），相同含义跨图同色 → 辨识度高、像教科书插图。
- 标签**中英并置**（英文术语为主、中文释义在括号/副标题），中文字体缺失也能读懂。
- 图自包含：白底 + 右下角署名/出处 + 必要处图例，单独导出也成立。
- 几何示意（die/core/电源 mesh/IR 热力图）尽量按真实关系画，不夸张失真。
- 校对用缩略图：`tools/thumbs.py`，避免大图超出查看上限。

---

> 出处：图示内容对应 *Digital VLSI Design (DVD)*, Prof. Adam Teman, Bar-Ilan University (Course 83-612)。整理：**J.C**。
