export const meta = {
  name: 'floorplan-oa-deep',
  description: 'Deeper OA figure hunt per slide: multiple openly-licensed (CC0/CC-BY/CC-BY-SA/PD) figures with DOI, verified license + fetchable image URL + a Chinese caption',
  phases: [{ title: 'Deep OA', detail: 'per slide-topic: broad OA search, verify license + fetchability + DOI' }],
}

// 目标：尽量用真实开放许可图替换程序自绘草图；每页可多张；带图注 + DOI/来源。
// 已用：1.1(486 die)、2.1(i9 die)、3.3(wire-bond)、4.1(Bitfury)、4.2(IR map)。本次补全其余 + 多图。
const TOPICS = [
  { slide: '2.2 利用率与拥塞', concept: '布线拥塞 / 布局密度热力图（congestion / density map），或标准单元布满核心区的真实版图', extra: 'CC-BY 论文里的 congestion/density heatmap 最可能命中（如 routability 预测、placement 论文）' },
  { slide: '2.4 硬宏摆放', concept: '真实 SoC / 处理器版图上存储宏（SRAM/cache）沿边缘摆放、标准单元区留大矩形', extra: 'die shot 中 cache 阵列清晰者；或 CC-BY 论文里的 macro floorplan 图' },
  { slide: '2.6 布局阻挡与留边 halo', concept: 'placement blockage / keepout / halo（宏外围留边、软/硬阻挡区）的版图或示意', extra: 'CC-BY 论文里的 floorplan with blockages/halo 图最可能；Commons 很少' },
  { slide: '3.2 时序预算与层次化', concept: '层次化 / 分区 floorplan（partition、block 边界、ILM）或 timing budget 示意', extra: 'CC-BY 论文里的 hierarchical floorplan / partitioned chip 图' },
  { slide: '4.7 电源网格与宏 / IR 热点', concept: '带电源网格条带的版图上叠加 IR drop 热点（hotspot）颜色图', extra: 'CC-BY 论文里的 IR-drop-on-layout / PDN heatmap；OpenROAD 图为 BSD(非 CC) 不收' },
  { slide: '通用·标准单元行 / 版图微观', concept: '标准单元行（standard-cell rows）显微照片，或一小块真实版图（金属布线层）', extra: 'Commons 有 die / metal layer 微距照；用于 2.x / 通用配图' },
  { slide: '通用·电源环条带 / wafer', concept: '电源环 power ring / 条带的真实版图，或晶圆 wafer / 封装剖面（补充 PDN / 几何页）', extra: 'Commons wafer/package；CC-BY 论文 PDN ring/stripe' },
]

const SCHEMA = {
  type: 'object',
  properties: {
    slide: { type: 'string' },
    candidates: {
      type: 'array',
      description: '0–4 个**已核验开放许可**的候选，按相关度排序；可多张供一页使用',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          caption_cn: { type: 'string', description: '建议的中文图注（这张图画了什么，一句话，≤24 字）' },
          source_page_url: { type: 'string', description: '论文页 / Wikimedia File 页 / PMC 页' },
          direct_image_url: { type: 'string', description: '可直接下载的图片 URL（upload.wikimedia.org / arxiv.org/html/.. / PMC 图 URL）' },
          fetchable: { type: 'boolean', description: '是否确认该图片 URL 能取到图片（WebFetch 不 403/不重定向走丢）' },
          license: { type: 'string', description: 'CC0 / CC BY 4.0 / CC BY-SA 4.0 / Public Domain / 其它（非开放则别列）' },
          license_verified: { type: 'boolean' },
          doi: { type: 'string', description: '论文来源的 DOI（如 10.3390/...），Commons/无 DOI 则留空' },
          author: { type: 'string', description: '作者 / 署名要求' },
          relevance: { type: 'string', enum: ['high', 'medium', 'low'] },
          why: { type: 'string' },
        },
        required: ['title', 'caption_cn', 'source_page_url', 'license', 'license_verified', 'relevance'],
      },
    },
    note: { type: 'string', description: '覆盖情况 / 取舍 / 哪些 fetch 不到' },
  },
  required: ['slide', 'candidates', 'note'],
}

phase('Deep OA')

const PRELUDE = `你是图片版权与检索助手，为 IC 后端（Floorplan）教学幻灯片找**开放许可**的真实插图，用来替换程序自绘的示意草图。

硬规则：
- **只接受开放许可**：CC0、CC BY、CC BY-SA、Public Domain。论文图必须整篇是 CC（看 license 声明）才可用其图；**arXiv 默认 non-exclusive 不是 CC**，要逐篇看具体许可。**不要**用厂商(Cadence/Synopsys)、教材、付费/非 CC 期刊、BSD/GPL 软件仓库的图。
- **必须核验**：用 WebFetch 打开来源页确认许可文字、作者、（论文则）DOI；并尽量确认 direct_image_url 能取到图（fetchable）。license_verified / fetchable 只有真核验过才填 true。
- **优先可取的源**：Wikimedia Commons（upload.wikimedia.org，许可清晰）、CC-BY 开放获取论文（MDPI / PMC / Frontiers / IEEE Access / Hindawi 等，带 DOI；注意部分站点会 403，取不到就如实标 fetchable=false）、Openverse。
- **强相关 + 可多张**：本页可用多张图，尽量给 2–4 个高相关候选；每个给一句中文图注 caption_cn。

工具：用 ToolSearch 加载 WebSearch + WebFetch（query: "select:WebSearch,WebFetch"）。

只负责下面这一页/主题。`

const results = await parallel(TOPICS.map(t => () =>
  agent(
    `${PRELUDE}

【页面/主题】${t.slide}
【需要表达】${t.concept}
【线索】${t.extra}

多换几组检索词，覆盖 Wikimedia + CC-BY 论文（带 DOI）+ Openverse。对每个像样候选 WebFetch 来源页核验许可/作者/DOI、确认图片可取。返回 0–4 个**已核验开放许可**且强相关的候选（多张优先），每个带中文图注与 DOI（若论文）。找不到就如实在 note 说明。`,
    { label: `oa2:${t.slide.slice(0, 7)}`, phase: 'Deep OA', schema: SCHEMA }
  ).then(r => r || { slide: t.slide, candidates: [], note: 'null' })
))

return { results: results.filter(Boolean) }
