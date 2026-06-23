# Floorplan 布图规划介绍

> 《芯片设计从 RTL 到 GDS》学习笔记
> 适用读者：已具备数字电路与逻辑综合基础的工科学生 / 初级数字 IC 后端工程师
> 用途：理解 floorplan 决策如何影响 placement、routing、timing closure 与 power signoff
> 说明：文中命令与 Tcl/UPF/LEF 片段均为工程骨架，真实项目以对应工具版本 User Guide / `man` 为准。

---

## 目录

1. [本篇导读：Floorplan 到底解决什么问题](#0-本篇导读floorplan-到底解决什么问题)
2. [从逻辑描述到物理描述](#1-从逻辑描述到物理描述)
3. [Floorplan 的输入、输出与设计导入前提](#2-floorplan-的输入输出与设计导入前提)
4. [芯片尺寸：IO Ring、Core Limited 与 Pad Limited](#3-芯片尺寸io-ringcore-limited-与-pad-limited)
5. [Core 区域、利用率与可布线性](#4-core-区域利用率与可布线性)
6. [Hard Macro 摆放：让标准单元区域保持可用](#5-hard-macro-摆放让标准单元区域保持可用)
7. [Placement Region、Blockage 与 Halo](#6-placement-regionblockage-与-halo)
8. [IO / Bump / Pin Assignment 与层次化接口](#7-io--bump--pin-assignment-与层次化接口)
9. [Flat vs. Hierarchical：时序预算、ILM 与 Feedthrough](#8-flat-vs-hierarchical时序预算ilm-与-feedthrough)
10. [Power Planning：从 Power Pads 到 Power Grid](#9-power-planning从-power-pads-到-power-grid)
11. [IR Drop 与 EM：电源完整性为什么要在 Floorplan 阶段考虑](#10-ir-drop-与-em电源完整性为什么要在-floorplan-阶段考虑)
12. [多电压域与 Power Gating 在 Floorplan 中的落地](#11-多电压域与-power-gating-在-floorplan-中的落地)
13. [一次典型 Floorplan Flow 如何串起来](#12-一次典型-floorplan-flow-如何串起来)
14. [Debug 指标与常见问题定位](#13-debug-指标与常见问题定位)
15. [本章小结](#14-本章小结)
16. [易混淆点 · 课后自测](#15-易混淆点--课后自测)

---

## 0. 本篇导读：Floorplan 到底解决什么问题

Floorplan 是数字后端从“逻辑世界”进入“物理世界”后的第一类关键决策。综合得到的门级网表只描述了实例和连接关系，并不说明任何 cell、macro、IO 或电源结构应该放在芯片的什么位置。Floorplan 的任务，就是把这张逻辑网表映射成一个物理布局骨架。

Floorplanning 本质上是一个 mapping：

- logical description：netlist，描述“谁和谁相连”；
- physical description：floorplan，描述实例、IO、宏单元和电源网络在芯片上如何摆放、连接和供电。

这一步要同时服务三个目标：

1. **Minimize chip area**：芯片面积不能无谓放大；
2. **Minimize delay**：关键路径不能被宏和引脚位置拉得太长；
3. **Minimize routing congestion**：后续布线要有资源、有通道、有 pin access。

这三个目标天然冲突：面积压得太紧会拥塞，通道留太宽会浪费面积，电源网做太强会抢走信号布线资源。因此，Floorplan 不只是定义芯片边界，而是在面积、时序、拥塞和供电可靠性之间做第一轮工程取舍。

---

## 1. 从逻辑描述到物理描述

![Floorplan 在物理实现流程中的位置](assets/floorplan/f01_position.png)

### 1.1 在后端流程中的位置

Floorplan 位于设计导入之后、placement 之前。它依赖已经读入的设计网表、工艺与单元库、约束和功耗意图，并把它们落成第一版可实现的物理骨架。

一个常见流程可以概括为：

```text
Design Import
  -> Floorplan
  -> Placement
  -> CTS
  -> Routing
  -> Finish / Signoff
```

这里的 Design Import 不只是 `read_verilog`。它通常还包括读入 LEF / Liberty / NDM、MMMC 视图、SDC、UPF/CPF、IO 信息、宏信息，以及初始化设计数据库。

### 1.2 Floorplan 需要决定的对象

从 fullchip 视角看，floorplan 需要同时考虑：

| 对象 | Floorplan 阶段要回答的问题 |
|------|----------------------------|
| Chip size | die / block 有多大，长宽比如何 |
| Core placement area | 标准单元可放置区域在哪里，利用率多少 |
| Interface to outside | IO pads / bumps / package pinout 如何对应 |
| Hard IP / Macros | SRAM、ROM、PLL、模拟 IP 等硬块放在哪里 |
| Power Delivery | power pads 数量和位置，grid/ring/stripe 怎么建 |
| Multiple Voltages | 电源域、电压岛、always-on 资源如何预留 |
| Clocking Scheme | 时钟分布是否需要特殊通道、约束或宏位置配合 |
| Flat or Hierarchical | 整颗芯片一次实现，还是切成多个 block 实现 |

在 fullchip floorplan 中，core placement area、periphery I/O area、P/G pads、P/G grid、RAM/ROM/IP 必须被同时考虑。它们共同说明 floorplan 的本质：把会互相抢空间的对象组织成一个可实现的平面结构。

---

## 2. Floorplan 的输入、输出与设计导入前提

![Floorplan 输入与输出](assets/floorplan/f12_io.png)

### 2.1 输入：不是只有网表

Floorplan 的输入至少包括：

| 输入 | 作用 |
|------|------|
| Design netlist | 设计实例和连接关系，是 floorplan 的逻辑来源 |
| Area requirements | 估算 core size、利用率和 macro 空间 |
| Power requirements | 决定 power pads、power grid、high-power macro 摆放 |
| Timing constraints | 影响 block 划分、pin assignment、macro dataflow |
| Physical partitioning information | 层次化设计中 block 的边界和约束 |
| Die size / performance / schedule trade-off | 决定面积、时序、进度之间的工程取舍 |
| IO placement / macro hints | 可选输入，但能显著减少初期迭代 |

### 2.2 输出：让设计 ready for placement

Floorplan 的输出不应只是“概念图”，而应包含足够让标准单元进入 placement 的物理信息：

- die 或 block area；
- IO 已摆放；
- hard macros 已摆放并固定；
- power grid 初步设计完成；
- 必要的 power pre-routing 已完成；
- standard cell placement areas 已定义；
- blockages、halos、regions 等约束已落入数据库；
- 可布线性、时序和电源完整性已有早期评估。

### 2.3 进入物理域前必须 uniquify

进入 physical domain 前，网表必须 uniquify。所谓 unique netlist，是指每个子模块只被引用一次。否则，物理优化某个实例内部的 cell 时，会误伤另一个共享同一 module definition 的实例。

例如，若 `m1` 和 `m2` 都引用同一个 `amod`，且 `amod` 内部有 `u1`，工具想优化 `m1/u1` 时，可能无法只改变 `m1/u1` 而不影响 `m2/u1`。因此，综合后的网表必须在 placement 之前完成 uniquify，可以由综合工具完成，也可以在 design import 阶段完成。

---

## 3. 芯片尺寸：IO Ring、Core Limited 与 Pad Limited

![芯片几何 Die/IO/Core/Rows](assets/floorplan/f03_geometry.png)

### 3.1 Die、Core、IO Ring 的嵌套关系

芯片几何可以先按由外到内理解：

| 概念 | English | 说明 |
|------|---------|------|
| 晶粒区 | Die Area | 整颗芯片最外边界，含 scribe / seal ring / IO 等 |
| IO 区 | IO Area / Pad Ring | Die 与 core 之间的外围区域，放 IO cell、pad、ESD、corner cell 等 |
| 核心区 | Core Area | 放标准单元、宏单元和内部电源结构的主要区域 |
| Core-to-IO Spacing | Core 到 IO 间距 | 留给 power ring、IO routing、ESD 与边界结构 |

粗略地说：

```text
Die ⊃ IO / Pad Ring ⊃ Core ⊃ (Macros + Standard Cell Rows)
```

### 3.2 IO Ring 为什么是核心约束

IO pinout 往往由前端、系统或封装侧先提出，但 physical design 必须参与评审。原因有两个：

1. **I/O 不像逻辑晶体管那样随工艺快速缩小**，IO cell 和 pad 面积非常贵；
2. **I/O 不只传信号，还负责供电**，power pads 和 ground pads 的数量、位置会直接影响 IR drop 和 EM。

因此，IO planning 是 floorplanning 的中心问题之一，而不是最后补一圈 pad。

### 3.3 Core Limited vs Pad Limited

选择芯片尺寸时，首先判断设计是 core limited 还是 pad limited：

| 类型 | 尺寸由谁决定 | 优化重点 |
|------|--------------|----------|
| Core Limited | 逻辑规模、macro、布线资源决定芯片大小 | utilization、macro placement、routing resources |
| Pad Limited | IO 数量、pad pitch、封装 pinout 决定 die 不能再小 | IO ring、pad/bump 分配、package 协同 |

如果是 pad limited，core 内部可能还有余量，但 die 边界被 IO 撑大；如果是 core limited，IO 不是瓶颈，真正要优化的是核心区面积、macro 和布线资源。

---

## 4. Core 区域、利用率与可布线性

![利用率与长宽比](assets/floorplan/f04_util.png)

### 4.1 Utilization 只是第一版估计

Floorplan 阶段的 utilization 通常指 standard cells 占 core area 的比例。常见初值可能是 70%，但这只是初始猜测，不是规范。

利用率太高会导致：

- routing congestion 上升；
- placement legalization 和优化阶段自由度不足；
- pin-dense cells 周围局部拥塞；
- power grid 与 signal routing 抢资源；
- timing optimization 难以插 buffer 或调整位置。

利用率太低也不是好事：

- die / block 面积浪费；
- 平均走线更长；
- 时钟树和全局互连可能变差。

### 4.2 总利用率与有效利用率

工程里常见两个口径：

```text
Total Util     = (Σ std_cell_area + Σ macro_area) / Core_area
Effective Util = Σ std_cell_area / (Core_area - blockage - macro_halo - keepout - ...)
```

工具报告里的 utilization 往往更接近有效利用率，因为它关心的是标准单元实际还能放进多少可用区域。看报告时必须确认工具口径。

### 4.3 Trial Route 是必要反馈

不能只凭 utilization 决定 die size。完成初始面积估算后，需要跑 quick trial route 或 global routing 估计，检查 routing congestion，再决定是否需要：

- 放大 core，降低 utilization；
- 调整 synthesis，减少过密逻辑或高 fanout；
- 改 macro placement，打开 channel；
- 改 pin assignment，减少长绕线；
- 增加或重分配 routing resources。

这也是 floorplan 的迭代本质：先给出假设，再用 trial place / trial route 让工具反馈，最后回到 floorplan 重新调整。

### 4.4 Row 与 Site：给 placement 留合法位置

虽然 row/site 在 placement 中会更详细展开，但 floorplan 阶段必须知道 core 是如何变成标准单元可放置区域的。

![标准单元行/site/翻转共享供电轨](assets/floorplan/f05_rows.png)

- **Row**：core 被切成等高的标准单元行；
- **Site**：行内最小放置栅格，cell 宽度通常是 site 宽度整数倍；
- **相邻行翻转**：让同名 VDD/VSS 轨落在行边界、被上下两行共享，减少供电轨条数并保持 follow-pin rail 连续。

```lef
SITE core
  CLASS CORE ;
  SYMMETRY Y ;
  SIZE 0.190 BY 1.260 ;
END core
```

这里的 `SYMMETRY` 描述单元允许的镜像方式；具体行方向、轨共享方式以工艺库和工具文档为准。

---

## 5. Hard Macro 摆放：让标准单元区域保持可用

![宏单元摆放原则](assets/floorplan/f06_macro.png)

### 5.1 为什么 macro 是 Floorplan 的核心难点

Hard macro 包括 SRAM、ROM、PLL、模拟 IP、第三方 hard IP 等。它们具有几个特点：

- 面积大；
- 形状固定；
- pin 固定；
- 内部不可被 placer 任意拆开；
- 对 routing、timing、power 都有强影响。

因此，floorplan 通常先放 hard macros，再让 placement 处理标准单元。宏摆错了，后面很难靠 placement 和 routing 完全救回来。

### 5.2 Macro Placement 的基本原则

Macro placement 的主线是：**把大 macro 推到边缘或角落，让标准单元区域保持一个尽量完整的大矩形**。原因是 placement algorithms 通常更喜欢 single large rectangular placement area。若宏把 core 切得支离破碎，placer 和 router 都会痛苦。

常用原则：

1. **沿边 / 沿角**：大宏尽量靠 core 边界或角落，不在中心挖洞；
2. **按 dataflow 就近**：让强连接的 macro / logic 靠近，用 flylines 看连接权重；
3. **保留 routing channel**：宏与宏、宏与边界之间要留足信号、电源、时钟通道；
4. **改善 pin accessibility**：必要时旋转 macro，让 pin 面向更开放的区域；
5. **避免 pin 对着窄 channel 或 corner**：这会制造局部 pin access 拥塞；
6. **摆好后 fixed**：hard macro 位置确定后通常标记为 fixed。

### 5.3 Macro 与电源的关系

对 wire-bond 设计，高功耗 macro 不宜放在芯片中心太深的位置，因为 power pads 通常在边缘，供电路径越长，IR drop 压力越大。实用规则是：

- high-power blocks 靠近 border power pads；
- high-power blocks 之间不要过度集中，避免局部电流密度过高和 EM 风险。

这说明 macro placement 不是单纯的 dataflow 问题，也属于 power planning 的一部分。

---

## 6. Placement Region、Blockage 与 Halo

![channel / halo / blockage](assets/floorplan/f07_halo.png)

### 6.1 Placement Region：表达“希望放在哪里”

Placement region 是帮助工具表达设计意图的方式，用来引导或限制某些 cell 的摆放区域。

| 类型 | 含义 | 强度 |
|------|------|------|
| Soft guide | 希望这些 cells 聚在一起，但无固定区域 | 最软 |
| Guide | 尽量放在指定区域 | 较软 |
| Region | 指定 cells 必须放在该区域，其他 cells 也可进入 | 较硬 |
| Fence | 指定 cells 必须放在该区域，其他 cells 不可进入 | 最硬 |

越硬的约束越容易制造局部拥塞，因此 region/fence 应只用于必要的结构性意图。

### 6.2 Placement Blockage：表达“这里不要放 cell”

Placement blockage 用于限制标准单元放置：

| 类型 | 作用 |
|------|------|
| Hard blockage | 完全禁止放置标准单元 |
| Soft blockage | 初始 placement 阶段禁用，优化阶段可用于 buffer/inverter |
| Partial blockage | 限制区域最大密度，例如最多 40% |

工程实践中，macro 四周常放 hard blockage，而 macro 与 macro 或 macro 与 core boundary 之间的 channel 可用 soft blockage 保留弹性，避免初期被标准单元塞满。

### 6.3 Halo / Keepout Margin：保护 macro 周边

Halo，也叫 padding 或 keepout margin，是 macro 外围保留的一圈空白区域。它主要用于：

- 改善 macro pin accessibility；
- 给 buffer / inverter 插入留空间；
- 给 power routing 和 signal routing 留出近宏通道；
- 避免 cell 贴得太近造成 DRC 或 routing 困难。

高频区别：

```text
Halo    -> 跟随 macro 移动
Blockage -> 多为固定坐标区域
```

### 6.4 Routing Blockage：表达“这里不要走线”

Routing blockage 限制的是 routing，而不是 placement。它可以指定某个 layer 或 layer range，例如禁止 M1-M3 在某个区域走线。常见用途包括：

- 保护 macro 上方特殊区域；
- 给电源结构预留资源；
- 避免低层金属被不合适的信号占用；
- 保护噪声敏感模拟区。

### 6.5 物理专用单元的早期规划

有些 physical-only cells 不参与逻辑功能，但 floorplan / early placement 阶段就要考虑。

| 单元 | 作用 | 典型时机 |
|------|------|----------|
| Endcap / Boundary Cell | 放在 row 端点、macro/void 边界，保证 well/implant 连续和 DRC | floorplan / early placement |
| Well-tap / Tap Cell | 周期性提供 well bias，避免 latch-up，满足 max tap distance | floorplan / early placement |
| Filler Cell | 填补行内空隙，保证 rail / well 连续 | placement 后期 / routing 前 |

---

## 7. IO / Bump / Pin Assignment 与层次化接口

![Wire-bond vs Flip-Chip](assets/floorplan/f13_iopad.png)

### 7.1 Wire-bond 与 Flip-chip

两种常见封装连接思路：

| 类型 | 连接方式 | Floorplan 关注点 |
|------|----------|------------------|
| Wire-bond | IO pads 沿 die 四周排成 pad ring，通过金线键合 | pad pitch、ESD、corner pads、power/signal pad 分布 |
| Flip-chip | die 表面形成 bump array，经 bump / RDL / UBM 连接封装 | bump map、RDL、power/signal bump 比例、面阵列布线 |

要点：wire-bond 走四周 pad ring，flip-chip 走面阵列 bump。

### 7.2 顶层 IO 与块级 pin 是两件事

顶层 IO placement 决定芯片对外接口位置；块级 pin assignment 决定 hierarchical blocks 之间怎么连接。两者都属于 floorplan，但影响点不同：

- 顶层 IO 影响封装、ESD、power pads、chip boundary；
- block pins 影响 block 间走线、timing budget、feedthrough 和 fullchip closure。

### 7.3 Block Pin Assignment 的约束

块级 pin 的约束常包括：

- routing layer；
- pin spacing；
- pin size；
- overlap 规则；
- net group；
- pin guide；
- dataflow 方向；
- trial-route boundary crossings。

参考命令骨架：

```tcl
# ICC2 块级 pin 约束骨架
set_individual_pin_constraints -ports {data_in[*]} -side left -layers {M3 M5}
set_block_pin_constraints -self -allowed_layers {M3 M4 M5} -pin_spacing 0.5
place_pins -self
```

pin 不宜挤在 partition corners，因为 corner 附近 routing 方向变化多、资源紧张，容易让块间路径绕远。

---

## 8. Flat vs. Hierarchical：时序预算、ILM 与 Feedthrough

![时序预算与模块划分](assets/floorplan/f11_budget.png)

### 8.1 为什么要层次化

如果设计太大，flat flow 一次跑完整颗芯片会遇到 runtime 和 memory 压力。层次化设计把 fullchip 切成多个 blocks，每个 block 独立实现，再在顶层做 fullchip timing and verification。

优点：

- EDA runtime 更短；
- memory 更少；
- ECO turn-around 更快；
- 有利于 design reuse。

代价：

- fullchip timing closure 更难；
- pin assignment 和 feedthrough 更关键；
- timing constraint budgeting 更复杂；
- block abstraction / ILM / ETM 需要维护。

### 8.2 Timing Budgeting：把顶层约束拆到块边界

Chip-level constraints 必须映射成 block-level constraints。例如顶层某个输入到 block 的路径预算为 1.5 ns，block 实现时就需要在 block 边界建立对应的 input delay / output delay / uncertainty / load / driving cell 等约束。

```tcl
create_clock -name clk -period 2.0 [get_ports clk]
set_input_delay  0.6 -clock clk [get_ports data_in]
set_output_delay 0.7 -clock clk [get_ports data_out]
set_clock_uncertainty 0.10 [get_clocks clk]
set_driving_cell -lib_cell BUFX4 [get_ports data_in]
set_load 0.05 [get_ports data_out]
```

预算合理，各 block 独立收敛后 fullchip 才容易收敛；预算不合理，单个 block 看似通过，fullchip 仍然可能失败。

### 8.3 ILM / ETM：让顶层分析更轻

Interface Logic Model（ILM）保留 block 边界附近与接口时序相关的逻辑，同时隐藏 block 内部大量细节。ETM（Extracted Timing Model）也用于提供 block 的抽象时序模型。它们的目的都是让 fullchip timing analysis 更快、更可控。

### 8.4 Feedthrough：别让信号绕整块

在 channel-less 或 channel 资源紧张的设计中，feedthrough 很关键。若信号从 Partition A 到 Partition C，中间隔着 Partition B，而 B 没有 feedthrough，信号可能被迫绕过整个 block。

解决办法是在 B 上生成 feedthrough pin / feedthrough net，把跨越 B 的连接拆成几段，让信号沿规划好的边界穿过。

---

## 9. Power Planning：从 Power Pads 到 Power Grid

![电源规划](assets/floorplan/f08_power.png)

### 9.1 Power Planning 不是后期补线

Power planning 要解决的是把电流从 pads 送到芯片上所有 transistors，同时保持稳定电压、低噪声、低 IR drop，并避免 EM 和 self-heating。它从 floorplan 阶段就开始，而不是 routing 后的补救。

Power Distribution Network（PDN）需要：

- carry current from pads to transistors；
- maintain stable voltage with low noise；
- provide average and peak power demands；
- provide current return paths for signals；
- avoid electromigration and self-heating wearout；
- consume reasonable chip area and routing resources。

### 9.2 Power Grid 的层次

常见电源结构自上而下包括：

| 结构 | English | 作用 |
|------|---------|------|
| Power pads / bumps | 电源入口 | 从封装引入 VDD/VSS |
| Power rings | 电源环 | 围绕 chip / core / hard IP 的主干环 |
| Power stripes | 电源条 | 横跨 core 分担电流 |
| Power mesh | 电源网格 | 纵横条带互连，降低等效电阻 |
| Std-cell rails | Follow-pin rails | 沿标准单元行连接每个 cell 的 VDD/VSS |
| Special route | sroute | 连接 pad/ring/stripe/block pin/core pin/follow-pin rail 并打 via |

参考命令骨架：

```tcl
# Innovus 命令骨架
globalNetConnect VDD -type pgpin -pin VDD -all
globalNetConnect VSS -type pgpin -pin VSS -all

addRing   -nets {VDD VSS} -type core_rings \
          -layer {top M9 bottom M9 left M8 right M8} -width 3

addStripe -nets {VDD VSS} -layer M9 -direction vertical \
          -width 2 -set_to_set_distance 40

sroute    -nets {VDD VSS} \
          -connect {corePin floatingStripe blockPin padPin}
```

Synopsys ICC2 / Fusion Compiler 侧常见思路是 `create_pg_ring` / `create_pg_mesh` / `create_pg_std_cell_conn_pattern` 后 `compile_pg`。

### 9.3 Power Grid Creation 要决定的参数

Power Grid Creation 需要明确以下参数：

- general grid structure：是否有 gating 或 multi-voltage；
- power pads 数量和位置，每个 voltage 单独考虑；
- 使用哪些 metal layers；
- straps 的 width 和 spacing；
- via stacks 与可用 routing tracks 的取舍；
- rings / no rings；
- hierarchical block shielding；
- initial power network analysis。

Power grid 的取舍是：线更宽、更多层、多 via 可以降低 IR / dI/dt / EM 风险；但它会吃掉 signal routing resources，导致更高 congestion。

---

## 10. IR Drop 与 EM：电源完整性为什么要在 Floorplan 阶段考虑

![IR drop 与 EM](assets/floorplan/f09_irem.png)

### 10.1 IR Drop

IR drop 是供电线上的电压下降：

```text
ΔV = I · R
```

芯片上的 power grid 是一个巨大网络，工具会建立 resistance matrix，结合每个 gate 的 average current，求解每个节点的电压。若 actual voltage level 低于 tolerance level，cell delay 会增加，timing 可能失败，严重时功能错误。

一个典型估算能说明问题：1 mm 长、100 nm 宽的 M1 power rail，若 sheet resistance 为 0.1 ohm/square，线电阻可达约 1000 ohm；若承载约 0.1 mA，IR drop 可达约 100 mV。这说明细而长的低层电源线无法单独承担供电，必须用更宽、更厚、更高层、多路径、多 via 的结构。

### 10.2 Electromigration

Electromigration（EM，电迁移）是电流长期流过导体时，电子动量推动金属原子迁移，可能导致：

- open：单根线上形成 void；
- short：相邻线之间 bridging；
- RC 改变：即使没开短路，也可能造成性能退化。

IR 更偏“瞬时电压够不够”，EM 更偏“长期电流密度能不能扛住”。两者都与 floorplan 有关，因为 power pads、high-power macro 位置、grid width/spacing/via 都是在 early floorplan 里决定或预留的。

### 10.3 Hot Spots 与局部修复

IR drop 通常用 color map 找 hot spots。修复不一定是全局加密，有时只需要：

- 在热点附近加一条 power wire；
- 增加 via array；
- 加宽或加密 stripes；
- 调整 high-power macro 位置；
- 增加或重分配 power pads / bumps；
- 改善 block-level power connection。

---

## 11. 多电压域与 Power Gating 在 Floorplan 中的落地

![多电压域与 UPF](assets/floorplan/f10_mv.png)

### 11.1 Multi-voltage 为什么影响 Floorplan

Multiple voltages / voltage islands 会让 power grid 和 clock distribution 更复杂。原因是不同电源域需要不同的供电入口、grid 结构和边界处理。

每个电源域可能需要：

- 独立 voltage area；
- 独立 VDD/VSS net；
- power switch；
- always-on power；
- isolation cells；
- level shifters；
- retention cells；
- domain boundary 约束。

### 11.2 UPF / CPF 与关键单元

UPF（IEEE 1801）和 CPF 都是 power intent 描述方式。floorplan 根据 power intent 创建 voltage area，规划独立 PG，预留 level shifter / isolation / switch 等单元位置。

| 单元 | 作用 | 场景 |
|------|------|------|
| Level Shifter | 转换跨电压域信号电平 | 信号跨不同电压域 |
| Isolation Cell | 域关断时把输出钳位到已知值 | 可关断域输出到常开域 |
| Retention FF | 断电时保存状态，上电恢复 | 需要状态保持的可关断域 |
| Always-on Buffer | 控制信号在关断域内仍有效 | enable / retention / isolation control |
| Power Switch | 控制某域 VDD/VSS 是否接通 | power gating |

```tcl
# UPF 约束骨架
create_power_domain PD_CPU -elements {u_cpu}
create_power_switch sw_cpu -domain PD_CPU \
  -input_supply_port  {vin VDD} \
  -output_supply_port {vout VDD_CPU} \
  -control_port       {ctrl pwr_en} \
  -on_state           {ON vin {ctrl}}

set_isolation iso_cpu -domain PD_CPU -clamp_value 0 -applies_to outputs \
  -isolation_power_net VDD -isolation_ground_net VSS

set_level_shifter ls_cpu -domain PD_CPU -rule low_to_high -location self
create_voltage_area -power_domain PD_CPU -region {{100 100} {400 400}} VA_CPU
```

### 11.3 Header / Footer Power Switch

![电源门控 header / footer](assets/floorplan/f14_gating.png)

Power gating 常见两类 switch：

| 类型 | 器件 | 位置 | 特点 |
|------|------|------|------|
| Header | PMOS | 真 VDD 与虚拟 VDD 之间 | 工程更常用，漏电控制较好 |
| Footer | NMOS | 虚拟 VSS 与真 VSS 之间 | 较少单独使用 |

Floorplan 阶段要规划 switch 阵列位置、enable daisy-chain 走向、inrush current 控制、always-on / secondary PG 连接。唤醒时冲击电流大，enable 通常需要分时错开开启。

---

## 12. 一次典型 Floorplan Flow 如何串起来

![Floorplan 迭代闭环](assets/floorplan/f15_loop.png)

### 12.1 Innovus 视角的主流程

实践中可以按以下工具无关步骤串起 floorplanning flow：

```text
1. Init Design
   - read netlist / LEF / MMMC / SDC / IO placement

2. Specify Floorplan
   - floorplan size
   - aspect ratio
   - target utilization

3. Place Hard Macros
   - absolute or relative placement
   - mark fixed
   - define halos and blockages

4. Regions & Blockages
   - placement regions
   - placement blockages
   - routing blockages

5. Define Global Nets
   - map top-level VDD/GND names to IP pg pins

6. Create Power Rings
   - chip periphery rings
   - hard IP rings if needed

7. Build Power Grid
   - standard-cell follow pins
   - power stripes / mesh
   - robust hard IP power connection

8. Assign Pins
   - block boundary pins for hierarchical implementation
```

### 12.2 ICC2 / Innovus 命令速查

| 任务 | Synopsys ICC2 / FC | Cadence Innovus |
|------|--------------------|-----------------|
| 初始化 floorplan | `initialize_floorplan` | `floorPlan` |
| 从 DEF 恢复 | `read_def` | `defIn` |
| 利用率 / 尺寸 / AR | `-core_utilization` / `-side_ratio` | `floorPlan -r` |
| macro halo | `create_keepout_margin` | `addHaloToBlock` |
| placement blockage | `create_placement_blockage` | `createPlaceBlockage` |
| pin assignment | `place_pins` / `set_block_pin_constraints` | `editPin` / `assignIoPins` |
| PG structure | `create_pg_ring/mesh` + `compile_pg` | `addRing` / `addStripe` / `sroute` |
| voltage area | `create_voltage_area` | `createPowerDomain` |

易错点：很多 margin 参数顺序是 **LBRT = left bottom right top**，不是 LTRB。`defIn` 是读已有 DEF，`floorPlan` 是创建 floorplan，语义不同。

### 12.3 Floorplan 是迭代闭环

完整思路不是一次写完脚本就结束，而是：

```text
floorplan
  -> trial placement / trial route
  -> congestion / timing / IR early analysis
  -> adjust utilization / macro / channel / pins / PG
  -> repeat until acceptable
  -> detailed placement
```

---

## 13. Debug 指标与常见问题定位

### 13.1 关键指标

| 指标 | 看什么 |
|------|--------|
| Core utilization | 是否太高导致拥塞，或太低浪费面积 |
| Congestion overflow | trial route / global route 是否有大面积红区 |
| Pin access | macro pin、block pin、pin-dense cells 是否可达 |
| WNS / TNS | early timing 是否被 macro / pin 位置拉坏 |
| IR drop | static / dynamic IR 是否超过预算 |
| EM margin | grid / stripes / vias 是否满足电流密度 |
| PG connectivity | VDD/GND 是否正确连接到 std cells、macros、pads |
| DRC precheck | boundary、tap、halo、row、macro spacing 是否合理 |

### 13.2 常见问题与反查方向

| 现象 | 常见根因 | Floorplan 调整方向 |
|------|----------|--------------------|
| 绕不出、拥塞红区 | utilization 太高、channel 太窄、macro 切碎 core | 降利用率、加宽 channel、移动/旋转 macro、加 partial blockage |
| macro 周围 pin access 差 | pins 对着窄通道、halo 不足 | 调朝向、加 halo、重分配 pin guide |
| timing 早期很差 | dataflow 不顺、block pins 离逻辑远 | 按 flyline 重摆 macro、优化 pin assignment、重做 timing budget |
| IR drop 热点 | high-power macro 离 power pads 远、grid 太弱 | 靠近 power pads、加 stripe/mesh/via、补 power bumps |
| EM 风险高 | 高功耗块集中、线宽/via 不足 | 分散 high-power macros、加宽线、多 via、多路径 |
| block 间信号绕远 | 缺 feedthrough、pin 放角落 | 生成 feedthrough pins/nets，调整 pin guides |
| power gating 唤醒冲击大 | switch 同时打开 | enable daisy-chain 分时开启，调整 switch 分布 |

---

## 14. 本章小结

1. Floorplan 是从 logical description 到 physical description 的 mapping，不只是定义几何边界。
2. 它的核心目标是同时控制面积、延迟和 routing congestion。
3. Fullchip floorplan 要一起考虑 chip size、IO、macro、power delivery、multiple voltages、clocking 和 hierarchy。
4. 输入不仅有 netlist，还有 area、power、timing、partition、IO/macro hints；输出必须让设计 ready for placement。
5. Chip size 要区分 core limited 和 pad limited；IO ring 不只是信号，也包括 power pads。
6. Utilization 只是初始假设，必须用 trial route / congestion feedback 验证。
7. Hard macro placement 要保持 single large rectangular standard-cell area，避免切碎 core。
8. Region、blockage、halo、routing blockage 分别表达不同意图，不能混用。
9. Hierarchical design 用 runtime/memory 换来 timing budget、pin assignment、feedthrough 的复杂性。
10. Power planning 从 floorplan 阶段开始，power pads、grid、macro placement 共同决定 IR/EM 风险。
11. Multi-voltage / power gating 需要 voltage area、always-on PG、switch、LS/ISO/retention 等物理预留。
12. 好的 floorplan 是迭代闭环：floorplan -> trial place/route -> 评估 -> 回退调整。

---

## 15. 易混淆点 · 课后自测

1. Floorplan 的目标为什么不是单纯“面积最小”？
2. Core limited 和 pad limited 的优化方向有什么不同？
3. 为什么 IO 不随 Moore's Law 缩小会影响 chip size？
4. utilization 为什么不能单独证明 floorplan 可实现？
5. total utilization 和 effective utilization 的分母有什么区别？
6. 为什么 hard macro 通常靠边或靠角摆放？
7. macro placement 为什么也属于 power planning？
8. placement region、placement blockage、routing blockage 分别限制什么？
9. halo 和 placement blockage 的核心区别是什么？
10. feedthrough 解决的是哪类层次化布线问题？
11. timing budget 为什么和 pin assignment 强相关？
12. ILM / ETM 为什么能加速 fullchip timing？
13. IR drop 和 EM 分别对应“短期电压”还是“长期可靠性”？
14. power grid 为什么不能无限加宽加密？
15. multi-voltage floorplan 为什么需要 always-on PG？
16. `defIn` 和 `floorPlan` 的语义为什么不能混用？
