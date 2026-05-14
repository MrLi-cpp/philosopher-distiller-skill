# Phase 3.5: 观点冲突与多元性处理

哲学研究的核心特征是解释多元性。数据构建中必须保留这种张力。

## 5.1 冲突检测

- **主题聚类**：对二手文献进行主题建模（LDA / BERTopic），识别同一哲学概念的不同解读方向
- **观点对立识别**：提取含 `however`, `in contrast`, `challenge`, `critique`, `反驳`, `然而` 等转折词的段落，标记为潜在冲突区域
- **学者立场映射**：为每位二手文献作者建立立场档案

## 5.2 冲突保留策略

- **不消除冲突**：清洗和格式化时保留不同学者的对立观点
- **冲突标注**：SFT/KD 数据中使用 `[争议观点]` 标签包裹分歧论述
- **冲突配对**：KD 数据集中为同一问题生成多个含不同学者立场的样本

## 5.3 冲突输出格式

```json
{
  "topic": "柏拉图理念论的本体论地位",
  "conflicting_views": [
    {"scholar": "Julia Annas", "position": "理念是形而上学实体", "tier": 1, "source": "SEP: Plato's Ethics"},
    {"scholar": "Gail Fine", "position": "理念是解释性假设而非独立实体", "tier": 1, "source": "SEP: Plato"},
    {"scholar": "Seth Benardete", "position": "理念论是修辞性/戏剧性的表达", "tier": 2, "source": "The Rhetoric of Morality and Philosophy"}
  ]
}
```

## 5.4 核心模块接口

```python
class ConflictDetector:
    def topic_cluster(self, texts: List[str]) -> List[TopicCluster]: ...
    def detect_oppositions(self, cluster: TopicCluster) -> List[Conflict]: ...
    def build_scholar_profiles(self, texts: List[str]) -> Dict[str, ScholarProfile]: ...
```
