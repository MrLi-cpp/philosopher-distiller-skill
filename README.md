# Philosopher Distiller Skill

为指定哲学家自动构建涵盖**一手原著**与**二手权威研究**的结构化语料库，并输出预训练 / SFT / KD 三种蒸馏格式。

---

## 这是什么

一个 OpenClaw AgentSkill，覆盖从数据源检索、文本抓取、学术清洗、观点冲突检测到最终格式化的完整 pipeline。支持中文/英文/双语哲学语料，自动标注来源类型（一手/二手）与权威等级（Tier 0~3）。

**适用场景：**
- 为大模型训练构建哲学家专用预训练语料
- 生成带观点分层的 SFT 对话数据集
- 构造知识蒸馏所需的 (问题, 教师回答, 上下文) 三元组

---

## 安装

### 方式一：导入 .skill 文件（推荐）

```bash
# 下载 .skill 打包文件
wget https://github.com/MrLi-cpp/philosopher-distiller-skill/raw/main/philosopher-distiller.skill

# 导入到 OpenClaw
openclaw skill install philosopher-distiller.skill
```

### 方式二：手动复制

将本仓库复制到 OpenClaw skills 目录：

```bash
cp -r philosopher-distiller ~/.kimi_openclaw/workspace/skills/
```

---

## 使用方法

### 第 1 步：触发 Skill

在对话中提供哲学家姓名、目标语言、蒸馏目标，Skill 自动触发：

> "帮我构建尼采的哲学语料库，语言用英文，蒸馏目标是 SFT 监督微调"

触发词包括：哲学家语料、哲学数据集、知识蒸馏、philosopher corpus、构建哲学家语料库、SFT 数据集、预训练数据准备、哲学大模型训练数据。

### 第 2 步：确认参数

Agent 会复述你的输入并确认哲学家姓名的标准写法，例如：

| 参数 | 你的输入 |
|------|---------|
| philosopher | Nietzsche |
| language | en |
| distill_target | sft |
| max_books | 10（默认） |
| max_secondary | 15（默认） |
| secondary_weight | 0.3（默认） |

你可以随时调整参数。

### 第 3 步：数据源检索（Phase 1）

Agent 自动检索：
- **一手原著**：Project Gutenberg、Wikisource、Perseus、ctext.org、古诗文网等
- **二手研究**：
  - **Tier 1**：SEP（斯坦福哲学百科）、Routledge、IEP
  - **Tier 2**：PhilPapers OA、JSTOR OA、Google Scholar、大学 OCW 讲义
  - **Tier 3**：Philosophy Now、Aeon 等通俗文章（仅作补充）

检索完成后列出所有可获取资源，你可以选择确认或让 Agent 自动选取前 N 条。

### 第 4 步：自动抓取（Phase 2）

Agent 按以下策略抓取：
- 静态 HTML/TXT → HTTP 直取
- 分页目录 → BeautifulSoup 爬虫
- 反爬严格站点（SEP/ctext）→ Playwright 浏览器模拟
- PDF → pdfplumber / PyMuPDF
- API → Gutendex、PhilPapers API

**限速规则：**
- 静态站点 ≥ 2 秒/请求
- 学术平台（SEP/JSTOR/PhilPapers）≥ 5 秒/请求

### 第 5 步：数据清洗（Phase 3）

**一手文献清洗：**
- 去除页眉页脚、脚注标记、Gutenberg 法律声明
- 合并断行、文本规范化
- SimHash 模糊去重 + 困惑度过滤

**二手文献清洗：**
- 去除参考文献列表、文内引用标记、DOI/URL
- 提取核心论点句（argue that / claim that / 我认为...）
- 标注观点持有者（学者姓名）
- 区分"客观描述" vs "主观评价"
- 构建一手引用映射（如 "Republic 514a"）

### 第 6 步：冲突检测（Phase 3.5）

对二手文献进行主题聚类，识别同一哲学概念的不同解读方向：
- 提取含 however / in contrast / 反驳 等转折词的段落
- 为每位学者建立立场档案
- **不消除冲突**，用 `[争议观点]` 标注保留学术张力

### 第 7 步：蒸馏格式化（Phase 4）

根据 `distill_target` 输出对应格式：

**Pretrain（继续预训练）：**
```jsonl
{"text": "...", "source_type": "primary", "authority_tier": 0, "book": "The Republic"}
{"text": "...", "source_type": "secondary", "authority_tier": 1, "author": "Julia Annas"}
```

**SFT（监督微调）：**
```jsonl
{"messages": [
  {"role": "system", "content": "你是一位精通柏拉图哲学的AI助手..."},
  {"role": "user", "content": "请解释洞穴寓言中'太阳'象征什么？"},
  {"role": "assistant", "content": "[柏拉图本人观点] ...\n\n[学者解读: Julia Annas] ...\n\n[争议观点] ..."}
]}
```

**KD（知识蒸馏）：**
```jsonl
{
  "question": "尼采的'权力意志'与叔本华的'生存意志'有何区别？",
  "context_primary": "...",
  "context_secondary": "...",
  "teacher_answer": "...",
  "source_coverage": {"primary": [...], "secondary_tier1": [...]}
}
```

### 第 8 步：质量验收（Phase 5）

生成 `report.md` 报告，包含：
- 一手/二手文献完整清单
- 清洗统计（段落数、去重率、乱码率）
- 观点冲突摘要（主题、涉及学者、对立立场）
- 数据集构成（样本数、一手/二手占比、平均长度）
- 样本预览（每种格式各 1~3 条）
- 版权合规说明与改进建议

---

## 输出目录结构

```
philosopher_corpus/{哲学家姓名}/
├── raw_corpus/
│   ├── primary/              # 一手原著原始文本
│   └── secondary/
│       ├── tier1/            # SEP、Routledge 等
│       ├── tier2/            # OA 论文、专著章节
│       └── tier3/            # 通俗文章
├── cleaned_corpus/
│   ├── primary/              # 清洗后一手纯文本
│   └── secondary/            # 清洗后二手文本（含观点标注）
├── distill_ready/            # 最终蒸馏数据集
├── logs/                     # 抓取与清洗日志
└── report.md                 # 处理报告
```

---

## 权威等级体系

| 等级 | 类型 | 说明 |
|------|------|------|
| **Tier 0** | 一手原著 | 哲学家本人著作、书信、手稿 |
| **Tier 1** | 最高权威 | SEP、Routledge、IEP 同行评审资源 |
| **Tier 2** | 高权威 | OA 论文、学术专著、OCW 讲义 |
| **Tier 3** | 中等权威 | 通俗杂志、书评、博客（仅作补充） |

---

## 核心约束

1. **版权合规** — 仅抓取公版/开放获取（CC0/CC-BY/OA）；SEP 为 CC BY-NC-ND，**不可商用**
2. **学术限速** — SEP/PhilPapers/JSTOR 请求间隔 ≥ 5 秒，避免触发封禁
3. **禁止编造** — SFT/KD 中所有学者姓名、著作、页码必须有清洗后文本依据
4. **保留冲突** — 不消除二手文献中的对立观点，用 `[争议观点]` 标注
5. **来源标注** — 每个样本保留 `source_type`（primary/secondary）与 `authority_tier`

---

## 辅助脚本

```bash
# 一键初始化项目目录
python scripts/init_project.py Nietzsche ./philosopher_corpus/Nietzsche/
```

---

## 示例对话

**用户：** "帮我构建庄子的哲学语料库，中文，蒸馏目标是预训练"

**Agent 确认：**
> 确认参数：
> - 哲学家：庄子（Chuang Tzu / Zhuangzi）
> - 语言：zh（中文）
> - 蒸馏目标：pretrain
> - 默认抓取 10 本一手原著 + 15 篇二手研究，二手权重 0.3
> 
> 开始 Phase 1 数据源检索...

**Agent 执行（自动，无需干预）：**
> Phase 1 ✅ 找到 8 本一手原著 + 12 篇二手研究
> Phase 2 ✅ 抓取完成（raw_corpus/ 已生成）
> Phase 3 ✅ 清洗完成（cleaned_corpus/ 已生成）
> Phase 3.5 ✅ 检测到 5 处观点冲突
> Phase 4 ✅ 格式化完成（distill_ready/ 已生成）
> Phase 5 ✅ 报告已生成：report.md

**Agent 交付：**
> 数据集已准备就绪！
> - 一手语料：庄子原著（内篇/外篇/杂篇）+ 郭象注
> - 二手语料：Tier 1 学术论文 + Tier 2 专著章节
> - 冲突标注：5 处（如"逍遥游主旨"的不同解读）
> - 输出路径：`./philosopher_corpus/庄子/distill_ready/`
> 
> 请查看 `report.md` 了解完整详情，或告诉我需要调整什么。

---

## License

Skill 本身按 MIT 协议分发。注意：**抓取的数据受各自源站版权协议约束**，SEP 数据为 CC BY-NC-ND，不可用于商业用途。
