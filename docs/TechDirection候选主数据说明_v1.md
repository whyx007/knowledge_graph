# TechDirection 候选主数据说明（v1）

对应文件：
- `data/mappings/unified_tech_directions_candidates_v1.csv`
- `data/mappings/unified_rel_techdirection_to_stage_candidates_v1.csv`

## 1. 目的
这份候选主数据用于把低置信 Capability 中更像“技术主题/工艺路线/底层原理”的内容，从 KeyCapability 层拆出来，正式沉淀到统一图谱第 4 层的 `TechDirection` 候选池。

---

## 2. 本轮纳入的候选技术方向
### 光学检测 / 机器视觉
- 单光子探测技术
- 皮秒级时间分辨技术

### 光通信 / 光模块
- 片上光电集成技术
- 晶体外延工艺技术
- 通信光交换芯片技术

---

## 3. 为什么它们更适合 TechDirection
这些对象有几个共同特点：
1. 更像底层技术路线，而不是可直接交付给客户的能力
2. 往往对应上游工艺、器件、探测原理、芯片架构
3. 如果硬映射到 KeyCapability，会让“能力层”混入大量技术名词，削弱推荐解释性

因此更合理的分层是：
- TechDirection：回答“企业基于什么核心技术路线”
- KeyCapability：回答“企业能交付什么能力”

---

## 4. 为什么要补 `ENABLES_STAGE`
只建 TechDirection 节点还不够，必须说明它对产业链的作用位置。

所以本轮额外补了：
- `TechDirection -> ENABLES_STAGE -> ChainStage`

这样后续可以回答：
- 某个技术方向主要支撑哪个环节？
- 某个环节背后有哪些核心技术方向？
- 某企业的旧 Capability 更应归到技术方向层还是能力层？

---

## 5. 当前仍是候选，不是正式主数据
注意：
- 这批文件当前是 `candidates_v1`
- 说明它们已经适合进入统一图谱设计，但还没作为正式导入主数据写入 schema / import 脚本主流程
- 下一步需要先人工确认，再决定是否生成正式 `unified_tech_directions.csv`

---

## 6. 下一步建议
1. 继续补 TechDirection 候选，尤其是激光加工方向
2. 生成正式版 `unified_tech_directions_v1.csv`
3. 生成 `import_unified_techdirection_patch_v1.cypher`
4. 导入 Neo4j 做一次结构层验证

---

## 7. 一句话结论

> TechDirection 这层现在已经从“物理模型里的占位概念”，推进成了“有候选主数据、有候选环节挂接”的可落地对象。
