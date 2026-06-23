export const meta = {
  name: 'floorplan-strict-align',
  description: 'Strict per-slide audit: re-verify every slide line-by-line against its note section, flag all discrepancies, return fully note-aligned text',
  phases: [{ title: 'Audit', detail: 'one agent per content slide vs its note section' }],
}

const NOTE = 'D:/Documents/IC/IC_Learning_Material/IC_Backend_Notes/05_Floorplan.md'
const SLIDES = 'D:/Documents/IC/IC_Learning_Material/_SlideKit/notes/05_floorplan/slides.py'

// 每张内容页 → 笔记小节。逐页严核。
const SLIDES_LIST = [
  ['1.1 从逻辑网表到物理骨架', '1.1'], ['1.2 沿主线反查', '1.2'], ['1.3 Floorplan 的目标', '1.3'],
  ['1.4 全芯片设计视角', '1.4'], ['1.5 输入、输出与导入前提', '1.5'],
  ['2.1 IO 环与芯片尺寸', '2.1'], ['2.2 利用率与试布线', '2.2'], ['2.3 网表唯一化', '2.3'],
  ['2.4 硬宏摆放', '2.4'], ['2.5 布局区域', '2.5'], ['2.6 阻挡与留边', '2.6'], ['2.7 布线阻挡与好 Floorplan', '2.7'],
  ['3.1 扁平 vs 层次化设计', '3.1'], ['3.2 时序预算与 ILM', '3.2'], ['3.3 引脚分配与穿通', '3.3'],
  ['4.1 电源规划：功耗与可靠性', '4.1'], ['4.2 IR 压降', '4.2'], ['4.3 电迁移 EM', '4.3'],
  ['4.4 PDN 的基本取舍', '4.4'], ['4.5 电源 / 地布线方式', '4.5'], ['4.6 电源网格创建', '4.6'],
  ['4.7 电源网格与宏摆放', '4.7'], ['5.1 Innovus 流程：从初始化到阻挡', '5.1'], ['5.2 判断一个好 Floorplan', '5.2'],
]

const SCHEMA = {
  type: 'object',
  properties: {
    slide: { type: 'string' },
    aligned: { type: 'boolean', description: '当前页文字是否已完全忠于笔记（true=无需改）' },
    discrepancies: {
      type: 'array', items: { type: 'string' },
      description: '逐条列出与笔记的出入：内容错误 / 遗漏的要点 / 体裁不符 / 中英对照缺失 / 自创内容。每条点明笔记里怎么说。',
    },
    corrected: {
      type: 'object',
      description: '完全对齐笔记的替换内容；不需改的字段留空',
      properties: {
        new_sub: { type: 'string', description: '修正后的副标题（含必要中英对照），不改留空' },
        new_style: { type: 'string', enum: ['bullet', 'num', 'prose', ''], description: 'split 体裁（笔记是散文用 prose / 列表用 bullet / 有序用 num），不改留空' },
        new_bullets: { type: 'array', items: { type: 'string' }, description: 'split/bullets 的整组替换文字（完整句、忠于笔记、首次出现英文专有名词中英对照）；不改留空' },
        table_note: { type: 'string', description: 'table 页表下说明（笔记的引言/定义/结论），≤2 行；不改留空' },
        table_fix: { type: 'string', description: '若表格行列内容与笔记有出入，在此说明应如何改（人工应用）；无则留空' },
      },
    },
  },
  required: ['slide', 'aligned', 'discrepancies'],
}

phase('Audit')

const PRELUDE = `你是 IC 后端教学幻灯片的**严格**文字校订。笔记是**唯一真源**。注意：当前幻灯片是上一轮修改的产物，**可能存在理解错误或改得不彻底**，你要把每一句都重新对照笔记核验，别默认它对。

判定「完全对齐」的标准（缺一不可）：
1) **内容正确**：没有与笔记相悖、张冠李戴或自创的说法（数字、术语、因果都要对）。
2) **要点齐全**：笔记该小节里对自学重要的点都在页面体现（含表格页要用 table_note 补笔记的引言/定义/结论）。
3) **体裁对齐**：笔记是散文段→prose；是列表/枚举→bullet/num；是对照表→table。别强行并列、别滥用分点、别把散文拆成悬空短句。
4) **中英对照**：首次出现的英文专有名词写「中文（English）」，沿用笔记配对；不要发明笔记里没有的配对。
5) **完整句**：要点能独立看懂。

先读两文件：笔记（真源）${NOTE}；幻灯片 SPECS ${SLIDES}。`

const results = await parallel(SLIDES_LIST.map(([title, sec]) => () =>
  agent(
    `${PRELUDE}

只审这一张：**${title}**，对应笔记小节 **${sec}**。
在 SLIDES 里找到该页 spec，在笔记里找到 ${sec} 小节，**逐句**比对。把所有出入列进 discrepancies（点明笔记原文怎么说），并给出 corrected（完全对齐笔记的整组替换文字）。若已完全对齐则 aligned=true、不返回 corrected。`,
    { label: `chk:${sec}`, phase: 'Audit', schema: SCHEMA }
  ).then(r => r || { slide: title, aligned: true, discrepancies: [] })
))

return { slides: results.filter(Boolean) }
