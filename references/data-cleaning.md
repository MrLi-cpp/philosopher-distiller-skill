# Phase 3: 数据清洗流水线

## 3.1 一手文献清洗

- 去除页眉/页脚/页码、脚注标记、章节编号、出版信息、Gutenberg 法律声明
- 文本规范化、合并断行、去除过短句子
- 精确去重 + 模糊去重（SimHash）
- 困惑度(PPL)过滤 + 规则过滤（乱码、符号密度）

## 3.2 二手文献专用清洗

学术文本噪声模式与原著不同，需额外处理：

### Step 1: 学术格式噪声去除

- **参考文献列表**：识别并去除文末 `References` / `Bibliography` / `Works Cited` 区块
- **文内引用**：去除 `(Annas 1999, p.45)`、`[1]`、`¹` 等引用标记，保留上下文语义
- **脚注/尾注**：仅保留补充论证内容，删除纯引用出处
- **DOI/URL**：去除文中嵌入的 DOI 链接和超链接
- **作者信息/摘要**：去除论文开头的作者单位、Abstract、Keywords 区块
- **页眉学术标识**：去除期刊名、卷号、页码等

### Step 2: 观点提取与结构化

- **识别核心论点句**：提取含 `argue that`, `claim that`, `contend that`, `maintain that`, `我认为`, `他指出` 的句子
- **标注观点持有者**：记录段落观点属于哪位二手文献作者
- **区分描述与评价**：标注"客观描述" vs "主观评价/批评"

### Step 3: 引用关系清洗

- **提取一手引用**：识别二手文献中对一手原著的引用（如 `Republic 514a`、`《论语·学而》`）
- **构建引用映射**：记录二手文献中的引用指向哪本一手著作的哪个章节
- **上下文保留**：保留引用周围的论证性文字，删除孤立引用列表

### Step 4: 质量与去重

- **学术文本去重**：二手文献间常有重复引用段落，MinHash 去重，阈值 0.80
- **低质量过滤**：去除纯目录、纯索引、纯图表说明的页面
- **语言纯度检测**：确保 > 95% 目标语言字符

## 3.3 清洗输出格式

二手文献额外包含观点标注：

```
[标题]: Plato's Ethics: An Overview
[作者]: Julia Annas
[来源]: Stanford Encyclopedia of Philosophy
[来源类型]: secondary
[权威等级]: 1
[清洗时间]: 2026-05-14
[原始大小]: 120KB
[清洗后大小]: 95KB
[去除引用标记数]: 45
[提取核心论点数]: 12

---正文开始---

[观点持有者: Julia Annas] [观点类型: 学术评价]
Plato's ethics is often interpreted as a form of eudaimonism, but this reading has been challenged...

[观点持有者: 原文引用] [观点类型: 客观描述]
In the Republic, Plato argues that justice is a kind of psychic health...
```

## 3.4 核心模块接口

```python
class PrimaryTextCleaner:
    def remove_headers_footers(self, text: str) -> str: ...
    def normalize_text(self, text: str) -> str: ...
    def deduplicate(self, texts: List[str]) -> List[str]: ...
    def quality_filter(self, text: str) -> bool: ...

class SecondaryTextCleaner:
    def remove_citations(self, text: str) -> Tuple[str, List[Citation]]: ...
    def remove_references(self, text: str) -> str: ...
    def extract_arguments(self, text: str) -> List[ArgumentSpan]: ...
    def extract_primary_citations(self, text: str) -> List[PrimaryRef]: ...
    def remove_academic_noise(self, text: str) -> str: ...
```
