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
  diagrams, tables, charts, equations-as-figures, citations. Builds locally with
  python (matplotlib + python-pptx); accurate WYSIWYG QA renders the real .pptx
  with LibreOffice.
---

# _SlideKit — 笔记 → 可编辑 PPT + 论文级插图 + 讲稿

把一篇 IC 后端学习笔记配成一套**可编辑 .pptx**（原生标题/要点 + 表格/图表 + 原生框图 + 插图）、一组**论文级插图**（PNG 给 PPT、SVG 给 md）、**逐页版面预览**，以及（可选）**连贯口语讲稿**。受众是**技术报告 / 教案**：要点写成完整句、支持表格 / 图表 / 编号参考文献 / 图号题注，带 spec 校验与防溢出。

**分工**：`.md` 教案是**纯文字文本源**（不嵌图）；图只活在 PPT 里（`figures.py` 自绘或文献真图）；口语**讲稿**在 `lecture_scripts/`。教案 / 讲稿 / slides 三者内容一致、**都向已人工润色的版本对齐**（讲稿改了→同步 slides 文字；笔记改了→同步 slides）。slides 逐小节对应笔记。

## 何时用

- 从笔记做。
- 要**可编辑** PowerPoint（表格能改单元格、图表能改数据、框图能拖拽改字），而非贴图。
- 要「教案 + 讲稿 + deck」一条龙，且按笔记小节逐页对应。

## 前置 + 构建 + 质检

```bash
python -m pip install -r requirements.txt        # matplotlib + python-pptx(>=1.0) + Pillow(>=10)
python notes/<NN_topic>/figures.py               # ① 出图（PNG+SVG）
python notes/<NN_topic>/slides.py                # ② 出片：可编辑 .pptx + 逐页预览 PNG
python -m pytest tests/                          # 冒烟测试（折行/spec/母版/页码/auto-fit/报告页型）
```
**校对两条路**——两者都看：
- **快近似**：`slides/_preview/prev_*.png`（matplotlib 直接画，秒出，但字体/换行/自动缩字号与真 PPT 会差）。日常改稿用它。
- **真成稿**：`python tools/pptx_qa.py` —— 用 **LibreOffice**（soffice，**已安装**）把 `.pptx` 渲成 PDF，再用 PyMuPDF 渲成 `slides/_qa/qa_*.png`。这是**真实 PowerPoint 成稿**的样子，最终校对以它为准。
逐张看（注意预览里的红字 ⚠ OVERFLOW）；跨机缺 YaHei/Consolas 时 `build_pptx(..., font=, mono_font=)`。

**内联强调（两种标记，均仅 pptx 渲染、预览 `_wrap` 去标记）**：
- `**重点**` → **加粗 + 强调色（橙）**：专点**总分结构的中心短句**，以及**标题 / sub 术语缩写（ILM / PDN / EM / PG …）的中英对照**作寻路锚点（每页≤1~2 处、别整段加粗）。
- `__重点__` → **普通加粗（无橙）**：专用于**总分式结构里各分点的「术语头」**——当「引导句 L(以：结尾) ＋ ≥3 个 ▪ 分点、且分点为『中文（English）：解释』形态」时，把每个分点开头的术语头 `__…__` 包裹（如 1.5「__设计网表（design netlist）__：…」、2.6 三种阻挡、3.1 优点/代价、4.3 EM 三态），强化视觉分割、不抢橙色。
- 两者可同页 / 同行并存（如 4.3「**电迁移（EM）**是**…机制…**」）。由 `deck._emph_segs` 解析（码 1=橙 / 2=普通加粗 / 0=常规）。

## 新建一份 deck（一个笔记一个桶）
1. 复制 `notes/05_floorplan/` → `notes/<NN_topic>/`。
2. 改 `figures.py`：`OUT` 指 `assets/<topic>/`，用 `theme` 图元写 `fXX_*()`，图幅 ~4:3/1:1。
3. 改 `slides.py`：`PPTX/ASSETS/PREV/FOOTER` 指该笔记；按笔记**小节**编 `SPECS`（一小节≈一张），各章之间插 `section()` 分节页。
4. 教案 md 保持**纯文字**（不嵌图，图只进 PPT）；连贯讲稿写到 `lecture_scripts/`。

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

`split` 的 `style`：`bullet`→▪ / `num`→①②③ / **`prose`→整段叙述（不分点）**。`diagram="名"` 用 **PPT 原生框图**（可编辑形状，见下）替代插图。`caption=` 给图注「图 N · …」；`credit=` 给来源小字；`figs=[fg(路径,图注,来源),…]` 右栏**并排多图**（各带图注）。

## 内容与排版铁律（用户**反复**强调、**反复踩**，别再回退）
- **要点是完整句**，能独立看懂；**不堆砌「A＞B＞C」式速记**。
- **混合体裁、逐段对齐笔记（对齐含分点格式，不只是文字）**——同一页 body 可混用四种：散文段 `P("…")`、引导句 `L("…：")`（P/L 均**无标记整段**）、并列项 `B("…")`(▪)、有序项 `N("…")`(①，仅 N 计数)。笔记是「散文 + 列表 + 散文」的小节就照搬这结构（如 1.1/2.4/2.6/2.7/4.3/4.7），**别把散文框架也分点、别给非列表项编号**；纯散文小节整页 `P`（或 `style="prose"`）。（**滥用分点是多次返工的坑**。）
- **内容最大限度对齐笔记、别过度精简**（便于自学）：笔记有、对理解重要的点要补回；表格列/行按笔记给足（别留大片空白）。可用 `notes/05_floorplan/_content_audit.wf.js`（5 章并行 note↔slide diff）找漏点。
- **没有草稿性 / 自言自语 / 元说明文字上幻灯片**（屡犯）：删掉「24页/8句话带走/吃什么吐什么」「（引用文献插图时图下另标…）」「坑：…」这类制作备注或给自己看的说明；副标题要**主题化**；图里不放草稿标签、**不加无意义编号**。
- **引用统一进参考文献(`refs`)专页**，**不要硬编码进封面/封底/标题页**；封面/封底只留署名（`BYLINE="整理 J.C"`），课程出处、教材、工具手册等都列在 refs 页；逐图来源用 `split(credit=)`。
- **图片分两类**：**简单示意图（流程/树/框图）→ `diagram=` 原生形状**（`deck.DIAGRAMS` 一份布局同驱动 pptx 形状 + 预览，已含 pnr/io/hier/uniquify/loop）；**空间/版图/热力/照片等"真插图"**→ 真实文献图。**版权红线**：会入库的 pptx 只用自绘原创图，第三方/讲义真图只在本地副本插、且只用开放许可或自有材料、必标来源（见下「文献插图流水线」）——别因为用户想要就把版权图提交进库。
- **图、要点、页码、母版件互不遮挡**；导览/分节页主线条让开页码。
- **副标题（sub）必须单行、且落在 1.6″ 母版分隔线之上**：`_title_block` 的 sub 框已改为**全宽** `(0.87, 1.18, 11.85, 0.32)` + `wrap=False`（跨 0.85..12.70、与分隔线同宽），单行可容很长 sub、不折行下探越线；与右上「第N章」面包屑分属标题行 / 副标题行、纵向分离不冲突。前提是 **sub 写短**——可省细节（如 DOI 书写格式这类脚注）移出 sub 到正文 / `refs`（图片来源页即如此）。预览端 `_mtext` 按单点放置不折行，与 pptx 天然一致，无需改预览。
- 讲稿是**一堂连贯的课**：每节开头有「过渡 + 为什么接着讲它」，贯穿主线；无 `[指…]`/口头禅/「用法」前言。
- **严格按笔记**：归纳/数字/术语忠于原文，别自创；**首次出现的英文专有名词用「中文（English）」中英对照**（沿用笔记配对，如 布图规划（floorplan）、硬宏（hard macro）、留边（halo）、电源分布网络（PDN）、穿通（feedthrough）…）。
- **文档与幻灯片的加粗保持一致**：凡幻灯片强调的短语（无论 `**橙**` 还是 `__普通加粗__`），在 `note.md` 对应句用 markdown `**…**` 同样加粗（note 无颜色，只标「哪些是重点」）；改一边就同步另一边，保持两侧「加粗短语集合」一致。
- **纯表格页别只有表**：笔记里表前后的引言 / 定义 / 结论用 `tbl(..., note="…")` 补进来——按**正文字号 14** 渲染（= split 正文同号，`deck._NOTE_FS`，不是小灰脚注），排在**表格上方**（顶左起、说明在前、表在后，符合阅读流）；`deck._table` 自动缩表留位。表格列 / 行按笔记给足，别留大片空白。
- **深入算法层（可选增强）**：笔记只有概念、需补算法时——先**按发展脉络（developmental thread）梳理**（时间轴 / 几代演进），再**分点把 landmark 算法讲透**，其余同类入**对比表**或一句话带过（别铺平、别罗列）。每个关键算法**配一张 `figures.py` 示意图**（命名延续 `fNN_*`、避开已用号；note 仍**纯文字不嵌图**，图只进 PPT）。**note / 讲稿 / slides 三处内容一致**（同一 syllabus 驱动，逐小节对应）。**忠于权威教材、不臆造**：以教材为单一真源（如《Handbook of Algorithms for Physical Design Automation》Floorplanning 部分 Ch.8–13），存疑处标注而非编造；可用 Read 的 `pages` 参数读本地 PDF 做 grounding。Floorplan landmark 示例：Polish 表达式 / Stockmeyer 形状曲线 / Wong–Liu 模拟退火 / Sequence Pair / B\*-tree / TCG / 固定轮廓 floorplanning。

## 配色（单一真源）
只改 `theme.py` 的 `BLUE/TEAL/AMBER/ROSE/VIOLET`（各带 `_L`/`_D`）+ `SOFT`（已直接引用 `_L`）+ `CARD_EDGE`，跑一次 `figures.py` 即全局换肤（**变量名不变、只改 hex**）。`deck.PRIMARY/ACCENT = T.BLUE/T.AMBER.lstrip('#')`，chrome 自动跟随。**别滥用透明色 / 浅色（会显"粉/浅"）**：`_L` 调已加深；关键框图用**实色 solid 变体**（饱和填充 + 白字，见 `_drole3` / `_dbox(variant="solid")`），原生框图的强调框（pnr 四任务 / loop 四环 / hier flat）已是 solid。

## 母版（版式）机制——便于扩充
重复的【左主色竖条 + 全宽细分隔线 + 页脚标签】由 `_layout_chrome` 下放到**版式**（python-pptx 不支持直接给版式加形状，故先在草稿页画好再把 XML 复制进版式、删草稿页）；内容页自动继承、新增页自动带样式。`_clean_master` 删掉默认模板的 **4:3 占位符**（日期/页脚/`<#>`，否则与自定义页脚重叠且 16:9 母版视图显示不对）与未用版式，只留一张干净 16:9 版式。页码用 PowerPoint **原生 `slidenum` 字段**（自动随增删页更新）；左下页脚是 `build_pptx(page_label=…)` 参数（随笔记而变）。

## 真实插图流水线

**找图**（用 Claude 的 WebSearch + WebFetch，可用 `notes/05_floorplan/_oa_*.wf.js` 这类**逐页并行检索 workflow**）：可取且许可清晰的源依次是 **Wikimedia Commons**（`upload.wikimedia.org` 直链）、**CC-BY 开放获取论文**（arXiv 逐篇看 License=CC BY/BY-SA、MDPI/PMC/Frontiers/IEEE-Access，带 **DOI**；注意 MDPI 站点常 403 取不到图）。本地讲义另有 `tools/extract_figs.py`（抽 PDF 位图→ gitignored `lit/`，仅本地个人学习用）。
**下载**：`Invoke-WebRequest`（带 UA）→ PIL `thumbnail` 缩到 ~1500px 存到 `assets/<topic>/ext_*.{jpg,png}`（命名标注来源/许可，如 `ext_die_i9_cc0.jpg`）。
**插入 + 标注**：

- 单图：`split(..., figure="ext_*.png", caption="图注：这张画了啥", credit="作者 · arXiv:xxxx / Wikimedia · 许可")`；`caption=`→「图 N · …」图注（**图号全 deck 连续编**），`credit=`→图下「来源：…」小字。
- 多图：`split(..., figs=[fg(路径, 图注, 来源), fg(...)])`——右栏多图、各带图注（`deck._split_figs`/`_psplit_figs`，1–3 张）。默认**左右并排**（配方/竖图用）；**宽图**（拥塞/IR 热力图、流程图）加 `figs_v=True` 改**上下堆叠**才不致压扁。
- deck 末尾两页：**参考文献 References**（内容来源）+ **图片来源 Image Credits**（每图 作者 / 许可 / **DOI**；>8 条自动双栏 + `_fit_scale` 缩字号防溢出）。
**何时仍自绘**：找不到「开放许可 + 可取 + 强相关」三者齐全的真图时（如 placement halo/blockage、IR-on-layout 这类概念，开放图稀缺），保留 `figures.py` 自绘示意——示意图能精确标注概念，有时比真图更利于教学。简单流程/框图仍用 `diagram=` 原生形状。

## 环境 GOTCHA
- 代码/等宽块文字必须 **ASCII**（Consolas/等宽字体无 CJK→豆腐块）；YaHei 缺 `⊃ ↔ ≠ ✓ ✗ ⑪+` 等字形 → 用 `＞ / — / != / 文字` 代替。
- `infocard` 的 `role` 必须是合法键（logic/memory/power/io/clock/neutral）。
- **git**：在检查点提交（曾因无 git 丢过被覆盖的历史版本）；`.gitignore` 注释必须单独成行（行内注释不生效）。外部 linter 会在 `.md` 旁自动生成滞后的 `.pdf`，别拿它当最新版。

> 源：*Digital VLSI Design (DVD)*, Prof. Adam Teman, Bar-Ilan University (83-612)。整理：**J.C**。
