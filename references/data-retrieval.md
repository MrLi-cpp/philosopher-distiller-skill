# Phase 1: 数据源检索策略

覆盖一手原著与二手权威研究两大维度。

## 1.1 一手原著（Primary Sources）

**西方哲学：**
- **Project Gutenberg** (gutenberg.org) — 公版书，`.txt`/`.html`/`.epub`
- **Wikisource** (wikisource.org) — 多语言经典文献，CC 协议
- **Perseus Digital Library** (perseus.tufts.edu) — 古希腊/罗马原著及英译
- **Internet Archive** (archive.org) — 扫描版 PDF（需 OCR）
- **Open Library** (openlibrary.org) — 借阅与开放获取

**中国哲学：**
- **中国哲学书电子化计划 (ctext.org)** — 先秦至历代原著，反爬严格
- **古诗文网 (so.gushiwen.cn/guwen/)** — 古籍原文+译文
- **书格 (shuge.org)** — 古籍扫描资源
- **维基文库 (zh.wikisource.org)** — 开放协议

**检索方法：**
- Gutenberg API: `https://gutendex.com/books/?search={philosopher}`
- 通用搜索: `site:gutenberg.org {philosopher}`

## 1.2 二手权威研究（Secondary Sources）

### Tier 1 — 最高权威

- **Stanford Encyclopedia of Philosophy (SEP)** (plato.stanford.edu) — 同行评审，动态更新
- **Routledge Encyclopedia of Philosophy** — 学术标准条目
- **Internet Encyclopedia of Philosophy (IEP)** (iep.utm.edu) — 学术质量，开放获取
- **Stanford Encyclopedia of Philosophy (Chinese)** — 部分条目有中文翻译

### Tier 2 — 高权威

- **Internet Archive Scholar** / **JSTOR Open Content** — 开放获取学术专著章节
- **PhilPapers** (philpapers.org) — 哲学论文索引，筛选 OA 论文
- **Google Scholar** — 检索 `{philosopher} "interpretation" OR "commentary" OR "system" filetype:pdf`
- **Academia.edu / ResearchGate** — 学者上传的开放获取章节
- **大学课程讲义（OCW）** — MIT OpenCourseWare、Yale Open Courses 等

### Tier 3 — 中等权威（仅作补充）

- **Philosophy Now** (philosophynow.org) — 通俗哲学杂志
- **Aeon / Psyche** — 哲学思想长文
- **权威学者博客/专栏** — 3QuarksDaily 等

**检索方法：**
- SEP 站内搜索: `site:plato.stanford.edu {philosopher}`
- PhilPapers API: `https://philpapers.org/browse/{philosopher}`，筛选 `open_access=1`
- Google Scholar: `allintitle: {philosopher} commentary OR interpretation OR system`
- JSTOR 开放获取: `https://www.jstor.org/open/` + 哲学家关键词
- 中文资源: 知网（CNKI）开放获取论文、万方、百度学术

## 1.3 检索输出格式

对每个找到的著作/研究，记录：

```json
{
  "title": "Plato's Ethics: An Overview",
  "author": "Julia Annas",
  "source": "Stanford Encyclopedia of Philosophy",
  "url": "https://plato.stanford.edu/entries/plato-ethics/",
  "format": "html",
  "language": "en",
  "license": "open_access",
  "source_type": "secondary",
  "authority_tier": 1,
  "estimated_size_kb": 120,
  "description": "对柏拉图伦理学的系统性学术综述"
}
```

## 1.4 降级策略

若主要源失败，自动降级到次级源：
- SEP 不可达 → IEP → 维基百科（Tier 3，标注）
- JSTOR OA 不可达 → Internet Archive Scholar → Google Scholar 预印本
- ctext 反爬 → 古诗文网 → 书格扫描版
