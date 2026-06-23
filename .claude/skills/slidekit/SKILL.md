---
name: slidekit
description: >-
  Build or update an IC / digital-VLSI backend slide deck from a study note —
  produces paper-grade figures (PNG+SVG), a native-editable PowerPoint .pptx, and
  逐页预览, in the IEEE indigo academic style. Use whenever the user wants an IC
  后端 / digital-VLSI 技术报告 or 讲课 deck (Floorplan, Placement, CTS, Routing,
  SDC, Power, multi-VDD, signoff…) built from notes — especially when they want
  editable PowerPoint with diagrams, data tables, charts, and a references page.
  Runs locally with python (matplotlib + python-pptx); no LibreOffice/Node needed.
---

# slidekit — 笔记 → 论文级插图 + 可编辑 PPT（IEEE 靛蓝学术）

引擎在仓库根目录 **`_SlideKit/`**。完整说明见 [`_SlideKit/README.md`](../../../_SlideKit/README.md) 与 [`_SlideKit/SKILL.md`](../../../_SlideKit/SKILL.md)；本文件是触发入口与速用步骤。

## 何时用

- 从笔记做/改一份 IC 后端或 digital-VLSI 的 deck（Floorplan、Placement、CTS、Route、SDC、Power…）。
- 要**可编辑** PowerPoint（表格能改单元格、图表能改数据），而非贴图。
- 「技术报告 / 答辩 / 讲课」受众：要点是完整句，需要表格 / 图表 / 编号参考文献 / 图号题注。

## 速用（命令从仓库根目录运行）

```bash
python -m pip install -r _SlideKit/requirements.txt      # 首次：matplotlib + python-pptx(>=1.0) + Pillow(>=10)

# 已有桶（floorplan 示例）：
python _SlideKit/notes/05_floorplan/figures.py           # ① 出图（PNG+SVG）
python _SlideKit/notes/05_floorplan/slides.py            # ② 出片：可编辑 .pptx + 逐页预览 PNG

# 报告页型样张（table/chart/refs/带题注 split）：
python _SlideKit/examples/report_sample.py               # → _SlideKit/examples/_out/

python -m pytest _SlideKit/tests/                        # 冒烟测试
```

## 新建一份 deck（按桶复制）

1. 复制 `_SlideKit/notes/05_floorplan/` → `_SlideKit/notes/<NN_topic>/`（一个笔记一个桶）。
2. 改 `figures.py`：`OUT` 指向 `assets/<topic>/`，用 `theme` 图元（优先 `infocard/flowrow/node`）写若干 `fXX_*()`，图幅 ~4:3 / 1:1。
3. 改 `slides.py`：`PPTX/ASSETS/PREV/FOOTER` 指向该笔记，编辑 `SPECS`（按下表选 `kind`）。
4. （可选）教案 md 每小节配图；讲稿放 `lecture_scripts/`。

## 页型 `kind` 速查

| kind | spec 关键字段 | 用途 |
|------|------|------|
| `cover` / `close` | `title, sub?, line?, src?` | 封面 / 收尾 |
| `agenda` | `title, sections=[(num,标题,说明)…]` | 导览（列数随小节数自适应） |
| `split` | `title, figure, bullets, style?, caption?` | 左要点 + 右插图；`caption`→「图 N.」编号题注 |
| `bullets` | `title, bullets, two_col?` | 纯要点（可双栏） |
| `cols2` / `cards2` / `grid6` | 见 `slides.py` 用例 | 双栏要点卡 / 代码对照卡 / 六宫格 |
| `table` | `table={headers, rows, col_align?, col_w?}` | **原生可编辑表格** |
| `chart` | `chart={type:'line'\|'bar', categories, series, x_title?, y_title?}` | **原生可编辑图表** |
| `refs` | `refs=[…]` | 编号参考文献（>8 条自动双栏） |

## 质检（务必）

1. 逐张看预览 PNG：版面、折行、是否出现红字 **⚠ OVERFLOW**。
2. `python -m pytest _SlideKit/tests/`。
3. **分发前用 PowerPoint 真打开一次最终 `.pptx`**（预览≠成稿；折行/字体以 PowerPoint 为准）。
4. 跨机缺 YaHei/Consolas：`build_pptx(..., font=, mono_font=)` 传本机字体名。

## 约定（详见 `_SlideKit/README.md` 第 6 节）

- 要点是**完整句**；并列用 ▪、递进用 ①②③；副标题主题化。
- 全篇统一靛蓝主色；改配色只动 `_SlideKit/theme.py`（单一真源）。
- 课后回顾统一叫「易混淆点 · 课后自测」。

> 源：*Digital VLSI Design (DVD)*, Prof. Adam Teman, Bar-Ilan University (83-612)。整理：**J.C**。
