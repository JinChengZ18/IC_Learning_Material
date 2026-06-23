# Floorplan 布图规划 · 口语讲稿

> 课程原版 (English source): Adam Teman, *Digital VLSI Design (DVD)*, Bar-Ilan University · Course 83-612 · Lecture 6 floorplan 部分约对应 PDF p.13-p.44 · <https://enicslabs.com/academic-courses/dvd-english/>
> 整理：**J.C**
>
> **用法**：逐页讲稿，可照念；`[]` 内为讲者指图提示，不念出来。本稿按 Lecture 6 的 floorplan 主线重构：goals/objectives -> fullchip overview -> inputs/outputs -> IO/chip size/utilization -> uniquify -> macro/regions/blockages -> hierarchy -> power planning -> Innovus flow。

---

## Slide 1 · 封面：Floorplan 布图规划

我们从 RTL 和综合一路走到门级网表，手里现在有的是一张 logical description：它知道有哪些实例、哪些连线，但还不知道任何东西放在芯片的哪个位置。从这一讲开始，我们进入 physical domain。Floorplan 做的事，就是把逻辑描述映射成物理描述，让芯片第一次有 die、core、IO、macro、power grid 这些具体骨架。

这一步不是简单“画个框”。它会决定后面 placement、CTS、routing 能不能顺利收敛，也会决定面积、延迟、拥塞和供电可靠性的上限。所以这讲的主线是：floorplan 是逻辑到物理的第一层承诺，承诺错了，后面每一步都会替它付成本。

---

## Slide 2 · 本讲导览

这一讲按原课件的顺序走。先讲 floorplanning 的 goals and objectives，再从 fullchip overview 看 floorplan 要决定哪些对象。接着讲输入输出、IO ring、chip size 和 utilization，这些决定芯片边界和标准单元区域。

然后进入实现细节：netlist uniquify 是进入物理域前的前提；hard macro placement、placement regions、blockages、halos 和 routing blockage 决定工具有多少空间可用。再往后是 hierarchical design，重点是 timing budgeting、pin assignment 和 feedthrough。最后一大块是 power planning，从 IR drop、EM 到 power grid creation，最后用 Innovus flow 把步骤串起来。

---

## Slide 3 · Floorplanning 的目标

[指 floorplan 在流程中的位置] Floorplanning 是 logical description 和 physical description 之间的 mapping。逻辑描述是 netlist，物理描述就是 floorplan。这个 mapping 要回答几个最早、也最关键的问题：block 放在哪里，IO pads 放在哪里，power pads 的位置和数量是多少，power distribution 用什么结构，clock distribution 大致如何组织。

它的 objectives 也很清楚：minimize chip area、minimize delay、minimize routing congestion。注意这三个目标天然有冲突：面积压得太紧会拥塞，通道留得太宽会浪费面积，power grid 加得太强又会吃掉信号布线资源。floorplan 的难点就在于一开始就要在这些冲突里做取舍。

---

## Slide 4 · Fullchip Design Overview

[指 fullchip overview 图] 从整颗芯片看，floorplan 要同时处理 chip size、number of gates、metal layers、interface to the outside、hard IPs/macros、power delivery、multiple voltages、clocking scheme，以及 flat or hierarchical 这些选择。图里的 core placement area、periphery IO area、P/G pads、P/G grid、RAM、ROM、IP 都是 floorplan 的对象。

所以 floorplan 不是单独决定一个矩形尺寸，而是把整颗芯片的空间组织起来。IO 区在外圈，core 在内部，macro 会切割标准单元区域，power grid 又要从 pad 把电送到每个单元。每一个对象都在抢空间，floorplan 的任务就是让这些对象抢得有秩序。

---

## Slide 5 · Floorplan 的输入与输出

把 floorplan 当成一个阶段来看，它的输入包括 design netlist、area requirements、power requirements、timing constraints、physical partitioning information，以及 die size、performance、schedule 之间的 trade-off。可选但很有帮助的输入包括 IO placement 和 macro placement information。

它的输出也必须具体：die 或 block area 已经确定，I/O 已经摆放，macros 已经摆放，power grid 已经设计，power pre-routing 已经完成到足够支撑后续流程，standard cell placement areas 已经定义好。换句话说，一个合格的 floorplan 输出，应该让设计 ready for standard cell placement。

---

## Slide 6 · IO Ring 与 Chip Size

IO pinout 往往由前端设计者决定，但一定要听 physical design 和 packaging engineers 的反馈。原因是 I/O 不像核心逻辑那样随 Moore's Law 快速缩小，IO cell 和 pad 在面积上很贵。更重要的是，I/O 不只是接信号到外部，也要给芯片供电，所以 power pads 和 ground pads 的规划也属于 IO ring 的一部分。

[指 core limited / pad limited 图] 选 chip size 时，要先判断设计是 core limited 还是 pad limited。Core limited 是核心逻辑、macro、布线资源决定芯片大小；pad limited 是 IO 数量、pad pitch 或封装要求决定 die 不能再小。两者的优化方向不同：core limited 要看 utilization 和 routing resource，pad limited 则要看 IO ring 和封装约束。

---

## Slide 7 · Utilization 与 Trial Route

Utilization 在原课件里指 standard cells 占 core area 的比例。常见起点可能是 70%，但这只是起点，不是定律。不同设计差异很大：pin 很密、macro 很多、布线层紧张、时序很难的设计，都可能需要更低的 utilization。

高 utilization 会让 routing congestion 上升，也会让 optimization 和 legalization 阶段很难操作。更麻烦的是 local congestion：比如 multiplexer 这类 pin-dense cells，即使全局 utilization 看起来合理，局部 pin access 仍然可能堵住。所以不能只凭 utilization 决定 die size。正确动作是跑 quick trial route 或 global routing 估计，检查 congestion，再回头调整 synthesis、core size 或 routing resources。

---

## Slide 8 · Uniquifying the Netlist

进入 physical domain 前，netlist 必须 uniquify。Unique netlist 的意思是每个 sub-module 只被引用一次。为什么这件事和 floorplan 有关？因为物理优化要按实例独立移动、缓冲、优化；如果两个实例共享同一个 module definition，工具想优化 `m1/u1` 时，就可能同时改变 `m2/u1`。

[指 non-unique / unique 图] 原课件里的例子很直观：两个 `amod` 实例里都有 `BUFFD1 u1`。如果不唯一化，物理优化无法只改其中一个实例。综合后的网表必须在 placement 之前 uniquify，可以由 synthesizer 完成，也可以在 design import 时完成。

---

## Slide 9 · Hard Macro Placement

Hard macro 包括 SRAM、ROM、PLL、模拟 IP、第三方硬核等。它们面积大、形状固定、pin 固定，对 routing、timing、power 都有强影响，所以通常先摆 macro，再让 placer 处理标准单元。

原课件给的主原则是：通常把大 macro 推到 floorplan 的边缘或角落，让标准单元区域保持一个尽量完整的大矩形。placement algorithms 一般更喜欢 single large rectangular placement area；如果 macro 把 core 切成很多碎片，后面 routing congestion 和 timing 都会更难。对于 wire-bond 设计，高功耗 macro 还要尽量远离芯片中心、靠近边缘 power pads，降低 IR drop。macro 摆好后，记得 mark as FIXED。

---

## Slide 10 · Placement Regions：帮助工具表达意图

有时我们希望“帮”工具一把，让某些逻辑靠近某个区域，或者让一组 cells 聚在一起。P&R tools 里通常有几类 placement regions。

Soft guide 是尽量把这些 cells 聚在一起，但不定义一个硬区域。Guide 是尽量放到指定区域。Region 是这些 cells 必须放在指定区域内，但其他 cells 也可以进来。Fence 最硬：指定 cells 必须在这个区域内，而且其他 cells 不能进来。约束越硬，工具自由度越低；用 region/fence 之前，要确认它表达的是必要的设计意图，而不是人为制造拥塞。

---

## Slide 11 · Placement Blockages 与 Halos

Placement blockage 是告诉 placer 某些区域不要放标准单元。Hard blockage 是完全不能放 cells；soft blockage 是 placement 阶段不能用，但 optimization 阶段可以用来放 buffer；partial blockage 是降低区域利用率，让工具少放一点。

Halo，也叫 padding 或 keepout margin，是 macro 外围保留的一圈空白区域，目的是改善 pin accessibility，给信号、电源和 buffer 留空间。一个很实用的区分：halo 跟着 macro 移动；普通 placement blockage 更多是固定坐标区域。原课件还给了一个典型做法：macro 四周常有 hard blockage，而 macro 之间或 macro 与 core boundary 之间的 channel 可以用 soft blockage 保留弹性。

---

## Slide 12 · Routing Blockage 与 Good Floorplan Guidelines

Routing blockage 限制的是走线，不是放 cell。它可以针对某个坐标区域、某些 routing layers 生效。比如保护 macro 上方的特殊区域、保留电源资源、或者禁止低层金属被信号线占掉。讲到这里要把两类 blockage 分清楚：placement blockage 管“能不能放单元”，routing blockage 管“能不能走线”。

[指 good floorplan guidelines 图] 好的 floorplan 有几个图上就能看出来的特征：保持 single large core area；RAM 这类大块尽量放在角落或边缘；保留 large routing channels；避免 constrictive channels；不要让很多 pins 对着狭窄通道；必要时旋转 macro 改善 pin accessibility；pins 尽量不要挤在 corners；用 blockage 改善 pin access。总结一句：让后面的线有路可走。

---

## Slide 13 · Flat vs. Hierarchical Design

如果设计太大，flat flow 一次跑完整颗芯片会遇到 runtime 和 memory 的限制，这时就要把芯片 partition 成多个 hierarchies 或 blocks，每个 block 独立跑 P&R flow，最后在 fullchip 级别做 timing 和 verification。

层次化的优点很明显：EDA runtime 更短，内存更少，ECO turn-around time 更快，也更利于 design reuse。代价也很明显：fullchip timing closure 更难，design planning 更重。你必须提前处理 feedthrough generation、repeater insertion、timing constraint budgeting 等问题。层次化不是让问题消失，而是把“大问题”换成“边界规划问题”。

---

## Slide 14 · Timing Budgeting 与 ILM

[指 set_input_delay 和 block boundary 图] Chip level constraints 必须正确映射成 block level constraints。例如顶层某个输入端口有 1.5 ns input delay，切到 block 实现时，就要变成 block 边界上的 I/O constraint。Timing budgeting 的本质，就是把一条跨层级路径的时间分配给各个 block。

预算合理，各 block 独立收敛后，fullchip 更容易收敛；预算不合理，单个 block 看起来都过了，顶层组合起来还是失败。Interface Logic Model，ILM，是层次化设计里常用的简化模型：它保留接口时序相关逻辑，隐藏 block 内部大量细节，让 fullchip timing 和 verification 更快。

---

## Slide 15 · Hierarchical Pin Assignment 与 Feedthrough

Block pin assignment 会直接影响块间走线和时序。pin constraints 包括 layers、spacing、size、overlap、net groups、pin guides 等。pin 可以按 placement-based flightlines 分配，也可以按 route-based trial route 和 boundary crossings 分配。Pin guide 可以引导某些 net groups 自动落到指定边界区域。

[指 feedthrough 图] 在 channel-less 设计或 channel 资源很紧的设计里，feedthrough 很关键。假设信号从 Partition A 到 Partition C，中间隔着 Partition B，如果 B 没有 feedthrough，信号可能被迫绕过整个 block。解决办法是在 B 上生成 feedthrough pin 或 feedthrough net，把原本跨越 B 的连接拆成几段。pin 不要挤在 partition corners，因为角落会让 routing difficult，也容易破坏 timing budget。

---

## Slide 16 · Power Planning：功耗与可靠性

Power planning 要解决的不只是“连上 VDD/GND”。它同时关系到 dynamic power、static leakage power、IR-drop、voltage droop、electromigration 这些问题。课件里把它分成两类：power problem 可能来自平均或瞬时功耗；power density problem 长期会变成 EM 可靠性问题。

在 floorplan 阶段，电源问题由两件事共同决定：floorplan 本身，以及 power grid 的设计。macro 放在哪里、power pads 有多少、grid 用几层金属、straps 多宽多密，都会影响 IR 和 EM。也就是说，power planning 不是 routing 之后的签核补救，而是 floorplan 阶段就要开始的结构设计。

---

## Slide 17 · IR Drop：电源线上掉电压

IR drop 是 supply voltage 沿供电线传播时，因为电流和电阻产生的电压下降。公式很简单：drop = I * R。但芯片上的 power grid 是一个很大的网络，所以工具会建立 power grid 的 resistance matrix，结合每个 gate 的 average current，求出每个节点上的 voltage。

如果 actual voltage level 掉到 tolerance level 以下，单元延迟会变大，timing 可能失败，严重时功能也可能出错。讲 IR drop 时要把它和时序连起来：它不是只属于电源网络的孤立问题，而是会通过单元延迟影响 timing closure。

---

## Slide 18 · Electromigration：长期电流带来的失效

Electromigration，电迁移，是电流流过导体时，电子动量逐渐推动金属原子迁移。结果可能是 open，也就是一根线上形成 void；也可能是 short，也就是两根线之间 bridging。

即使没有立刻 open 或 short，EM 也会改变 wire RC，造成性能退化。IR 更偏“电压够不够”，EM 更偏“金属长期能不能扛住”。所以电源网要同时满足短期电压稳定和长期可靠性；只看 IR 或只看 EM 都不够。

---

## Slide 19 · Power Distribution 的基本取舍

Power Distribution Network 的功能包括：把电流从 pads 送到 chip 上的 transistors，保持稳定低噪声电压，提供 average 和 peak power demands，为 signals 提供 return paths，并避免 electromigration 和 self-heating wearout。

更宽、更多的 power lines 可以减少 static IR drop、dynamic dI/dt drop 和 EM 风险；但代价是减少 signal routing resources，提高 congestion。原课件用一根 1 mm 长、100 nm 宽的 M1 rail 做估算，电阻能到约 1000 ohm，0.1 mA 电流就可能带来约 100 mV drop。结论很直接：power rails 要尽量宽、尽量厚、尽量有多路径，但不能把信号布线资源全部吃光。

---

## Slide 20 · P/G Routing 与标准 Power Routing 方式

每个 standard cell 和 macro 都有 power 和 ground signals，比如 VDD 和 GND。它们也要被连接，而且是非常巨大的网络。P/G mesh 提供从 power/ground sources 到 destinations 的多条路径，降低 series resistance。通常结构是 hierarchical 的：上层厚金属做主干 mesh 或 straps，下层连接到 standard cell follow pins，中间用 multiple vias 和 via stacks 连起来。

标准做法是 power grid：vertical 和 horizontal power bars 互连，高性能设计里很常见，甚至 upper thicker layers 上超过一半金属资源都会给 VDD/GND。Dedicated VDD/GND planes 分析简单但非常昂贵，很少使用。趋势上，P/G IO pad 要和 physical design 协同优化，decoupling capacitors 可以帮助降低 voltage drop，而 multiple voltage/frequency islands 会让 P/G 和 clock distribution 都更复杂。

---

## Slide 21 · Power Grid Creation 要决定什么

Power grid creation 的本质，是在 IR drop、EM 和 routing resources 之间取舍。开始之前，需要 power budget 和 initial power estimation，知道 average current、max current density，再决定 grid 结构。

具体要决定的内容包括：general grid structure，是否有 gating 或 multi-voltage；每个 voltage 的 power pads 数量和位置；使用哪些 metal layers；straps 的 width 和 spacing；via stacks 如何放、会占掉多少 routing tracks；要不要 rings；hierarchical block 是否需要 shielding。最后必须跑 initial power network analysis，确认这版 grid 大方向能撑住。

---

## Slide 22 · Power Grid 与 Macro Placement 的关系

[指 high power blocks 图] 高性能、高功耗 blocks 的 macro placement 不能只看 dataflow，还要看 power delivery。靠近 border power pads 可以缩短供电路径、降低 IR drop；但高功耗 macro 之间也不能全挤在一起，否则局部电流密度太高，EM 风险会上升。

所以课件给的直觉是：power hungry blocks should be close to border power pads, and away from each other。换成中文就是：靠近电源入口，但彼此适当分散。这里再次说明，floorplan 和 power grid 不是两件独立事情，macro placement 本身就是 power planning 的一部分。

---

## Slide 23 · Innovus Flow：从 Init 到 Blockage

最后用 Innovus 的 floorplanning summary 把流程串起来。第一步是 Init Design：定义 Verilog netlist、MMMC 信息，包括 timing、SDC、extraction 等设置，同时读 LEF 和 IO placement。第二步是 Specify Floorplan：定义 floorplan size、aspect ratio、target utilization。

第三步是 Place Hard Macros，可以是 absolute placement，也可以是 relative placement。macro 放好以后，定义 halos 和 blockages。第四步是 Regions & Blockages：必要时定义 placement regions、placement blockage、routing blockage。到这里，几何、macro 和可放置/可布线空间基本成型。

---

## Slide 24 · 结束

Innovus flow 的后半段是电源和 pin。先 Define Global Nets，告诉工具全局 VDD/GND 在顶层和各个 IP 里分别叫什么名字；名字对不上，电源网就可能没有正确连接。然后 Create Power Rings，通常围绕 chip periphery，也可能围绕每个 hard IP。再 Build Power Grid，连接 standard cell follow pins，建立 power stripes，并确认 hard IP 的电源连接足够 robust。最后，如果做的是 block 而不是 fullchip，还要 Assign Pins 到 floorplan 边界。

这一讲收束成一句话：好的 floorplan 不是把所有对象塞进 core，而是让后面的 placement、CTS、routing 和 power signoff 都有路可走。遇到问题时按这条线回查：拥塞看 utilization、macro channel、pin access；时序看 macro/pin/budget；IR/EM 看 power pads、grid、via 和高功耗 macro 位置。下一讲进入 Placement。

---

> 配套幻灯片 slides/05_Floorplan.pptx · 笔记 05_Floorplan.md · 整理 J.C
