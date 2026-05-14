# Phase 2: 自动抓取策略

## 2.1 技术选型矩阵

| 数据源类型 | 技术方案 | 工具库 |
|-----------|---------|--------|
| 静态 HTML/TXT | HTTP 直取 | `requests`, `httpx` |
| 分页目录+章节 | 爬虫框架 | `Scrapy` / `requests + BeautifulSoup` |
| 动态渲染/反爬 | 浏览器模拟 | `Playwright` |
| PDF/EPUB | 文档解析 | `pdfplumber`, `PyMuPDF`, `ebooklib` |
| API 接口 | REST 调用 | `requests` |

## 2.2 一手文献抓取规范

- **请求间隔**：静态站点 ≥ 2 秒，反爬严格站点 ≥ 5-10 秒
- **User-Agent**：轮换常见浏览器 UA
- **失败重试**：3 次指数退避（1s, 2s, 4s）
- **断点续传**：记录已下载书目，支持中断恢复
- **版权过滤**：仅抓取 `public_domain` / `CC0` / `CC-BY` 内容

## 2.3 二手文献抓取规范

- **学术资源限速**：SEP、JSTOR、PhilPapers 间隔 ≥ 5 秒
- **PDF 元数据提取**：标题、作者、出版年份、DOI
- **引用关系记录**：提取二手文献中对一手原著的引用上下文
- **分层抓取策略**：
  1. 优先 Tier 1（SEP、Routledge）完整 HTML
  2. 其次 Tier 2（OA 论文、专著章节）PDF 全文
  3. 最后 Tier 3（通俗文章）补充
- **中文二手文献**：知网/万方优先 OA 论文；豆瓣/知乎仅 Tier 3

## 2.4 原始数据存储结构

```
{output_dir}/
├── raw_corpus/
│   ├── primary/
│   │   ├── book_001_the_republic/
│   │   │   ├── metadata.json
│   │   │   ├── raw.txt
│   │   │   └── source_url.txt
│   │   └── ...
│   └── secondary/
│       ├── tier1_sep_plato_ethics/
│       │   ├── metadata.json
│       │   ├── raw.html
│       │   └── source_url.txt
│       ├── tier2_jstor_annas_plato/
│       │   ├── metadata.json
│       │   ├── raw.pdf
│       │   └── source_url.txt
│       └── ...
└── logs/
    ├── primary_fetch_log.jsonl
    └── secondary_fetch_log.jsonl
```

## 2.5 核心模块接口

```python
class PrimarySourceFinder:
    def search_gutenberg(self, philosopher: str) -> List[BookMeta]: ...
    def search_wikisource(self, philosopher: str) -> List[BookMeta]: ...
    def search_ctext(self, philosopher: str) -> List[BookMeta]: ...
    def search_perseus(self, philosopher: str) -> List[BookMeta]: ...

class SecondarySourceFinder:
    def search_sep(self, philosopher: str) -> List[ArticleMeta]: ...
    def search_philpapers_oa(self, philosopher: str) -> List[ArticleMeta]: ...
    def search_google_scholar(self, philosopher: str) -> List[ArticleMeta]: ...
    def search_jstor_oa(self, philosopher: str) -> List[ArticleMeta]: ...
    def search_cnki_oa(self, philosopher: str) -> List[ArticleMeta]: ...  # 中文哲学研究
```
