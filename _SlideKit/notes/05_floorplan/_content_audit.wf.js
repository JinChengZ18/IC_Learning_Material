export const meta = {
  name: 'floorplan-content-audit',
  description: 'Per-chapter, compare the Floorplan deck slides against the source note; flag over-trimmed slides + sparse tables and return note-faithful enrichments',
  phases: [{ title: 'Audit', detail: 'one agent per chapter: note↔slide diff' }],
}

const NOTE = 'D:/Documents/IC/IC_Learning_Material/IC_Backend_Notes/05_Floorplan.md'
const SLIDES = 'D:/Documents/IC/IC_Learning_Material/_SlideKit/notes/05_floorplan/slides.py'

const CHAPTERS = [
  { n: '1', title: '认识 Floorplan', subs: '1.1–1.5' },
  { n: '2', title: '几何：die / core / IO / 宏 / 通道', subs: '2.1–2.7' },
  { n: '3', title: '层次化 Hierarchical', subs: '3.1–3.3' },
  { n: '4', title: '电源规划 Power / PG', subs: '4.1–4.7' },
  { n: '5', title: '工具流程与调试收束', subs: '5.1–5.2' },
]

const SCHEMA = {
  type: 'object',
  properties: {
    chapter: { type: 'string' },
    slides: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          slide: { type: 'string', description: 'slide title as in slides.py, e.g. "1.4 全芯片设计视角"' },
          kind: { type: 'string', description: 'split / table / bullets / cols2 / cards2 / section' },
          verdict: { type: 'string', enum: ['ok', 'over_trimmed', 'table_sparse', 'both'] },
          note_points_missing: {
            type: 'array', items: { type: 'string' },
            description: 'concrete points/numbers/terms present in the NOTE for this subsection but absent from the slide (for self-study). Empty if ok.',
          },
          suggested_bullets: {
            type: 'array', items: { type: 'string' },
            description: 'if over_trimmed: the FULL replacement bullet/prose list (complete sentences, note-faithful, no invented facts). 4–7 items for split; keep each ≤ ~40 CJK chars. Empty if no change.',
          },
          suggested_style: { type: 'string', enum: ['bullet', 'num', 'prose', ''], description: 'style for suggested_bullets, or "" if unchanged' },
          suggested_table: {
            type: 'object',
            properties: {
              headers: { type: 'array', items: { type: 'string' } },
              rows: { type: 'array', items: { type: 'array', items: { type: 'string' } } },
            },
            description: 'if table_sparse: a richer table (more columns/rows from the note) to better use the space. Omit if not a table.',
          },
          rationale: { type: 'string', description: 'one line: why this verdict' },
        },
        required: ['slide', 'kind', 'verdict', 'rationale'],
      },
    },
  },
  required: ['chapter', 'slides'],
}

phase('Audit')

const PRELUDE = `你是 IC 后端教学幻灯片的内容审校。任务：把【笔记】与【幻灯片 SPECS】逐小节比对，找出"为了上幻灯片而过度精简、漏掉了利于学生自学的要点"的页，以及"太空、版面利用不足"的表格，给出**忠于笔记**的增补建议。

唯一真源是笔记，**不得自行发明 VLSI 事实**；只把笔记里已有、但幻灯片漏掉的要点补回。要点写成**完整句**（能独立看懂），不要电报式速记。每条 ≤ ~40 个汉字（太长会溢出）。split 页正文区放得下 4–7 条。

先读两份文件：
- 笔记（真源）：${NOTE}
- 幻灯片 SPECS：${SLIDES}

幻灯片助手：split(标题,副标题,图,bullets,style)、tbl(标题,副标题,headers,rows)、section(...)；style 取 bullet(▪并列)/num(①②③有序)/prose(整段叙述)。`

const results = await parallel(CHAPTERS.map(ch => () =>
  agent(
    `${PRELUDE}

只审你负责的【第 ${ch.n} 章 ${ch.title}（小节 ${ch.subs}）】。对该章的**每一张**幻灯片：
1) 在笔记里找到对应小节，列出笔记有、但该页漏掉的具体要点（note_points_missing）。
2) 若该页过度精简（漏了对自学重要的点）→ verdict=over_trimmed，给出 suggested_bullets（整页替换、完整句、忠于笔记）+ suggested_style。
3) 若该页是表格且太空/列太少/利用不足 → verdict=table_sparse（或 both），给出 suggested_table（用笔记里的内容增列/增行，把空间用起来）。
4) 内容与笔记基本相称 → verdict=ok。
返回该章所有页的审校结果。`,
    { label: `audit:ch${ch.n}`, phase: 'Audit', schema: SCHEMA }
  ).then(r => r || { chapter: ch.n, slides: [] })
))

return { chapters: results.filter(Boolean) }
