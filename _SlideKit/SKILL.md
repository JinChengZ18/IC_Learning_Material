---
name: slidekit
description: >-
  Build or update an IC / digital-VLSI backend slide deck from a study note —
  produces paper-grade figures (PNG+SVG), a native-editable PowerPoint .pptx, and
  逐页预览, in the IEEE indigo academic style. Use whenever the user wants an IC
  后端 / digital-VLSI 技术报告 or 讲课 deck (Floorplan, Placement, CTS, Routing,
  SDC, Power, etc.) built from notes — especially when they want editable
  PowerPoint with diagrams, data tables, charts, equations-as-figures, and a
  references page. Runs locally with python (matplotlib + python-pptx); no
  LibreOffice/Node required.
---

# _SlideKit — 笔记 → 论文级插图 + 可编辑 PPT（IEEE 靛蓝学术）

把一篇 IC 后端学习笔记配成一套**可编辑 .pptx**（原生标题/要点 + 表格/图表 + 插入插图）、一组**论文级插图**（PNG 给 PPT、SVG 给 md）和**逐页版面预览**。视觉：靛蓝主色、暖橙仅强调、白底细线、全篇统一不每页换色。

适用于**技术报告**受众：要点是完整句、支持数据**表格 / 图表 / 编号参考文献 / 图号题注**，并有防溢出与 spec 校验。

## 何时用

- 用户要从笔记做/改一份 IC 后端或 digital-VLSI 的 deck（Floorplan、Placement、CTS、Route、SDC、Power…）。
- 用户要**可编辑** PowerPoint（表格能改单元格、图表能改数据），而非贴图。
- 用户提到「技术报告 / 答辩 / 讲课 / 教案 + 讲稿 + deck」一条龙。

## 前置

```bash
python -m pip install -r requirements.txt   # matplotlib + python-pptx(>=1.0) + Pillow(>=10)
```
本机无 LibreOffice/Node：**`build_previews` 的 PNG 是唯一版面校对**（见 README 第 7 节预览保真度边界）。

## 新建一份 deck（按桶复制）

1. 复制 `notes/05_floorplan/` → `notes/<NN_topic>/`（一个笔记一个桶）。
2. 改 `figures.py`：`OUT` 指向 `assets/<topic>/`，用 `theme` 图元（优先 `infocard/flowrow/node`）写若干 `fXX_*()`，图幅 ~4:3 / 1:1。
3. 改 `slides.py`：`PPTX/ASSETS/PREV/FOOTER` 指向该笔记，编辑 `SPECS`（按下表选 `kind`）。
4. （可选）教案 md 每小节配 `![](assets/<topic>/fXX.png)`；另写连贯讲稿到 `lecture_scripts/`。

## 页型 `kind` 速查（在 `SPECS` 里声明）

| kind | spec 关键字段 | 用途 |
|------|------|------|
| `cover` / `close` | `title, sub?, line?, src?` | 封面 / 收尾（独立整版） |
| `agenda` | `title, sections=[(num,标题,说明)…]` | 导览（列数随小节数自适应） |
| `split` | `title, figure, bullets, style?('num'/'bullet'), caption?` | 左要点 + 右插图（最常用）；`caption` → 图下「图 N.」编号题注 |
| `bullets` | `title, bullets, two_col?` | 纯要点（可双栏） |
| `cols2` / `cards2` / `grid6` | 见 `slides.py` 用例 | 双栏要点卡 / 代码对照卡 / 六宫格 |
| `table` | `table={headers, rows, col_align?, col_w?}` | **原生可编辑表格**：主色表头 + 斑马纹 + 数值右对齐 |
| `chart` | `chart={type:'line'\|'bar', categories, series:[(name,[v…])…], x_title?, y_title?}` | **原生可编辑图表** |
| `refs` | `refs=[…]` | 编号参考文献（>8 条自动双栏） |

辅助函数 `split(...)` / `bl(...)` 在 `slides.py` 顶部；`table`/`chart`/`refs` 直接写 dict。

## 构建

```bash
python notes/<NN_topic>/figures.py                       # ① 出图（PNG + SVG）
python tools/thumbs.py ../IC_Backend_Notes/assets/<topic>   # （可选）缩略图供肉眼校对
python notes/<NN_topic>/slides.py                        # ② 出片：可编辑 .pptx + 逐页预览 PNG
```

## 质检（务必）

1. 逐张看 `slides/_preview/prev_*.png`：版面、折行、是否出现红字 **⚠ OVERFLOW**（溢出要精简或缩字号）。
2. `python -m pytest tests/`（折行 / spec 校验 / 母版结构 / 页码字段 / auto-fit / 报告页型）。
3. **分发前用 PowerPoint 真打开一次最终 `.pptx`**：确认折行、表格、图表、字体无误（预览≠成稿）。
4. 跨机器若缺 YaHei/Consolas：`build_pptx(..., font=, mono_font=)` 传本机字体名。

## 约定（避免回退，详见 README 第 6 节）

- 要点是**完整句**；并列用 ▪、递进用 ①②③；副标题主题化、不写制作备注。
- 全篇统一靛蓝主色；改配色只动 `theme.py`（单一真源）。
- 课后回顾统一叫「易混淆点 · 课后自测」。

> 源：*Digital VLSI Design (DVD)*, Prof. Adam Teman, Bar-Ilan University (83-612)。整理：**J.C**。
