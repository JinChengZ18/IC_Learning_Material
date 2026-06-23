export const meta = {
  name: 'floorplan-oa-pdn',
  description: 'Deep search for an openly-licensed power ring/stripe/mesh figure for slide 4.1 (PDN second figure)',
  phases: [{ title: 'PDN', detail: 'broad OA search for power-grid geometry figure' }],
}

const SCHEMA = {
  type: 'object',
  properties: {
    candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          caption_cn: { type: 'string' },
          source_page_url: { type: 'string' },
          direct_image_url: { type: 'string' },
          fetchable: { type: 'boolean' },
          license: { type: 'string' },
          license_verified: { type: 'boolean' },
          doi: { type: 'string' },
          author: { type: 'string' },
          relevance: { type: 'string', enum: ['high', 'medium', 'low'] },
          why: { type: 'string' },
        },
        required: ['title', 'caption_cn', 'source_page_url', 'license', 'license_verified', 'relevance'],
      },
    },
    note: { type: 'string' },
  },
  required: ['candidates', 'note'],
}

phase('PDN')

const PRELUDE = `你是图片版权与检索助手，为 IC 后端幻灯片 4.1「电源规划」找**开放许可**的真实「电源环 power ring / 条带 stripe / 网格 mesh」版图或剖面图，与已有的 Bitfury 顶层金属实拍互补。
硬规则：只接受 CC0 / CC BY / CC BY-SA / Public Domain（论文必须整篇 CC，arXiv 默认 nonexclusive 不算，逐篇核 license；不收厂商/教材/付费/BSD）。必须 WebFetch 来源页核验许可、作者、DOI，并尽量确认图片 URL 可取。
多换检索词（power grid stripe mesh layout / on-chip power distribution network cross section / C4 bump power grid / redistribution layer power）。优先 Wikimedia Commons + CC-BY 论文(MDPI/PMC/Frontiers/IEEE-Access/EDP Sciences 带 DOI)。工具：ToolSearch 加载 WebSearch + WebFetch。返回 0–3 个已核验候选；找不到就如实说明。`

const r = await agent(PRELUDE, { label: 'oa:pdn', phase: 'PDN', schema: SCHEMA })
return r || { candidates: [], note: 'null' }
