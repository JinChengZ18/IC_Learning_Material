# Floorplan 布图规划 · 口语讲稿

> 课程原版 (English source): Adam Teman, *Digital VLSI Design (DVD)*, Bar-Ilan University · Course 83-612 · <https://enicslabs.com/academic-courses/dvd-english/>
> 整理：**J.C**

---

## Slide 1 · 封面：Floorplan 布图规划

我们从 RTL 一路综合下来，得到的是一张「逻辑网表」——它只说清楚了谁连谁，却没有任何物理位置。从这一讲开始，我们正式进入物理域。Floorplan，布图规划，做的就是把这张逻辑网表映射成一副「物理布局骨架」，它是物理实现（P&R）里第一个确定版图骨架的步骤。请记住贯穿全讲的一条主线：**Floorplan 决定 PPA 上限，一步错、步步错——上游决定下游天花板。** 后面每讲一个决策，我们都会回到这条主线，看它如何往下游传导。

---

## Slide 2 · 本讲导览

在钻进细节之前，先给一张地图，这样后面每一页你都知道自己站在哪里。本讲分七块：① 定位与意义；② 几何（Die/Core/IO）、利用率、长宽比、Row/site/翻转供电轨；③ 宏摆放、halo/blockage、专用单元（endcap/well-tap/filler）；④ IO/Pad/Bump 与引脚分配；⑤ 电源（ring/stripe/mesh/rail/sroute）、IR drop/EM、电源门控；⑥ 多电压域与 UPF、时序预算；⑦ 拥塞/IR 早期预估与迭代闭环，最后加上指标、文件、命令、考点。这七块不是平铺的清单，它们共同服务于一个观念：Floorplan 是「floorplan→试布局/GR→评估→回退」的**迭代闭环**，不是一遍过。带着这个闭环往下听。

---

## Slide 3 · 什么是 Floorplan

先把它在整条流程里钉死位置，才好理解它为什么重要。Floorplan 处在综合产出门级网表之后、详细 Placement 之前；再往前是「设计导入/初始化」——读库（LEF/Liberty/NDM）、读网表、加载 SDC 与 UPF/CPF、初始化设计。这里有一个前提必须满足：物理实现前网表必须**唯一化（uniquify）**——每个子模块只被引用一次，否则无法独立优化，比如你改 `m1/u1` 会牵连到 `m2/u1`；这一步在综合或 import 时完成。Floorplan 本身有六项任务：① die/core 几何；② 宏（Macro/hard IP）的位置与朝向；③ IO/Pad/Bump 与引脚分配；④ PG 电源骨架（环/条/网）；⑤ 多电压域与电压岛边界；⑥ 各类 blockage 与 halo/keepout。这六项合起来，本质是把逻辑网表映射成物理骨架，为后续 Placement、CTS、Routing 划定边界条件。工具上区分一下：综合用 DC 或 Genus，而 Fusion Compiler 是综合加 P&R 一体的实现工具。

---

## Slide 4 · 为什么重要：一步错，步步错

知道了它做什么，接下来要回答的就是「凭什么这一步值得我们花这么大篇幅」——答案就是它决定 PPA 上限。Floorplan 决定一颗芯片 PPA（性能/功耗/面积）的上限。我们看三类典型代价，注意每一类都是往下游传导的：利用率定高，Placement 再优秀也拥塞绕不出，问题压到布线；宏摆放不合理，关键路径被迫绕远，时序怎么优化都收不回，问题压到 CTS 和 STA；PG 规划不足，要到签核（Signoff）才发现 IR drop 或 EM 超标，往往推倒重做。这背后是一条成本规律：Floorplan 阶段改几乎是免费的，越往后——布线后、签核阶段——改的成本急剧上升。「七分布局、三分布线」是经验俗语、不是量化指标，它的价值只在于提醒你早期版图决策的份量有多重。

---

## Slide 5 · 芯片几何：Die / IO / Core / Rows

明白了份量，我们就从最外层的几何边界开始一层层往里定。芯片由外到内层层嵌套。最外是 Die Area（晶粒区），是整颗芯片的最外边界，含 scribe 切割道，包含一切。往里是 IO 区/Pad Ring，是 Die 与 Core 之间的环形区，放 IO 单元与 Pad。再往里是 Core Area（核心区），放标准单元与宏。Core 边界到 Pad 内沿的距离叫 Core-to-IO Spacing，这段距离要留给电源环与 IO 走线。Core 内部再被切成等高的标准单元行 Rows。整个嵌套关系是 Die ⊃ Pad Ring ⊃ Core ⊃ (Macro + Rows)。这里有一个决定芯片面积「贵不贵」的判据：Core-limited 还是 Pad-limited——芯片尺寸是由 core 面积决定（核受限），还是由 IO/Pad 环周长决定（焊盘受限）。要警惕的是，IO 不随摩尔定律缩小，一旦 pad 受限，面积就很「贵」。

---

## Slide 6 · 标准单元行 / site / 翻转共享供电轨

Core 被切成行，那这些行的高度和栅格由什么决定、行与行之间又靠什么省面积？这一页讲清这个机关。Row：Core 切成等高水平行，行高等于库单元高度（9T/7T），约等于 track 数 × M2 pitch，所以 9T 行高大于 7T。Site：行内最小放置栅格，定义于 LEF，单元宽度必须是 site 宽度的整数倍。真正的核心机关是翻转共享供电轨：相邻行做镜像翻转（FS，绕水平中线），同名电源轨就落在行边界上、被上下两行共享，于是供电轨条数减半、面积更省，而且 follow-pin rail 保持连续。LEF 里 `SYMMETRY Y` 描述的是单元自身的镜像方式；行间共享靠的是相邻行上下镜像，具体轴向以工具/库文档为准。这个「同名轨落行边界、被两行共享」的细节，是行翻转省面积的全部原因。

---

## Slide 7 · 利用率与长宽比

行和站位定好了，下一个要拍板的数字是 Core 该塞多满、长成什么形状——这两个数字直接定下了后面拥塞和时钟树的难度。利用率有两个口径，务必分清。总利用率 Total Util =（Σ标准单元面积 + Σ宏面积）/ Core 面积；有效利用率 Effective Util = Σ标准单元面积 /（Core − blockage − macro halo − keepout − …），工具报告里的 "utilization" 多指后者，因为它更贴近实际可放置密度。经验初值 0.5–0.8，并非固定的 60–75%：宏占比高、IP 密集、datapath 可以超 0.8，拥塞高或活动率高就要留余量，降到 0.5–0.6。一个易混点：目标利用率不等于 placement 后的局部实际密度（placement density）。长宽比 Aspect Ratio 是 core 的高/宽——各工具约定可能相反，以文档为准；比值越接近 1（方正）越利于布线均衡与时钟树平衡，长条形长边易拥塞、skew 难控。对应参数是 ICC2 `initialize_floorplan -side_ratio {1 1}`、Innovus `floorPlan -r 1.0`。利用率「过高拥塞、过低浪费」，是常考的权衡。

---

## Slide 8 · 宏单元摆放原则

利用率和形状定下了 Core 的「容器」，接下来要往里放最大、最不好挪的东西——宏，因为它一旦放偏，前面定的利用率和后面的时序全得跟着遭殃。宏（Macro）= SRAM/ROM/PLL/ADC/IP 核等硬核，尺寸大、形状固定、引脚固定，是 floorplan 的核心难点。摆放五条原则：① 沿边/沿角，大宏靠 core 边界或角落，中间连续区留给标准单元，避免在中央「挖洞」；② 按数据流就近（dataflow-driven），用 flyline 飞线指导，现代工具有 auto macro placer，按 connection weight 自动布大块 IP；③ 预留 channel 走 PG/时钟/信号，也有 channel-less 紧贴（abutted）风格，省面积但对 pin access 要求高；④ 引脚朝 core，避免信号绕过整个 macro 本体；⑤ 朝向与对称——R0/R90/R180/R270 加镜像 MX/MY 共 8 种朝向，常把两块对称宏引脚相对、背靠背摆放，共享 channel、对齐成规整阵列。摆好之后标记 FIXED；功耗大的宏（wire-bond）要远离芯片中心、靠近边界电源 pad 以降 IR drop，且彼此拉开以避 EM。一句话兜底：摆放不当就等于给布线设障碍、拉长走线，最终一定回到拥塞与时序问题上，而且摆放手法常常优于自动。

---

## Slide 9 · halo / keepout 与各类 blockage

宏摆好了，但紧挨着它的那圈空间不能随便放标准单元——这就引出 halo 和各类 blockage，它们是你「保护」摆放成果、给工具划禁区的手段。先区分 halo 与 blockage，这是高频考点。Halo/Keepout Margin 是 macro 四周「不放标准单元」的边带，留给 pin access、电源、缓冲，关键特征是**跟随 macro 移动**。Placement Blockage 则是钉在**固定坐标**的禁放区，细分三种：hard 完全禁放任何标准单元；soft 在粗放（coarse）阶段禁放，但优化/合法化阶段可以放 buffer/inverter；partial 按密度上限限制，比如该区最多 40%，它和 density screen 概念相近，但实现和命名因工具而异、并不等价。Routing Blockage 是禁某些层布线，可指定层范围（如 M1–M3），也分 hard/partial。另外还有一类容易和 blockage 混的——Placement Region（聚类约束）：soft guide 尽量聚拢、guide 尽量放指定区、region 必须放该区但他人也可、fence 必须放该区且排他，它们是用来「帮」工具把某类逻辑放一起的。经验上，macro 引脚一侧加 halo，给 pin access 留空间，避免 pin 拥塞绕不出。记一句：halo 跟着 macro 走，blockage 钉在坐标上。

---

## Slide 10 · 物理专用单元：endcap / well-tap / filler

划完禁区，还有一类不参与逻辑、却必须在这个阶段就安排的单元，否则后面会撞 DRC 甚至 latch-up。这三种 physical-only cell 不参与逻辑功能，但和 row/site、供电轨连续、N-well 连续强相关，所以要在 floorplan 或早期 placement 阶段规划。Endcap/Boundary Cell 放在每行两端及 macro/void 边界，保证行边界处 well/implant 连续与 DRC 合规。Well-tap/Tap Cell 周期性插入，提供 well 偏置接触，它的间距必须满足工艺的 max well-tap distance（DRC），否则就有 latch-up（闩锁）风险与 DRC 报错——所以 tap 间距要在 floorplan 早期就按规则规划好。Filler Cell 在布线前/流程末期插入，填行内空隙、保证供电轨与 well 连续，引入时机晚于 tap 和 endcap。两个考点收一下：tap 间距违规会 latch-up，filler 最后才放。

---

## Slide 11 · IO / Pad、Bump 与引脚分配（上）

Core 内部的骨架基本成型，现在把视线移到芯片边界——信号怎么引出芯片，这决定了 Pad/Bump 怎么排，也直接影响后面的引脚分配。两种封装思路。Wire-bond（引线键合）：IO Pad 沿 die 四周排成 Pad Ring，金线键合，要考虑信号/电源 Pad 交替、ESD、Corner Pad。Flip-Chip（倒装焊）：信号经 die 表面的凸点（Bump）面阵列（area array）从正面引出，常配 RDL 重布线层——但是否需要完整 RDL 取决于封装和凸点布局，部分 flip-chip 或 WLCSP 直接落顶层金属或 UBM，不一定需要。bump 摆放要对齐封装的 bump map，控制 bump 间距与电源/信号比例。一句话：wire-bond 走四周 pad ring，flip-chip 走面阵列 bump。

---

## Slide 12 · 引脚分配 Pin Assignment（下）

引脚从芯片引出只是顶层，层次化设计里真正影响块间时序的是块级 pin——它直接决定块间走线长度，所以要单独讲。引脚分配分两级。顶层（Top-level）：IO buffer 的位置决定芯片对外引脚的位置。块级/分区（hierarchical）：partition 对外端口需要分配到块边界的具体位置，pin 位置直接决定块间走线长度与时序。块级 pin 的核心约束有四条：① 落在合法 routing track 上，并与该层布线方向一致；② 沿数据流方向分布，相连逻辑在左则 pin 放左边界，避免长绕线；③ 注意 feedthrough 穿通——信号穿过无关 block 需要预留穿通端口或缓冲，否则被迫绕过整个 block；④ 工具支持 pin 自动优化，但关键总线常常需要手工约束，比如 `set_block_pin_constraints` 配 `place_pins`。最后埋一个伏笔：pin 离逻辑越远，块内走线越长、budget 越紧——这正好和下一页的时序预算耦合在一起。

---

## Slide 13 · 电源规划：Ring → Stripe → Mesh → Rails

几何和摆放定完，芯片还只是一副「不通电」的骨架；接下来要把电送到每一个单元，这就是电源规划，而它规划得好不好，直接决定后面 IR drop 和 EM 的签核结果。PG 网络自上而下、由粗到细。Power Ring：沿 core/macro 边界的闭合环，用顶层粗金属做主干供电。Power Stripe：粗金属条横跨 core 分担电流。Power Mesh：stripe 纵横交织成网，降低等效电阻。Std-cell Rail：沿标准单元行的 M1 供电轨，也就是 follow-pin。Special Route（sroute）：它不只是「连 mesh 到 rail」——它生成 follow-pin rail，并把 ring、stripe、core pin、block pin、pad 连起来并打 via，是整个 PG 网络成型的关键步骤。命令上，Innovus 用 `addRing/addStripe/sroute`，ICC2 用 `create_pg_ring/mesh/std_cell_conn_pattern` 加 `compile_pg`。整条链记成：ring→stripe→mesh→rail，sroute 收尾。

---

## Slide 14 · IR drop 与 电迁移 EM

电源网络搭好了，怎么判断它够不够？衡量它的就是两大可靠性问题，也正是上一页 PG 规划不足时会在签核暴雷的地方。IR Drop：ΔV = I·R，电流流过电阻产生压降，单元实际电压低于标称，于是延迟增大、时序变差，严重时功能失效；预算随工艺和电压而异，常为标称 VDD 的百分之几，比如 3–5%，先进工艺更严，而且 static 和 dynamic 分别约束。EM（电迁移）：长期大电流使金属原子迁移，导致开路或短路，影响可靠性与寿命，需要保证线宽能承载电流密度；注意 PG 网络（单向大电流）和高翻转的信号线/时钟线（自热加高活动）都有 EM，但机理与约束不同，要分别评估。缓解手段：加密 mesh、加宽 stripe、增加 via array、多层并联、合理布 bump/pad。签核工具记准厂商：Voltus（Cadence）、RedHawk 与 RedHawk-SC（Ansys，不是 Cadence）、PrimeRail（Synopsys，做 IR/EM）；PrimePower 做的是动态功耗/活动率，不是 IR 签核。一句话区分：IR 是瞬时电压不够、影响时序，EM 是长期电流太猛、影响寿命。

---

## Slide 15 · 电源门控：power switch / header / footer

控住了 IR 和 EM，下一个功耗维度是漏电——对不工作的模块直接断电，这就是电源门控，而它的开关阵列同样要在 floorplan 阶段就排进去。对可关断模块插 Power Switch 实现 Power Gating（功率门控）。Header（头开关）是 PMOS，置于真实 VDD 与模块虚拟电源 VVDD 之间，关断时切断正轨，工程上更常用，因为漏电控制好。Footer（脚开关）是 NMOS，置于模块虚拟地 VVSS 与真实 VSS 之间，关断时切断接地回路，较少单独使用；header 加 footer 同时用就更罕见。floorplan 阶段要规划三件事：switch 的阵列布局（ring-style 或 grid/column-style）、enable 信号菊花链（daisy-chain）的走向（用来控制冲击电流 inrush 与唤醒时间），以及 secondary/always-on PG 的连接。一个要点：唤醒时冲击电流很大，所以 enable 菊花链要分时错开开启。

---

## Slide 16 · 多电压域与 UPF

电源门控是「整块断电」，再进一步，不同模块本身就跑在不同电压上——这就是多电压域，它需要一整套专用单元来处理跨域的电平和断电问题，并且全程由 UPF/CPF 来描述意图。不同模块工作在不同电压，或者干脆可关断，以此省功耗，每个独立的电压/电源状态区域就是一个电压岛/电源域。关键专用单元有五类：Level Shifter 负责跨电压域信号的电平转换，比如 0.8V 和 1.0V 之间；Isolation Cell 在某域关断时把它的输出钳位到已知值 0 或 1，防止下游浮空，用于信号从可关断域进入常开域；Retention FF 在域断电时用低漏电的「影子锁存」保住状态，上电后恢复；Always-on Buffer 身在关断域内却接常开电源，保证 enable/retention 这类控制信号始终有效；Power Switch 就是上一页讲的门控。一个顺序问题：通常先 isolation 后 level shift（先钳位再转电平），但这不绝对，取决于信号方向与隔离单元的供电域，如果用 ELS 把两者合并就没有先后。整套意图由 UPF（IEEE 1801，Synopsys 主推）或 CPF（Cadence 主推）描述，floorplan 据此 `create_voltage_area`、规划独立 PG 与 secondary/always-on 网、放 switch、预留 LS 和 ISO 的位置。记住区别：LS 管「电压不同」，ISO 管「关断后输出乱」。

---

## Slide 17 · 时序预算与模块划分

电压域把芯片切成了若干电源域，而层次化设计还要按时序把顶层切成块来分别实现——这就回到了 Slide 12 埋的伏笔：每个块要拿到自己的时序预算才能独立收敛。层次化设计中顶层切成 Partition/Block 分别实现，每个 block 对外端口都需要一份 Timing Budget——把顶层路径约束拆到各 block 边界，生成每个 block 各自的 SDC。预算合理，各 block 独立收敛后顶层就能收敛；不合理，就得反复迭代。这里 pin 位置与 budget 强耦合：pin 离驱动或接收逻辑越远，块内走线越长、可用 budget 越少。自动预算工具：ICC2 用 `allocate_budgets` / `estimate_timing`，Innovus 用 `deriveTimingBudget`，或者用 `create_block_abstraction` 加 ETM（Extracted Timing Model）。还有 ILM（Interface Logic Model），只保留接口逻辑、抽掉块内部，用来简化并加速顶层时序收敛，是层次化设计常用的手段。注意 block 的 SDC budget 不只是 input/output delay，还包含时钟不确定度、时钟延迟、驱动单元/输入转换、负载。一句话：预算就是把一条总约束像切蛋糕一样分给各层级。

---

## Slide 18 · 拥塞 / IR 早期预估与迭代闭环

前面每一项决策——利用率、macro、channel、PG——我们都说「会影响下游」，那到底怎么在 floorplan 阶段就提前看到下游的反馈、再回头调整？这就是把全讲收拢成闭环的一页。先说拥塞早期预估：用全局布线（GR）估每个 GCell 的布线需求/资源比，输出拥塞图加 Overflow。拥塞分两类：全局拥塞是区域整体需求超资源，比如利用率高、stripe 过密占了布线资源；局部/pin-access 拥塞是引脚密集处的可达性问题，哪怕全局资源充裕也可能堵。热点成因有 macro notch（凹角）、macro 间窄 channel、pin 密集区、高 pin density 单元。缓解就是降利用率、加宽 channel、调 macro 朝向/位置、加 partial blockage、优化 pin。再说 IR/EM 早期预估：floorplan 阶段用静态 PG 分析评估 mesh 是否足够，定位高压降区加密 mesh/via，精确签核留到布线后用 Voltus/RedHawk-SC/PrimeRail。把这些串起来就是迭代闭环：floorplan → 试布局加 GR → 评估拥塞/时序/IR → 回退去调 floorplan（利用率/macro/channel/PG）→ 收敛后才进详细 Placement。核心态度就一句：Floorplan 是回环，不是一遍过。

---

## Slide 19 · 输入 / 输出 与 文件作用

理解了闭环的运转，再把 Floorplan 当成一个黑盒，看清楚它到底吃进什么、吐出什么，这样你对接上下游工具时就不会错。输入是门级网表 `.v`、Tech/Cell LEF、Timing Liberty（.lib）、SDC、UPF/CPF、划分与时序预算。输出是带宏摆放、PG、blockage 的 DEF，Floorplan 数据库（NDM/OA），以及可布线性/时序的初步评估。关键文件各自的角色：LEF 是抽象库，提供 site、layer、布线规则、单元和 macro 的抽象（尺寸/pin/obstruction）；DEF 是交换格式，负责 die/core、row、macro 位置、pin、PG 的导出导入；Liberty 是时序/功耗库，供时序预算与 STA 用；SDC 是约束，给时钟和 IO delay，时序预算据此拆分；UPF/CPF 是功耗意图，描述电源域、switch、isolation、level shifter、retention；NDM 是 ICC2/FC 的新数据模型，旧的 DB 是 Milkyway。一句话：吃进设计、约束、库，吐出物理骨架。

---

## Slide 20 · 衡量指标与常见问题

黑盒的输入输出清楚了，那拿到输出后怎么判断这版 floorplan 行不行、不行又该回去调哪一项？这一页就是闭环里「评估」和「回退」两步的速查表。先看关键指标：Core Utilization 0.5–0.8（视 macro/拥塞/时序）；Aspect Ratio ≈1（约定方向以工具为准）；Congestion Overflow 趋近 0、没有大面积红区；WNS/TNS ≥0 才算收敛；Static/Dynamic IR 为标称 VDD 的百分之几（静、动分别约束）；EM margin 满足 foundry 电流密度规则。再看常见问题怎么对治，每一条都能反查到前面某页的知识点：绕不出/拥塞，就降利用率、加宽 channel、加 partial blockage、改 pin/macro 朝向；时序收不回，就按 dataflow 重摆 macro、用 flyline、优化 pin；IR 超标，就加密 mesh、加宽 stripe、加 via array、补 bump；EM 违例，就加宽线、并联 via、降电流密度；Pin 拥塞，就加 halo、调 pin 层/间距、对齐 track；switch 唤醒冲击大，就让 enable 菊花链分时开启。

---

## Slide 21 · EDA 命令速查（ICC2 / Innovus 对照）

知识点和对治方法都过完了，落到实操就是命令，这里把两大主流工具对照起来，方便你照着敲。初始化 floorplan：ICC2 `initialize_floorplan`，Innovus `floorPlan`。从 DEF 恢复：`read_def` / `defIn`。利用率·尺寸·AR：`-core_utilization` 加 `-side_ratio` / `floorPlan -r`。macro halo：`create_keepout_margin` / `addHaloToBlock`。布局阻挡：`create_placement_blockage` / `createPlaceBlockage`。引脚：`place_pins` 系列 / `editPin`、`assignIoPins`。电源：`create_pg_ring/mesh` 加 `compile_pg` / `addRing`、`addStripe`、`sroute`。电压区域：`create_voltage_area` / `createPowerDomain`。这里有个最容易栽的坑：Innovus `floorPlan` 的 margin 四值、`addHaloToBlock`、以及 ICC2 的 `-outer`，顺序都是 **LBRT（left bottom right top）**，初学者常误填成 LTRB，务必核对手册。另外 `defIn` 不等于 `floorPlan`——前者是读入已有 DEF（从 DEF 恢复），后者是交互式创建，语义不同。命令和选项随版本而变，最终以官方手册为准。

---

## Slide 22 · 本章小结

讲到这里，整条主线已经走完一遍，我们用八点把它收束，每一点都对应前面某一块。① Floorplan 是 P&R 第一个确定版图骨架的步骤，定 die/core 几何、macro 摆放与朝向、IO/bump、电源骨架、电压域，**决定 PPA 上限**。② 几何：区分总利用率与有效利用率（0.5–0.8）、长宽比 ≈1、row 与 site、行翻转共享供电轨。③ Macro：沿边/沿角、按 dataflow、留 channel 或 channel-less、pin 朝 core、选朝向与对称，配 flyline、auto placer、halo、blockage（hard/soft/partial）、endcap/well-tap/filler。④ IO/bump 与引脚分配：pad ring 对 bump array，块级 pin 须落合法 track、注意 feedthrough。⑤ 电源：ring→stripe→mesh→rail→sroute，控 IR drop（百分之几、静/动）与 EM（PG 与信号分别评估），含 power switch/header/footer 与 secondary/always-on PG。⑥ 多电压域：level shifter / isolation / retention FF / always-on buffer / power switch，由 UPF/CPF 描述并落地为电压区域。⑦ 时序预算：层次化把顶层约束拆到各 block，预算含 IO delay、时钟不确定度、驱动/负载，pin 位置与 budget 强耦合。⑧ 早期预估与迭代：GR 估拥塞（全局/局部）、静态 PG 估 IR，floorplan→trial place/GR→评估→回退，是迭代闭环。

---

## Slide 23 · 易混淆点 · 课后自测

下面这十六个点是最容易混的地方，留作课后自测，每一题都能反查到前面对应的页。① Utilization 过高（拥塞/IR 恶化）对过低（面积浪费、走线变长），并区分总/有效。② Halo（跟 macro 走）对 Placement Blockage（钉固定坐标）。③ Hard/Soft/Partial Blockage：全禁 / 优化阶段可放 buffer / 按密度上限。④ Placement Blockage 对 Routing Blockage：限制放单元对限制走线。⑤ Level Shifter（电压不同）对 Isolation（关断钳位）。⑥ Retention FF（保状态）对 Always-on Buffer（保控制信号）。⑦ Header（PMOS 门控 VDD，更常用）对 Footer（NMOS 门控 VSS）。⑧ IR Drop（瞬时电压→时序）对 EM（长期电流→可靠性）。⑨ Ring/Stripe/Mesh/Rail/sroute 各自的角色。⑩ Flyline 是可视化连接关系（可带 weight）指导摆 macro，不是实际布线。⑪ Core Utilization（floorplan 初始、含 macro）对 Placement Density（placement 后局部实际）。⑫ UPF（IEEE 1801/Synopsys）对 CPF（Cadence）。⑬ Aspect Ratio 为何偏好 1.0：方正利于布线均衡与 CTS，长条易拥塞、skew 难控。⑭ 为何相邻行翻转：让同名供电轨落行边界、被两行共享，条数减半、保 follow-pin rail 连续。⑮ defIn（读入已有 DEF）对 floorPlan（交互创建）。⑯ 签核厂商：Voltus=Cadence、RedHawk 系列=Ansys、PrimeRail=Synopsys（IR/EM）、PrimePower=Synopsys（动态功耗）。

---

## Slide 24 · 结束

最后用一组速查口诀把整讲钉进记忆，这也是你日后遇到问题时回查的第一反应：绕不出，看利用率和 channel；时序差，看 macro 和 pin；IR 超标，看 mesh、stripe、via。而最重要的一句仍然是我们开篇立下的主线——Floorplan 是迭代回环，不是一遍过，它的每一个决定都在为后端整条流程「定调」。下一讲，我们顺着这副骨架进入 Placement 与 CTS。

---

> 配套幻灯片 slides/05_Floorplan.pptx · 教案 05_Floorplan.md · 整理 J.C
