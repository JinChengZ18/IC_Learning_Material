export const meta = {
  name: 'floorplan-text-align',
  description: 'Per chapter, align each slide text faithfully to the note: 中英对照 on first occurrence, fix content drift / forced-parallel / mixed in-out, add table explanatory text',
  phases: [{ title: 'Align', detail: 'one agent per chapter: note↔slide text alignment' }],
}

const NOTE = 'D:/Documents/IC/IC_Learning_Material/IC_Backend_Notes/05_Floorplan.md'
const SLIDES = 'D:/Documents/IC/IC_Learning_Material/_SlideKit/notes/05_floorplan/slides.py'

const CHAPTERS = [
  { n: '1', subs: '1.1–1.5', focus: '1.2 现在只有反查表、丢了「本讲路线/主线」叙述(按工程决策顺序展开)，要把主线补回；1.4 丢了「FP 重要性」(修改成本随阶段上升 + PPA 权衡 + 这些对象互相抢空间)，作为 table_note 补回；1.5 输入与输出混在一起，要分成「输入」与「输出」两组(笔记输入是带「作用」的表、输出是清单)。' },
  { n: '2', subs: '2.1–2.7', focus: '2.5 纯表缺说明(笔记的「布局区域是帮 P&R 工具表达设计意图」定义 + 「越硬越易拥塞、只用于必要结构意图」)→table_note；2.6 文字强行并列、与笔记(散文+三种阻挡表+halo 散文)不齐；2.7 格式没和笔记对齐(笔记是 用途清单 + 好 floorplan 特征清单)。' },
  { n: '3', subs: '3.1–3.3', focus: '3.1 优点/代价是真列表可保留，但检查是否有「强行并列」、与笔记定义句对齐(扁平 flat / 层次化 hierarchical 定义)。' },
  { n: '4', subs: '4.1–4.7', focus: '4.4 纯表缺说明(「电源线越强 IR/EM 越低但越抢信号资源」引言 + 「好 PDN 尽量宽厚多路径但别吃光信号资源」结论)→table_note；4.5 纯表缺说明(已部分在副标题，确认笔记「标准做法」整段在)；4.6 命令骨架与 9 项决定。' },
  { n: '5', subs: '5.1–5.2', focus: '5.2 纯表缺说明(「好 floorplan 让后面 Place/CTS/Route/Signoff 都有路可走」+ 笔记结尾的迭代闭环总结)→table_note。' },
]

const SCHEMA = {
  type: 'object',
  properties: {
    chapter: { type: 'string' },
    fixes: {
      type: 'array',
      description: '只列需要改的页；不需改的不返回',
      items: {
        type: 'object',
        properties: {
          slide: { type: 'string', description: '页标题，如 "1.2 沿主线反查"' },
          kind: { type: 'string', description: 'split / table / bullets' },
          issue: { type: 'string', description: '一句话问题' },
          new_sub: { type: 'string', description: '修正后的副标题（含中英对照），不改留空' },
          new_style: { type: 'string', enum: ['bullet', 'num', 'prose', ''], description: 'split 文字体裁修正，不改留空' },
          new_bullets: { type: 'array', items: { type: 'string' }, description: 'split/bullets 修正后的整组文字（完整句、忠于笔记、首次出现的英文专有名词用「中文（English）」中英对照）；不改留空' },
          table_note: { type: 'string', description: 'table 页要补的说明文字（取自笔记的引言/结论/定义），一两句；非 table 或无需补留空' },
        },
        required: ['slide', 'kind', 'issue'],
      },
    },
  },
  required: ['chapter', 'fixes'],
}

phase('Align')

const PRELUDE = `你是 IC 后端教学幻灯片的文字校订。唯一真源是笔记，把每页文字**忠实对齐笔记**。

**硬规范（全章贯彻）：**
1) **中英对照**：每个英文专有名词**首次出现**时写成「中文（English）」，沿用笔记的配对（如 布图规划（floorplan）、硬宏（hard macro）、利用率（utilization）、试布线（trial route）、留边（halo）、阻挡（blockage）、电源分布网络（PDN）、电迁移（electromigration, EM）、接口逻辑模型（ILM）、穿通（feedthrough）…）。同一页内第二次起可只用其一。
2) **不滥用分点 / 不强行并列**：笔记是散文段就用 prose（整段）、是真列表/枚举/对照才分点；并列项必须真并列，别把因果/递进硬拆成并列。
3) **不要过度精简**：笔记里对自学重要的点要在页面体现；纯表格页若笔记有引言/定义/结论说明文字，用 table_note 补上。
4) 要点写**完整句**，能独立看懂。

先读两文件：笔记（真源）${NOTE}；幻灯片 SPECS ${SLIDES}。`

const results = await parallel(CHAPTERS.map(ch => () =>
  agent(
    `${PRELUDE}

只审【第 ${ch.n} 章（${ch.subs}）】。重点排查：${ch.focus}
另外**逐页**检查中英对照与文字是否忠于笔记。对每张需要改的页，返回修正后的 new_sub / new_style / new_bullets / table_note（不改的字段留空，不需改的页不返回）。new_bullets 要给**整组**替换文字。`,
    { label: `align:ch${ch.n}`, phase: 'Align', schema: SCHEMA }
  ).then(r => r || { chapter: ch.n, fixes: [] })
))

return { chapters: results.filter(Boolean) }
