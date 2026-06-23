export const meta = {
  name: 'floorplan-oa-figsearch',
  description: 'Per pictorial slide, search open repositories for openly-licensed (CC0/CC-BY/CC-BY-SA/PD) strongly-relevant figures; verify license on the source page; return candidates',
  phases: [{ title: 'OA search', detail: 'one agent per slide-topic: search + verify license' }],
}

// 仅搜「开放许可」真图（CC0 / CC-BY / CC-BY-SA / 公有领域），可带署名再分发；不碰厂商/教材版权图。
// 已完成：2.1（CC0 die shot）、3.3（CC BY-SA wire-bond）。本次覆盖其余 pictorial 页。
const TOPICS = [
  { slide: '1.1 物理骨架 / floorplan 总览', concept: '一张真实芯片的版图 / floorplan 总览（die + 功能块），让读者看清"骨架"长什么样', q: 'annotated chip die floorplan layout labelled blocks' },
  { slide: '2.2 利用率与拥塞', concept: '布局密度 / 布线拥塞可视化（congestion / density map），或标准单元布满核心区的版图', q: 'VLSI placement congestion map utilization density standard cell layout' },
  { slide: '2.4 硬宏摆放', concept: '真实芯片上 SRAM / 存储宏块沿边缘 / 角落摆放、标准单元区留大矩形', q: 'SoC floorplan memory macros SRAM blocks placement die shot cache' },
  { slide: '2.6 布局阻挡与留边 halo', concept: 'placement blockage / keepout / halo 的版图或示意（真实工具截图或开放示意）', q: 'placement blockage keepout halo macro padding floorplan' },
  { slide: '4.1 电源规划 PDN / 电源网格', concept: '电源分布网络（power grid / mesh / ring / stripe）的真实版图或开放示意', q: 'power distribution network power grid mesh ring stripe layout IC' },
  { slide: '4.2 IR 压降', concept: 'IR 压降 / 电压降颜色图（voltage drop / IR drop color map）', q: 'IR drop voltage drop power grid color map heatmap analysis' },
  { slide: '4.7 电源网格与宏 / IR 热点', concept: '带宏单元的电源网格 + IR 热点（hotspot）颜色图', q: 'power grid macro IR drop hotspot floorplan thermal map' },
]

const SCHEMA = {
  type: 'object',
  properties: {
    slide: { type: 'string' },
    candidates: {
      type: 'array',
      description: '仅列开放许可且已在来源页核验的候选；没有合适的就留空',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string', description: '图片标题 / 文件名' },
          shows: { type: 'string', description: '这张图具体画了什么（用于判断强相关性）' },
          source_page_url: { type: 'string', description: 'Wikimedia Commons / Openverse / OA 论文等的来源页 URL' },
          direct_image_url: { type: 'string', description: '可直接下载的图片文件 URL（如 upload.wikimedia.org/...），找不到就留空' },
          license: { type: 'string', description: '已核验的许可：CC0 / CC BY 4.0 / CC BY-SA 4.0 / Public Domain / 其它；不确定写 unknown' },
          license_verified: { type: 'boolean', description: '是否已 WebFetch 来源页确认许可（true 才可信）' },
          author: { type: 'string', description: '作者 / 署名要求' },
          relevance: { type: 'string', enum: ['high', 'medium', 'low'], description: '与该页概念的相关度' },
          why: { type: 'string', description: '为何相关 / 不相关的一句话' },
        },
        required: ['title', 'shows', 'source_page_url', 'license', 'license_verified', 'relevance'],
      },
    },
    note: { type: 'string', description: '若开放许可的强相关图稀缺，如实说明' },
  },
  required: ['slide', 'candidates', 'note'],
}

phase('OA search')

const PRELUDE = `你是图片版权与检索助手，为一套 IC 后端（Floorplan）教学幻灯片找**开放许可**的强相关真实插图。

硬规则：
- **只接受开放许可**：CC0、CC BY、CC BY-SA、Public Domain（公有领域）。**绝不**用厂商（Cadence/Synopsys）、教材、付费期刊等版权图。
- **必须核验许可**：对每个候选，用 WebFetch 打开其来源页（优先 Wikimedia Commons 的 File: 页），确认许可文字，并尽量取到直接图片 URL（upload.wikimedia.org/...）。license_verified 只有在你真的核验过才填 true。
- **强相关优先**：图要真的画了该页的概念；宁缺毋滥，相关度低就标 low 或不返回。
- 来源优先级：Wikimedia Commons（commons.wikimedia.org，许可清晰）> Openverse（openverse.org）> 明确 CC 许可的开放获取论文插图（PMC / MDPI / arXiv 注意多数 arXiv 图并非 CC，要看具体许可）。

工具：用 ToolSearch 加载 WebSearch 与 WebFetch（query: "select:WebSearch,WebFetch"），再用它们检索与核验。

只负责下面这一页，返回 0–3 个**已核验**的开放许可候选（按相关度排序）。`

const results = await parallel(TOPICS.map(t => () =>
  agent(
    `${PRELUDE}

【页面】${t.slide}
【需要表达的概念】${t.concept}
【检索词起点（可自行调整 / 多试几个）】${t.q}

步骤：WebSearch 找候选 → 对每个像样的候选 WebFetch 其来源页核验许可与作者、取直接图片 URL → 只返回开放许可（CC0/CC-BY/CC-BY-SA/PD）且强相关的。若确实找不到合适的开放图，candidates 留空并在 note 说明。`,
    { label: `oa:${t.slide.slice(0, 6)}`, phase: 'OA search', schema: SCHEMA }
  ).then(r => r || { slide: t.slide, candidates: [], note: 'agent returned null' })
))

return { results: results.filter(Boolean) }
