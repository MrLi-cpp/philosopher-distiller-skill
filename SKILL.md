---
name: philosopher-distiller
description: 哲学家知识蒸馏与语料构建工作流。当用户需要为一手大模型训练构建某位哲学家的结构化语料库时触发。覆盖从数据源检索、文本抓取、学术清洗、观点冲突检测到预训练/SFT/KD 三种蒸馏格式输出的完整 pipeline。适用于中文/英文/双语哲学语料，支持一手原著与二手权威研究的分层标注。触发词包括：哲学家语料、哲学数据集、知识蒸馏、philosopher corpus、构建哲学家语料库、SFT 数据集、预训练数据准备、哲学大模型训练数据。
---

# 哲学家知识蒸馏语料构建工作流

为指定哲学家自动构建涵盖**一手原著**与**二手权威研究**的结构化语料库，并输出预训练/SFT/KD 三种蒸馏格式。

## 快速开始

用户提供：
- `philosopher` — 哲学家姓名（如 "Nietzsche", "庄子"）
- `language` — 目标语言：`zh` / `en` / `bilingual`
- `distill_target` — 蒸馏目标：`pretrain` / `sft` / `kd`

一键执行入口：`main.py`，按 Phase 1→6 顺序运行。

## 核心工作流

| 阶段 | 内容 | 关键产出 | 参考文档 |
|------|------|---------|---------|
| Phase 1 | **数据源检索** — 一手原著 + 二手研究 | 资源清单（含权威等级） | [data-retrieval.md](references/data-retrieval.md) |
| Phase 2 | **自动抓取** — 多策略文本获取 | `raw_corpus/` | [data-fetching.md](references/data-fetching.md) |
| Phase 3 | **数据清洗** — 噪声去除 + 观点提取 | `cleaned_corpus/` | [data-cleaning.md](references/data-cleaning.md) |
| Phase 3.5 | **冲突检测** — 保留学术多元性 | 冲突标注映射 | [conflict-detection.md](references/conflict-detection.md) |
| Phase 4 | **蒸馏格式化** — Pretrain/SFT/KD | `distill_ready/` | [data-formatting.md](references/data-formatting.md) |
| Phase 5 | **质量验收** — 指标检查 + 报告 | `report.md` | [quality-standards.md](references/quality-standards.md) |

## 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `philosopher` | string | 是 | — | 哲学家姓名 |
| `language` | string | 是 | — | `zh` / `en` / `bilingual` |
| `distill_target` | string | 是 | — | `pretrain` / `sft` / `kd` |
| `max_books` | int | 否 | 10 | 最多抓取原著数 |
| `max_secondary` | int | 否 | 15 | 最多抓取二手研究数 |
| `secondary_weight` | float | 否 | 0.3 | 二手文献采样权重（0.0-1.0） |
| `output_dir` | string | 否 | `./philosopher_corpus/{philosopher}/` | 输出目录 |

## 项目结构

```
{output_dir}/
├── raw_corpus/
│   ├── primary/          # 一手原著原始文本
│   └── secondary/        # 二手研究原始文本（含 tier1/tier2/tier3）
├── cleaned_corpus/
│   ├── primary/          # 清洗后一手纯文本
│   └── secondary/        # 清洗后二手纯文本（含观点标注）
├── distill_ready/        # 蒸馏-ready 数据集
├── logs/                 # 抓取与清洗日志
└── report.md             # 处理报告
```

## 权威等级体系

- **Tier 0**: 一手原著（哲学家本人著作）
- **Tier 1**: 最高权威 — SEP、Routledge、IEP 等同行评审资源
- **Tier 2**: 高权威 — OA 论文、学术专著章节、OCW 讲义
- **Tier 3**: 中等权威 — 通俗杂志、书评、博客（仅作补充）

## 关键约束

1. **版权合规** — 仅抓取公版/开放获取（CC0/CC-BY/OA）内容；SEP 为 CC BY-NC-ND，不可商用
2. **学术限速** — SEP/PhilPapers/JSTOR 请求间隔 ≥ 5 秒
3. **禁止编造** — SFT/KD 中所有学者姓名、著作、页码必须在清洗文本中有依据
4. **保留冲突** — 不消除二手文献中的对立观点，用 `[争议观点]` 标注
5. **来源标注** — 每个样本保留 `source_type`（primary/secondary）与 `authority_tier`

## 执行顺序

1. 复述并确认用户输入的哲学家标准写法
2. 执行 Phase 1，列出可获取资源，让用户确认或自动选取前 N 条
3. 串行执行 Phase 2→3→3.5→4，生成 `distill_ready/`
4. 执行 Phase 5，输出 `report.md`
5. 交付最终数据集路径与格式说明

## 辅助脚本

- `scripts/init_project.py` — 一键创建项目目录结构
- 用法：`python scripts/init_project.py {philosopher} {output_dir}`
