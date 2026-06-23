# Floorplan 布图规划 · 口语讲稿

> 课程原版 (English source): Adam Teman, *Digital VLSI Design (DVD)*, Bar-Ilan University · Course 83-612 · <https://enicslabs.com/academic-courses/dvd-english/>
> 整理：**J.C**
>
> **用法**：逐页讲稿，可照念；精简去口头禅，只留干货。`[]` 内为讲者指图提示，不念出来。

---

## Slide 1 · 封面：Floorplan 布图规划

Floorplan，布图规划，是把综合得到的「逻辑网表」映射成「物理布局骨架」，是物理实现（P&R）里第一个确定版图骨架的步骤。全讲一条主线：**Floorplan 决定 PPA 上限，一步错、步步错——上游决定下游天花板。**

---

## Slide 2 · 本讲导览

本讲七块：① 定位与意义；② 几何（Die/Core/IO）、利用率、长宽比、Row/site/翻转供电轨；③ 宏摆放、halo/blockage、专用单元（endcap/well-tap/filler）；④ IO/Pad/Bump 与引脚分配；⑤ 电源（ring/stripe/mesh/rail/sroute）、IR drop/EM、电源门控；⑥ 多电压域与 UPF、时序预算；⑦ 拥塞/IR 早期预估与迭代闭环，加指标、文件、命令、考点。贯穿全讲的一个观念：Floorplan 是「floorplan→试布局/GR→评估→回退」的**迭代闭环**，不是一遍过。

---

## Slide 3 · 什么是 Floorplan

[指流程位置] Floorplan 在综合产出门级网表之后、详细 Placement 之前；再往前是「设计导入/初始化」——读库（LEF/Liberty/NDM）、读网表、加载 SDC 与 UPF/CPF、初始化。它的六项任务：① die/core 几何；② 宏（Macro/hard IP）的位置与朝向；③ IO/Pad/Bump 与引脚分配；④ PG 电源骨架（环/条/网）；⑤ 多电压域与电压岛边界；⑥ 各类 blockage 与 halo/keepout。本质是把逻辑网表映射成物理骨架，为后续 Placement、CTS、Routing 划定边界。工具上，综合用 DC 或 Genus，而 Fusion Compiler 是综合加 P&R 一体的实现工具。

---

## Slide 4 · 为什么重要：一步错，步步错

Floorplan 决定芯片 PPA（性能/功耗/面积）的上限。三类典型代价：利用率定高，Placement 再优秀也拥塞绕不出；宏摆放不合理，关键路径绕远、时序收不回；PG 规划不足，签核才发现 IR drop 或 EM 超标，往往推倒重做。关键成本规律：Floorplan 阶段改几乎免费，越往后（布线、签核）改成本急剧上升。「七分布局三分布线」是经验俗语、不是量化指标，只为强调早期版图决策的份量。

---

## Slide 5 · 芯片几何：Die / IO / Core / Rows

[指由外到内] 芯片由外到内层层嵌套。Die Area（晶粒区）：最外边界，含 scribe 切割道。IO 区/Pad Ring：Die 与 Core 之间的环形区，放 IO 单元与 Pad。Core Area（核心区）：放标准单元与宏。Core-to-IO Spacing：Core 边界到 Pad 内沿的距离，留给电源环与 IO 走线。Core 内被切成等高的标准单元行 Rows。嵌套关系：Die ⊃ Pad Ring ⊃ Core ⊃ (Macro + Rows)。

---

## Slide 6 · 标准单元行 / site / 翻转共享供电轨

[指两行交界] Row：Core 切成等高水平行，行高 = 库单元高度（9T/7T）≈ track 数 × M2 pitch，所以 9T 行高 > 7T。Site：行内最小放置栅格，定义于 LEF，单元宽度必须是 site 宽度的整数倍。核心机关——翻转共享供电轨：相邻行镜像翻转（FS，绕水平中线），同名电源轨就落在行边界、被上下两行共享，于是供电轨条数减半、面积更省，follow-pin rail 保持连续。LEF 里 `SYMMETRY Y` 描述单元自身镜像方式；行间共享靠相邻行上下镜像，轴向以工具/库文档为准。

---

## Slide 7 · 利用率与长宽比

利用率有两个口径，务必分清。总利用率 Total Util =（Σ单元 + Σ宏）/ Core 面积；有效利用率 Effective Util = Σ单元 /（Core − blockage − macro halo − keepout），工具报告多指后者。经验初值 0.5–0.8，不是固定 60–75%：宏多、IP 密集、datapath 可超 0.8，拥塞高/活动率高则留余量降到 0.5–0.6。易混点：目标利用率 ≠ placement 后的局部密度（placement density）。长宽比 Aspect Ratio = core 高/宽——各工具约定可能相反，以文档为准；比值 ≈1（方正）最利于布线均衡与时钟树，长条形长边易拥塞、skew 难控。对应 ICC2 `-side_ratio {1 1}`、Innovus `floorPlan -r 1.0`。

---

## Slide 8 · 宏单元摆放原则

宏（Macro）= SRAM/ROM/PLL/ADC/IP 核，尺寸大、形状与引脚固定，是 floorplan 的核心难点。五条原则：① 沿边/沿角，中间留给标准单元，别在中央挖洞；② 按数据流就近，用 flyline 飞线指导，现代有 auto macro placer 按 connection weight 自动布大块 IP；③ 留 channel 走 PG/时钟/信号，或 channel-less 紧贴（abutted，省面积但 pin access 要求高）；④ 引脚朝 core，避免信号绕过宏本体；⑤ 朝向（R0/R90/R180/R270 + 镜像 MX/MY 共 8 种）与对称背靠背、对齐成规整阵列。摆不好就等于给布线设障碍、拉长走线，最终是拥塞与时序问题。

---

## Slide 9 · halo / keepout 与各类 blockage

区分 halo 与 blockage，高频考点。Halo/Keepout Margin：macro 四周「不放标准单元」的边带，留给 pin access、电源、缓冲，**跟随 macro 移动**。Placement Blockage：钉在**固定坐标**的禁放区，分 hard（全禁）、soft（粗放阶段禁、优化阶段可放 buffer）、partial（按密度上限，与 density screen 相近但实现/命名因工具而异、不等价）。Routing Blockage：禁某些层布线，可指定层范围（如 M1–M3），分 hard/partial。经验：macro 引脚侧加 halo 给 pin access 留空间。记一句：halo 跟 macro 走，blockage 钉在坐标上。

---

## Slide 10 · 物理专用单元：endcap / well-tap / filler

三种 physical-only cell，不参与逻辑，但关乎 row/供电轨/N-well 连续，需在 floorplan 或早期 placement 规划。Endcap/Boundary：放每行两端及 macro/void 边界，保 well/implant 连续与 DRC。Well-tap/Tap：周期插入提供 well 偏置接触，间距须满足工艺的 max well-tap distance（DRC），否则 latch-up（闩锁）风险与 DRC 报错，间距要在 floorplan 早期就规划。Filler：布线前/末期插入，填行内空隙、保供电轨与 well 连续，时机晚于 tap/endcap。两个考点：tap 间距违规会 latch-up，filler 最后才放。

---

## Slide 11 · IO / Pad、Bump 与引脚分配（上）

两种封装思路。Wire-bond（引线键合）：IO Pad 沿 die 四周排成 Pad Ring 金线键合，要考虑信号/电源 Pad 交替、ESD、Corner Pad。Flip-Chip（倒装焊）：信号经 die 表面的 Bump 面阵列（area array）从正面引出，常配 RDL 重布线层——是否需要完整 RDL 取决封装/凸点布局，部分 flip-chip/WLCSP 直接落顶层金属或 UBM。bump 要对齐封装 bump map，控间距与电源/信号比例。一句话：wire-bond 走四周 pad ring，flip-chip 走面阵列 bump。

---

## Slide 12 · 引脚分配 Pin Assignment（下）

引脚分配分两级。顶层：IO buffer 位置决定芯片对外引脚。块级（hierarchical）：partition 对外端口分配到块边界的具体位置，pin 位置直接决定块间走线长度与时序。核心约束：① 落合法 routing track，且与该层布线方向一致；② 沿数据流方向分布（逻辑在左则 pin 放左边界），避免长绕线；③ 注意 feedthrough——信号穿无关 block 需预留穿通端口/缓冲，否则被迫绕整个 block；④ 工具可自动优化，关键总线常需手工约束（`set_block_pin_constraints` / `place_pins`）。pin 离逻辑越远，块内走线越长、budget 越紧——与时序预算耦合。

---

## Slide 13 · 电源规划：Ring → Stripe → Mesh → Rails

[指由粗到细] PG 网络自上而下、由粗到细。Power Ring：沿 core/macro 边界的闭合环，顶层粗金属主干供电。Power Stripe：粗金属条横跨 core 分担电流；纵横交织成 Power Mesh，降等效电阻。Std-cell Rail：沿行的 M1 供电轨（follow-pin）。Special Route（sroute）：不只是连 mesh 到 rail——它生成 follow-pin rail，并把 ring/stripe/core pin/block pin/pad 连起来打 via，是 PG 成型的关键。命令：Innovus `addRing/addStripe/sroute`；ICC2 `create_pg_ring/mesh/std_cell_conn_pattern` + `compile_pg`。链条：ring→stripe→mesh→rail，sroute 收尾。

---

## Slide 14 · IR drop 与 电迁移 EM

电源网络两大可靠性问题。IR Drop：ΔV = I·R，电流过电阻产生压降，单元实际电压低于标称 → 延迟增大、时序变差，严重则功能失效；预算常为标称 VDD 的百分之几（如 3–5%，先进工艺更严），static/dynamic 分别约束。EM（电迁移）：长期大电流使金属原子迁移 → 开路/短路，影响可靠性/寿命，需保证线宽承载电流密度；PG（单向大电流）与高翻转信号/时钟线（自热 + 高活动）机理不同，分别评估。缓解：加密 mesh、加宽 stripe、加 via array、多层并联、合理 bump/pad。签核厂商：Voltus（Cadence）、RedHawk/-SC（Ansys，非 Cadence）、PrimeRail（Synopsys，IR/EM）；PrimePower 做动态功耗、非 IR 签核。一句话：IR = 瞬时电压不够（影响时序），EM = 长期电流太猛（影响寿命）。

---

## Slide 15 · 电源门控：power switch / header / footer

对可关断模块插 Power Switch 实现 Power Gating。Header（PMOS）：置真实 VDD 与虚拟电源 VVDD 之间，关断切正轨，工程更常用（漏电控制好）。Footer（NMOS）：置虚拟地 VVSS 与真实 VSS 之间，关断切接地回路，较少单独用；header + footer 同用罕见。floorplan 阶段要规划：switch 阵列布局（ring/grid/column-style）、enable 信号的菊花链走向（控冲击电流 inrush 与唤醒时间）、secondary/always-on PG 连接。唤醒冲击电流大 → enable 菊花链分时错开开启。

---

## Slide 16 · 多电压域与 UPF

不同模块用不同电压（或可关断）省功耗，每个独立电压/电源状态区域 = 电压岛/电源域。关键专用单元：Level Shifter——跨电压域信号电平转换（如 0.8V↔1.0V）；Isolation——某域关断时把输出钳位到已知值，防下游浮空（用于信号从可关断域进常开域）；Retention FF——断电时低漏电「影子锁存」保状态，上电恢复；Always-on Buffer——关断域内但接常开电源，保证 enable/retention 控制信号有效；Power Switch 见上页。顺序：常先 isolation 后 level shift（先钳位再转电平），但非绝对，取决信号方向与隔离单元供电域，ELS 合并则无先后。UPF（IEEE 1801，Synopsys）/CPF（Cadence）描述意图，floorplan 据此 `create_voltage_area`、规划独立 PG 与 always-on 网、放 switch、预留 LS/ISO。一句话：LS 管电压不同，ISO 管关断后输出乱。

---

## Slide 17 · 时序预算与模块划分

层次化设计把顶层切成 Partition/Block 分别实现，每个 block 对外端口需 Timing Budget——把顶层路径约束拆到各 block 边界，生成各自 SDC。预算合理则各块独立收敛后顶层收敛，不合理则反复迭代。pin 位置与 budget 耦合：pin 离驱动/接收逻辑越远，块内走线越长、可用 budget 越少。自动预算：ICC2 `allocate_budgets` / `estimate_timing`，Innovus `deriveTimingBudget`，或 `create_block_abstraction` + ETM。注意 block 的 SDC budget 不只 input/output delay，还含时钟不确定度、时钟延迟、驱动单元/输入转换、负载。一句话：预算 = 把总约束像切蛋糕分给各层级。

---

## Slide 18 · 拥塞 / IR 早期预估与迭代闭环

把前面串起来——早期预估与迭代闭环。拥塞早估：全局布线（GR）估每个 GCell 的需求/资源比，输出拥塞图与 Overflow。两类拥塞：全局拥塞（区域整体需求超资源，如利用率高、stripe 过密）；局部/pin-access 拥塞（引脚密集处可达性，全局充裕也会堵）。热点：macro notch、窄 channel、pin 密集、高 pin density。缓解：降利用率、加宽 channel、调 macro 朝向/位置、加 partial blockage、优化 pin。IR/EM 早估：floorplan 阶段用静态 PG 分析评估 mesh、定位高压降区加密 mesh/via；精确签核在布线后（Voltus/RedHawk-SC/PrimeRail）。闭环：floorplan → 试布局 + GR → 评估拥塞/时序/IR → 回退调 floorplan（利用率/macro/channel/PG）→ 收敛后进详细 Placement。核心态度：Floorplan 是回环，不是一遍过。

---

## Slide 19 · 输入 / 输出 与 文件作用

把 Floorplan 当黑盒看输入输出。输入：门级网表 `.v`、Tech/Cell LEF、Liberty（.lib）、SDC、UPF/CPF、划分/时序预算。输出：带宏摆放 + PG + blockage 的 DEF、Floorplan 数据库（NDM/OA）、可布线性/时序初评。关键文件：LEF = 抽象库（site/layer/布线规则/单元·macro 抽象：尺寸/pin/obstruction）；DEF = 交换格式（die/core/row/macro 位置/pin/PG 的导出导入）；Liberty = 时序/功耗库（供预算与 STA）；SDC = 约束（时钟/IO delay，预算据此拆分）；UPF/CPF = 功耗意图（电源域/switch/isolation/level shifter/retention）；NDM = ICC2/FC 新数据模型（旧 DB 为 Milkyway）。一句话：吃进设计/约束/库，吐出物理骨架。

---

## Slide 20 · 衡量指标与常见问题

实用速查。关键指标：Core Utilization 0.5–0.8（视 macro/拥塞/时序）；Aspect Ratio ≈1（约定方向以工具为准）；Congestion Overflow→0、无大面积红区；WNS/TNS ≥0（收敛）；Static/Dynamic IR 为标称 VDD 的百分之几（静/动分别约束）；EM margin 满足 foundry 电流密度规则。常见问题对治（反查前面知识点）：绕不出/拥塞 → 降利用率、加宽 channel、partial blockage、改 pin/macro 朝向；时序收不回 → 按 dataflow 重摆 macro、用 flyline、优化 pin；IR 超标 → 加密 mesh、加宽 stripe、加 via array、补 bump；EM 违例 → 加宽线、并联 via、降电流密度；Pin 拥塞 → 加 halo、调 pin 层/间距、对齐 track；唤醒冲击大 → enable 菊花链分时开。

---

## Slide 21 · EDA 命令速查（ICC2 / Innovus 对照）

命令速查，ICC2/FC 对 Innovus。初始化：`initialize_floorplan` / `floorPlan`。从 DEF 恢复：`read_def` / `defIn`。利用率·尺寸·AR：`-core_utilization` + `-side_ratio` / `floorPlan -r`。macro halo：`create_keepout_margin` / `addHaloToBlock`。布局阻挡：`create_placement_blockage` / `createPlaceBlockage`。引脚：`place_pins` 系列 / `editPin`、`assignIoPins`。电源：`create_pg_ring/mesh` + `compile_pg` / `addRing`、`addStripe`、`sroute`。电压区域：`create_voltage_area` / `createPowerDomain`。易错点：Innovus `floorPlan`、`addHaloToBlock` 与 ICC2 `-outer` 的四个 margin 值都是 **LBRT（left bottom right top）**，常被误填 LTRB，务必核对手册。另：`defIn` ≠ `floorPlan`（读入已有 DEF vs 交互创建）。命令/选项随版本而变，以官方手册为准。

---

## Slide 22 · 本章小结

八点收束。① Floorplan 是 P&R 第一步，定 die/core 几何、macro 摆放与朝向、IO/bump、电源骨架、电压域，决定 PPA。② 几何：区分总/有效利用率（0.5–0.8）、长宽比 ≈1、row/site、行翻转共享供电轨。③ Macro：沿边/沿角、按 dataflow、留 channel（或 channel-less）、pin 朝 core、选朝向对称，配 flyline/auto placer/halo/blockage、endcap/well-tap/filler。④ IO/bump 与引脚：pad ring vs bump array，块级 pin 落合法 track、注意 feedthrough。⑤ 电源：ring→stripe→mesh→rail→sroute，控 IR/EM，含 power switch/header/footer 与 always-on PG。⑥ 多电压：LS/ISO/retention/always-on/switch，UPF/CPF 落地电压区域。⑦ 时序预算拆到各 block，pin 与 budget 耦合。⑧ 早期预估 + 迭代：GR 估拥塞、静态 PG 估 IR，floorplan→trial place/GR→评估→回退，是闭环。

---

## Slide 23 · 易混淆点 / 面试高频考点

十六个高频考点，课后自测。① Utilization 过高（拥塞/IR 恶化）vs 过低（浪费/走线长），分总/有效。② Halo（跟 macro）vs Placement Blockage（固定坐标）。③ Hard/Soft/Partial：全禁/优化阶段可放 buffer/按密度上限。④ Placement vs Routing Blockage：限放单元 vs 限走线。⑤ Level Shifter（电压不同）vs Isolation（关断钳位）。⑥ Retention FF（保状态）vs Always-on Buffer（保控制信号）。⑦ Header（PMOS 门控 VDD，更常用）vs Footer（NMOS 门控 VSS）。⑧ IR Drop（瞬时电压→时序）vs EM（长期电流→可靠性）。⑨ Ring/Stripe/Mesh/Rail/sroute 区别。⑩ Flyline = 可视化连接关系指导摆 macro，非实际布线。⑪ Core Util（初始含 macro）vs Placement Density（布局后局部）。⑫ UPF（IEEE 1801/Synopsys）vs CPF（Cadence）。⑬ Aspect Ratio 偏好 1.0：方正利于布线均衡与 CTS。⑭ 为何相邻行翻转：同名供电轨落行边界、被两行共享。⑮ defIn（读 DEF）vs floorPlan（交互创建）。⑯ 签核厂商：Voltus=Cadence、RedHawk 系列=Ansys、PrimeRail=Synopsys（IR/EM）、PrimePower=Synopsys（动态功耗）。

---

## Slide 24 · 结束

速查口诀收尾：绕不出看利用率/channel，时序差看 macro/pin，IR 超标看 mesh/stripe/via。最重要一句——Floorplan 是迭代回环、不是一遍过，每个决定都在为后端整条流程「定调」。下一讲进入 Placement 与 CTS。

---

> 配套幻灯片 slides/05_Floorplan.pptx · 教案 05_Floorplan.md · 整理 J.C
