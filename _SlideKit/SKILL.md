---
name: slidekit
description: >-
  Build or update an IC / digital-VLSI backend slide deck from a study note —
  produces a native-editable PowerPoint .pptx (titles/bullets, native tables &
  charts, native box-diagrams, paper-grade figures), matching figures (PNG+SVG),
  逐页预览, and a references page, in a single-source academic palette. Use
  whenever the user wants an IC 后端 / digital-VLSI 技术报告 or 讲课 deck
  (Floorplan, Placement, CTS, Routing, SDC, Power…) built from notes — especially
  editable PowerPoint with section dividers, prose-or-bullets-as-appropriate,
  diagrams, tables, charts, equations-as-figures, citations. Runs locally with
  python (matplotlib + python-pptx); no LibreOffice/Node required.
---

# _SlideKit — 笔记 → 可编辑 PPT + 论文级插图 + 讲稿

把一篇 IC 后端学习笔记配成一套**可编辑 .pptx**（原生标题/要点 + 表格/图表 + 原生框图 + 插图）、一组**论文级插图**（PNG 给 PPT、SVG 给 md）、**逐页版面预览**，以及（可选）**连贯口语讲稿**。受众是**技术报告 / 教案**：要点写成完整句、支持表格 / 图表 / 编号参考文献 / 图号题注，带 spec 校验与防溢出。

## 何时用
- 从笔记做/改 IC 后端或 digital-VLSI 的 deck（Floorplan、Placement、CTS、Route、SDC、Power…）。
- 要**可编辑** PowerPoint（表格能改单元格、图表能改数据、框图能拖拽改字），而非贴图。
- 要「教案 + 讲稿 + deck」一条龙，且按笔记小节逐页对应。

## 前置 + 构建 + 质检
```bash
python -m pip install -r requirements.txt        # matplotlib + python-pptx(>=1.0) + Pillow(>=10)
python notes/<NN_topic>/figures.py               # ① 出图（PNG+SVG）
python notes/<NN_topic>/slides.py                # ② 出片：可编辑 .pptx + 逐页预览 PNG
python -m pytest tests/                          # 冒烟测试（折行/spec/母版/页码/auto-fit/报告页型）
```
**本机无 LibreOffice/Node → `slides/_preview/prev_*.png` 是唯一的版面校对**。质检：逐张看预览（注意红字 ⚠ OVERFLOW）；**分发前务必用 PowerPoint 真打开最终 `.pptx`**（预览≠成稿，折行/字体可能差一两字）；跨机缺 YaHei/Consolas 时 `build_pptx(..., font=, mono_font=)`。

## 新建一份 deck（一个笔记一个桶）
1. 复制 `notes/05_floorplan/` → `notes/<NN_topic>/`。
2. 改 `figures.py`：`OUT` 指 `assets/<topic>/`，用 `theme` 图元写 `fXX_*()`，图幅 ~4:3/1:1。
3. 改 `slides.py`：`PPTX/ASSETS/PREV/FOOTER` 指该笔记；按笔记**小节**编 `SPECS`（一小节≈一张），各章之间插 `section()` 分节页。
4. 教案 md 每小节配 `![](assets/<topic>/fXX.png)`；连贯讲稿写到 `lecture_scripts/`。

## 页型 `kind`（在 `SPECS` 声明；助手 `split()/bl()/tbl()/section()` 在 `slides.py` 顶部）

| kind | 关键字段 | 用途 |
|------|------|------|
| `cover` / `close` | `title, sub?, tag?, line?, src?` | 封面 / 收尾（独立整版，浅底 + 左主色厚条） |
| `agenda` | `title, sections=[(num,标题,说明)…], line?` | 导览（列数/行距随小节数自适应 + 底部主线高亮） |
| `section` | `num, title, sub?, items=[小节…]` | **分节标题页**（左主色面板 + 大号章节数字 + 小节清单）；其后内容页右上自动带「第N章·…」面包屑 |
| `split` | `title, sub, figure, bullets, style?, diagram?, caption?, credit?` | 左要点 + 右图（最常用） |
| `bullets` | `title, sub, bullets, two_col?` | 纯要点（可双栏） |
| `cols2`/`cards2`/`grid6` | 见用例 | 双栏要点卡 / 代码对照卡 / 六宫格 |
| `table` | `table={headers, rows, col_align?, col_w?}` | **原生可编辑表格**（主色表头 + 斑马纹 + 数值右对齐） |
| `chart` | `chart={type:'line'\|'bar', categories, series, x_title?, y_title?}` | **原生可编辑图表** |
| `refs` | `refs=[…]` | 编号参考文献（>8 条自动双栏） |

`split` 的 `style`：`bullet`→▪ / `num`→①②③ / **`prose`→整段叙述（不分点）**。`diagram="名"` 用 **PPT 原生框图**（可编辑形状，见下）替代插图。`caption=` 给图号题注；`credit=` 给文献插图来源小字。

## 内容与排版铁律（用户反复强调，**别回退**）
- **要点是完整句**，能独立看懂；**不堆砌「A＞B＞C」式速记**。
- **不滥用分点**：叙述段落用 `style="prose"`；**只在真正的列表（原则/步骤/并列项）才分点**——并列 ▪、递进/有序 ①②③。
- **副标题主题化**，不写「24页/8句话带走/吃什么吐什么」这类制作备注；图里不放草稿性标签、**不加无意义编号**（单标题图别用 `sechead("①",…)`）。
- **简单框图（流程/树/框图）用 `diagram=` 原生形状**（`deck.DIAGRAMS`，一份布局同时驱动 pptx 原生形状与 matplotlib 预览）；**空间/版图/热力/真实照片类**才用 matplotlib 图片或文献插图。
- **图、要点、页码、母版件互不遮挡**；导览/分节页主线条让开页码。
- 讲稿是**一堂连贯的课**：每节开头有「过渡 + 为什么接着讲它」，贯穿主线；无 `[指…]`/口头禅/「用法」前言。
- 课后回顾统一叫「**易混淆点 · 课后自测**」（完整疑问句），**不用「面试」字样**。
- **严格按笔记**：归纳/数字/术语忠于原文，别自创。

## 配色（单一真源）
只改 `theme.py` 的 `BLUE/TEAL/AMBER/ROSE/VIOLET`（各带 `_L`/`_D`）+ `SOFT`（已直接引用 `_L`）+ `CARD_EDGE`，跑一次 `figures.py` 即全局换肤（**变量名不变、只改 hex**）。`deck.PRIMARY/ACCENT = T.BLUE/T.AMBER.lstrip('#')`，chrome 自动跟随。配色随用户口味变过多轮（清华紫→鲜明多色→…→当前**深清华紫 `#46196B`** 主色），别假设是某一版——以 `theme.py` 现值为准。**别滥用透明色 / 浅色（会显"粉/浅"）**：`_L` 调已加深；关键框图用**实色 solid 变体**（饱和填充 + 白字，见 `_drole3` / `_dbox(variant="solid")`），原生框图的强调框（pnr 四任务 / loop 四环 / hier flat）已是 solid。

## 母版（版式）机制——便于扩充
重复的【左主色竖条 + 全宽细分隔线 + 页脚标签】由 `_layout_chrome` 下放到**版式**（python-pptx 不支持直接给版式加形状，故先在草稿页画好再把 XML 复制进版式、删草稿页）；内容页自动继承、新增页自动带样式。`_clean_master` 删掉默认模板的 **4:3 占位符**（日期/页脚/`<#>`，否则与自定义页脚重叠且 16:9 母版视图显示不对）与未用版式，只留一张干净 16:9 版式。页码用 PowerPoint **原生 `slidenum` 字段**（自动随增删页更新）；左下页脚是 `build_pptx(page_label=…)` 参数（随笔记而变）。

## 文献插图流水线（增强说明力，**务必标注 + 注意版权**）
程序画的是示意图；真实照片 / 版图截图 / IR 颜色图等需引自文献。**两个来源，不依赖本地**：
- 本地 PDF：`python tools/extract_figs.py <lecture.pdf>` → 提取**嵌入位图** → `lit/<pdf名>/`（已 gitignore）+ `manifest.csv`。
- 文献检索：用 Claude 的 WebSearch / WebFetch 按主题找相关图 + 其**来源与许可**（开放获取论文、Wikimedia/CC、厂商公开资料）。
挑合适的 → `split(..., figure="lit/<…>.png", credit="来源：…")`；deck 末尾 `refs` 页列参考文献。
**版权红线（重要）**：第三方图版权属原始来源（讲义也转引 Cadence / Rabaey / Weste-Harris 等）。**入库（git）的 deck 只用自绘原创图**——把第三方图嵌进会被提交的 pptx＝把版权图复制进仓库。真实文献图只在**本地个人学习副本**里插，且**只用开放许可（CC / 公有领域）或自有课程材料**、使用处必标来源；`lit/` 与含版权图的 pptx 都不要提交。要找图 / 许可可让 Claude 跑 WebSearch，但它不会替你把版权图提交进库。
- 想让 deck 自己更"像真图"而无版权顾虑：升级 `figures.py` 的原创图（IR 热力、die / 版图、电源网格已是原创，可继续做细）。

## 环境 GOTCHA
- 代码/等宽块文字必须 **ASCII**（Consolas/等宽字体无 CJK→豆腐块）；YaHei 缺 `⊃ ↔ ≠ ✓ ✗ ⑪+` 等字形 → 用 `＞ / — / != / 文字` 代替。
- `infocard` 的 `role` 必须是合法键（logic/memory/power/io/clock/neutral）。
- **git**：在检查点提交（曾因无 git 丢过被覆盖的历史版本）；`.gitignore` 注释必须单独成行（行内注释不生效）。外部 linter 会在 `.md` 旁自动生成滞后的 `.pdf`，别拿它当最新版。

> 源：*Digital VLSI Design (DVD)*, Prof. Adam Teman, Bar-Ilan University (83-612)。整理：**J.C**。
