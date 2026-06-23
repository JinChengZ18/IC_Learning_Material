# _SlideKit — 笔记 → 论文插图 → 可编辑 PPT + 讲稿 流水线

把一篇学习笔记（如 [`IC_Backend_Notes/05_Floorplan.md`](../IC_Backend_Notes/05_Floorplan.md)）配成一套**论文/图书级插图**、一份**可编辑演示文稿**和一份**口语讲稿**。与 `_BiliKit`（B站→字幕）同级，是本仓库第二个可复用引擎。

> 视觉：**IEEE 靛蓝学术**（低饱和、近双色）。主色靛蓝 `#1F3A8A`，暖橙 `#C2772E` **仅作强调**；钢青 `#3F7C8C`/砖红 `#A6473C`/板岩 `#4C4A78` 为降饱和语义色；墨字 `#1A1F2B`、白底、细线。**全篇统一主色，不每页换色。** 图幅统一 **~4:3 / 1:1**，作 16:9 幻灯片右栏侧插图。

---

## 1. 目录结构（按笔记分桶）

```
_SlideKit/
├─ theme.py            # 主题引擎：靛蓝配色 + 字号层级 + 图元(node/infocard/flowrow/sechead/save…)
├─ deck.py             # 幻灯片版面 + build_pptx(python-pptx) + build_previews(matplotlib 校对)
│                      #   母版：重复的标题条/分隔线/页脚由 _layout_chrome 下放到【版式】
├─ tools/
│   ├─ thumbs.py       # 大图 → <=1280px 缩略图(<dir>/_qa)，便于肉眼校对
│   └─ inspect_pptx.py # 导出某 .pptx 的母版主题/版式/配色/字体，作参考
├─ notes/              # ★ 每篇笔记一个桶（project management）
│   └─ 05_floorplan/
│       ├─ figures.py  # 该笔记全部插图函数 → assets/floorplan/f01..f15
│       └─ slides.py   # 该笔记幻灯片规格(SPECS) → slides/05_Floorplan.pptx
│   (将来：02_rtl/、03_inputs/、04_sdc/、06_placement/ …)
├─ requirements.txt    # matplotlib + python-pptx + Pillow
└─ README.md

产物（落在对应笔记目录下，便于 md 相对路径引用）：
IC_Backend_Notes/
├─ assets/floorplan/              # f01..f15 .png(插 PPT) + .svg(嵌 md)，_qa/ 缩略图
├─ slides/05_Floorplan.pptx       # 可编辑 PPT，_preview/ 为逐页版面预览 PNG
├─ 05_Floorplan.md                # 教案（知识点在页、备注精简）
└─ lecture_scripts/05_Floorplan.md   # 口语讲稿（连贯成课、可照念）
```

---

## 2. 两步流水线（以 floorplan 桶为例）

```bash
python -m pip install -r requirements.txt                       # 首次
python notes/05_floorplan/figures.py                            # ① 出图（PNG + SVG，~4:3/1:1）
python tools/thumbs.py ../IC_Backend_Notes/assets/floorplan     #   （可选）生成缩略图供校对
python notes/05_floorplan/slides.py                             # ② 出片：可编辑 .pptx + 逐页预览
```

> **本机无 LibreOffice / Node**，无法把 pptx 渲染成图。`build_previews` 用 matplotlib 按**同一套坐标**画出逐页 PNG（`slides/_preview/`）——这是**唯一**的版面校对手段。预览端会**按显示宽度折行**（`_wrap`/`_pbul`），所以预览能如实反映 pptx 的自动换行。

---

## 3. theme.py 速查

| 类 | 函数 |
|----|------|
| 画布/保存 | `canvas(w,h)`（白底、关 autoscale）· `save(fig,outdir,name)`（png+svg） |
| 图块 | `node(role,variant)`（soft/solid/outline 两段色块）· `rect/line/arrow` |
| **卡片风** | `infocard(title,detail,role,highlight)` · `flowrow(items)`（chevron 流程带高亮）· `sechead(num,text)`（①带圈分节标题） |
| 标注 | `legend / annotate / tag / bracket / heading / caption` |

- **配色（换肤只改这里）**：`BLUE/TEAL/AMBER/ROSE/VIOLET`（各带 `_L`/`_D`）+ `SOFT`(卡片浅底) + `CARD_EDGE`。**变量名不变、只改 hex**，跑一次 `figures.py` 即全局换肤（`figures.py` 不用动）。`INK/INK2/MUTED/LINE/SLATE_L`、`ROLE`/`MAIN` 为派生。
- **字号层级**：`FS_H1=24 > FS_H2=19 > FS_BODY=17 > FS_CAP=15`。图被缩到 ~0.78 插入幻灯片，故图内字号要**调大**才看得清；图元默认字号也已同步上调。
- 代码块文字必须 **ASCII**（等宽字体无 CJK→豆腐块）；YaHei 缺字符（⊃ ↔ ≠）改用 ＞ / — / !=；`infocard` 的 `role` 必须是合法键（logic/memory/power/io/clock/neutral/ink）。

---

## 4. deck.py：母版（版式）与页型

**母版机制（便于扩充）**：每页重复出现的【左侧主色竖条 + 全宽细分隔线 + 左下页脚标签】由 `_layout_chrome(prs, layout)` 一次性放到**版式（slide layout）**上，所有内容/导览页**自动继承**。
- 要全局改样式（条色 / 分隔线 / 页脚 / 底色），改 `theme/deck` 里那一处常量即可，或直接在 PowerPoint「视图 → 幻灯片母版」里改版式——**新增幻灯片自动带样式**。
- **页码**用 PowerPoint **原生 `slidenum` 字段**（每页一个 `<a:fld type="slidenum">`，增删/重排页**自动更新**，不写死 "N/24"）；**左下页脚标签**是 `build_pptx(..., page_label=…)` 参数（**随笔记而变**，如 `Floorplan · 布图规划`），左/右分置不与页码重叠。
- 实现细节：python-pptx 不支持直接给版式加形状，故 `_layout_chrome` 先在草稿页画好、再把形状 XML 复制进版式、删草稿页；`_clean_master` 删掉默认模板的 **4:3 占位符**（日期/页脚/页码）与未用版式，只留一张干净的 **16:9** 版式。
- 封面 / 收尾页是整版独立设计，用 `_mask(slide)` 盖一层满版白底遮住继承来的母版件，再画自己的版面。

**页型（spec `kind`）**，在 `slides.py` 的 `SPECS` 里声明：

| kind | 用途 |
|------|------|
| `cover` | 封面（独立整版：左厚竖条 + 大标题 + 主线高亮） |
| `agenda` | 导览（①…⑦ 编号小节双列 + 底部主线高亮条） |
| `split` | 左要点 + 右插图（最常用）。`style="num"`→要点用 ①②③，缺省 `style="bullet"`→▪ |
| `bullets` | 纯要点（`two_col=True` 双栏） |
| `cols2` / `cards2` / `grid6` | 双栏要点卡 / 代码对照卡 / 六宫格 |
| `close` | 收尾（独立整版，与封面呼应） |

---

## 5. 复用到别的主题（如 Placement / SDC）

1. 复制 `notes/05_floorplan/` → `notes/06_placement/`。
2. 改 `figures.py`：`OUT` 指向 `assets/placement/`，用 `theme` 图元（优先 `infocard/flowrow` 卡片风）写若干 `fXX_*()`，图幅取 ~4:3/1:1。
3. 改 `slides.py`：`PPTX/ASSETS/PREV` 指向该笔记，编辑 `SPECS`（按上表选 `kind`）。
4. 教案 md 每小节配 `![](assets/<topic>/fXX.png)`，与幻灯片逐页对应；另写一份连贯讲稿放 `lecture_scripts/`。

> 原则：**一个笔记一个 `notes/<NN_name>/` 桶；所有视觉规范只在 `theme.py` / `deck.py` 里定义一次。**

---

## 6. 内容与排版约定（务必遵守，避免回退）

- **要点必须是完整句**：有主谓、能独立看懂；**不要堆砌"A ＞ B ＞ C"式难懂的速记要点**。
- **并列 vs 递进**：并列内容用 ▪（`style="bullet"`）；递进/有序内容用 ①②③（`style="num"`）。不要把递进内容硬塞成并列要点。
- **副标题要主题化**，不写"24 页 / 8 句话带走 / 吃什么吐什么"这类**制作备注（草稿味）**；图里也不放草稿性标签。
- **不与文字遮挡**：图、要点、页码、母版件互不压盖（如导览主线条要让开右下页码）。
- **讲稿是一堂连贯的课**：每节开头有**过渡 + 为什么**（为什么接着讲这个、和上一步什么关系），贯穿"Floorplan 决定 PPA / 迭代闭环"主线；无 `[指…]` 指图提示、无"用法"说明、无"各位同学/那么/对吧"口头禅。
- 课后回顾章节统一叫 **「易混淆点 · 课后自测」**（完整疑问句），**不用"面试"字样**。

---

## 7. 环境与限制

- 本机：Python 3.10 + `matplotlib` + `python-pptx` + `Pillow`。**无 LibreOffice/soffice、无 Node/npm、无 pdftoppm** → 不能把 pptx/pdf 渲染成图；`build_previews` 的 PNG 是唯一版面校对。
- **没有现成的 PPT 制作 skill**（市场仅有网页向 `frontend-design`；Anthropic 的 pptx skill 未装且依赖 LibreOffice）→ **_SlideKit 即工具**。
- 外部 watcher/linter 会在编辑 `.md` 旁自动生成同名 `.pdf`（可能滞后于源文件，别拿它当最新版）。

---

> 出处：图示内容对应 *Digital VLSI Design (DVD)*, Prof. Adam Teman, Bar-Ilan University (Course 83-612)。整理：**J.C**。
