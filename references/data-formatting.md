# Phase 4: 蒸馏数据格式化

根据 `distill_target` 参数，将一手与二手语料转换为对应格式，并明确标注来源类型与权威等级。

## 4.1 Pretrain（继续预训练）

**目标**：让模型同时学习哲学家的语言风格与学术讨论语境。

**格式**：JSON Lines，每行一个样本

```jsonl
{"text": "柏拉图在《理想国》中提出了洞穴寓言。他认为，人类如同被锁在洞穴中的囚徒...", "source_type": "primary", "authority_tier": 0, "book": "The Republic"}
{"text": "Julia Annas argues that Plato's ethics should be understood as a form of eudaimonism that prioritizes...", "source_type": "secondary", "authority_tier": 1, "author": "Julia Annas", "work": "SEP: Plato's Ethics"}
```

**处理要求**：
- 按自然段落或固定长度（2048 tokens）切分
- 保留完整句子，不在句中截断
- 一手与二手语料按 `secondary_weight` 比例混合（默认 7:3）
- 多本书/多篇研究合并 shuffle，避免单来源过拟合
- `source_type` 和 `authority_tier` 作为 metadata 保留

## 4.2 SFT（监督微调）

**目标**：让模型能基于哲学家本人思想与权威研究，回答多层次哲学问题。

**格式**：JSON Lines，对话格式

```jsonl
{"messages": [
  {"role": "system", "content": "你是一位精通柏拉图哲学的AI助手。你的回答应综合柏拉图原著与当代权威研究（如Julia Annas, John Cooper等）。回答时需区分'柏拉图本人观点'与'学者的解读'，并在引用二手研究时注明学者姓名。"},
  {"role": "user", "content": "请解释洞穴寓言中'太阳'象征什么？不同学者对此有何分歧？"},
  {"role": "assistant", "content": "在《理想国》第七卷（514a-517a）中，柏拉图通过洞穴寓言描述了认知的上升过程...\n\n[柏拉图本人观点] 柏拉图本人将'太阳'明确类比为'善的理念'（Form of the Good）...\n\n[学者解读: Julia Annas] Annas 在《Plato's Ethics》中进一步指出...\n\n[学者分歧] 然而，Nicholas White 等学者质疑这种解读是否过度形而上学化..."}
]}
```

**处理要求**：
- 基于一手文本构造基础 QA
- 基于二手文本构造深度 QA（学术争议、比较研究、思想演进）
- **观点分层标注**：
  - `[哲学家本人观点]` — 直接来自一手文献
  - `[学者解读: 姓名]` — 来自特定二手文献
  - `[学界共识]` — 多个 Tier 1/2 来源交叉验证
  - `[争议观点]` — 存在明显学术分歧的议题
- **禁止幻觉**：所有学者姓名、著作、页码必须有清洗后文本依据
- **系统提示词动态生成**：根据哲学家自动构建，含主要一手著作列表与 Tier 1 学者名单

## 4.3 KD（知识蒸馏）

**目标**：将大教师模型的哲学推理与学术综述能力迁移到小模型，保留一手/二手信息区分能力。

**格式**：JSON Lines，含教师模型输出与来源标注

```jsonl
{
  "question": "尼采的'权力意志'与叔本华的'生存意志'有何本质区别？学界对此的主要分歧是什么？",
  "context_primary": "尼采在《查拉图斯特拉如是说》中提出权力意志... [来自一手文献]",
  "context_secondary": "Heidegger 在《尼采》中将权力意志解读为存在论概念... Deleuze 则强调其作为力的差异... [来自二手文献]",
  "teacher_answer": "尼采的权力意志（Wille zur Macht）与叔本华的生存意志（Wille zum Leben）存在本质区别...\n\n[一手依据] 尼采在《查拉图斯特拉如是说》中明确区分了...\n\n[二手解读: Heidegger] Heidegger 认为权力意志标志着西方形而上学的完成...\n\n[二手解读: Deleuze] Deleuze 则提出权力意志应理解为'力的差异'...\n\n[学术分歧] 学界主要分歧在于：权力意志是形而上学概念（Heidegger）还是生理学/心理学概念...",
  "distill_type": "black_box",
  "source_coverage": {
    "primary": ["Thus Spoke Zarathustra"],
    "secondary_tier1": ["Heidegger - Nietzsche", "Deleuze - Nietzsche and Philosophy"],
    "secondary_tier2": ["Richardson - Nietzsche's System"]
  }
}
```

**处理要求**：
- **黑盒蒸馏**（推荐）：使用教师模型对哲学问题生成回答，收集 `(question, teacher_answer, context_primary, context_secondary)`
- **问题设计覆盖多层次**：
  - 概念解释（基于一手文本）
  - 学术争议（基于二手文献的不同观点对比）
  - 比较研究（与其他思想家的比较）
  - 思想演进（前后期思想变化，需二手文献支撑）
- **上下文注入**：向教师模型提供清洗后的一手与二手文本作为上下文（RAG 模式）
- **来源覆盖度检查**：确保 teacher_answer 中引用的每个学者/著作都在 `source_coverage` 中有记录

## 4.4 核心模块接口

```python
class DistillFormatter:
    def to_pretrain(self, primary_texts: List[str], secondary_texts: List[str],
                    weight: float) -> List[Dict]: ...
    def to_sft(self, primary_texts: List[str], secondary_texts: List[str],
               conflicts: List[Conflict]) -> List[Dict]: ...
    def to_kd(self, qa_pairs: List[Tuple], teacher_model: str,
              contexts: Dict[str, str]) -> List[Dict]: ...
```
