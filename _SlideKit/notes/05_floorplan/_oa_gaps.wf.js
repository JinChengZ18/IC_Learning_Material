export const meta = {
  name: 'floorplan-oa-gaps',
  description: 'Fill remaining OA-figure gaps: 2.6 halo/blockage, 4.7 IR-on-layout, 4.1 power-ring/stripe, 4.3 electromigration, 3.3 flip-chip — openly-licensed only, verified + DOI',
  phases: [{ title: 'Gaps', detail: 'per gap topic: broad OA search + verify' }],
}

const TOPICS = [
  { slide: '2.6 阻挡 / 留边 halo', concept: 'placement blockage / keepout / halo（宏外围留边、软/硬阻挡区）的真实版图或开放示意', extra: 'CC-BY 论文里 floorplan with blockages/halo；可放宽到 medium 相关' },
  { slide: '4.7 电源网格 + 宏 / IR 热点', concept: '版图上叠加 IR drop 热点（hotspot）颜色图，最好带电源网格条带', extra: 'CC-BY 论文(MDPI/IEEE-Access/Frontiers/CC arXiv)里的 IR-drop-on-layout heatmap；OpenROAD 是 BSD 不收' },
  { slide: '4.1 电源环 / 条带 / 网格（PDN 第二图）', concept: '电源环 power ring / 条带 stripe / 网格 mesh 的真实版图或开放示意（与 Bitfury 顶层金属互补）', extra: 'CC-BY 论文的 PDN ring/stripe 图；Commons 电源布线' },
  { slide: '4.3 电迁移 EM', concept: '电迁移失效真实显微照：空洞 void / 晶须 whisker / 金属线断裂', extra: 'PMC Micromachines EM 综述(DOI 10.3390/mi13060883, CC BY 4.0)、Commons EM 照片' },
  { slide: '3.3 倒装焊 / 凸点（封装第二图）', concept: 'flip-chip / C4 solder bump / BGA 封装剖面或凸点阵列（与 wire-bond 互补）', extra: 'Commons flip chip / C4 bump / BGA cross-section' },
]

const SCHEMA = {
  type: 'object',
  properties: {
    slide: { type: 'string' },
    candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          caption_cn: { type: 'string', description: '中文图注，≤24 字' },
          source_page_url: { type: 'string' },
          direct_image_url: { type: 'string', description: '可直接下载的图片 URL' },
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
  required: ['slide', 'candidates', 'note'],
}

phase('Gaps')

const PRELUDE = `你是图片版权与检索助手，为 IC 后端（Floorplan）教学幻灯片找**开放许可**真图。
硬规则：只接受 CC0 / CC BY / CC BY-SA / Public Domain；论文必须整篇 CC（看 license 声明，arXiv 默认 nonexclusive 不算，逐篇核）；不用厂商/教材/付费/BSD/GPL 图。必须 WebFetch 来源页核验许可、作者、（论文）DOI，并尽量确认图片 URL 可取（fetchable）。优先 Wikimedia Commons（upload.wikimedia.org）+ CC-BY 论文（带 DOI；MDPI 站点常 403 取不到，如此则 fetchable=false）。
工具：ToolSearch 加载 WebSearch + WebFetch（query: "select:WebSearch,WebFetch"）。多换检索词。返回 1–3 个已核验候选；找不到就如实说明。`

const results = await parallel(TOPICS.map(t => () =>
  agent(`${PRELUDE}\n\n【页面】${t.slide}\n【需要表达】${t.concept}\n【线索】${t.extra}\n\n返回已核验开放许可且相关的候选（每个带中文图注 + DOI若论文）。`,
    { label: `gap:${t.slide.slice(0, 6)}`, phase: 'Gaps', schema: SCHEMA }
  ).then(r => r || { slide: t.slide, candidates: [], note: 'null' })
))

return { results: results.filter(Boolean) }
