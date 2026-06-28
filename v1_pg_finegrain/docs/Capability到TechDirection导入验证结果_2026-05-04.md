# Capability -> TechDirection 导入验证结果（2026-05-04）

## 1. 本次结论
`Capability -> DERIVES_FROM -> TechDirection` 已完成第一版真实导入验证。

当前结果：
- DERIVES_FROM 关系数：8

说明：
- 旧 Capability 已经不只是能映射到 KeyCapability
- 其中一部分也已经能回连到更底层的 TechDirection
- 统一图谱中的“技术路线 -> 能力 -> 环节”链路开始成型

---

## 2. 本次导入文件
### 关系数据
- `data/mappings/unified_rel_capability_to_techdirection_v1.csv`

### 导入/验证脚本
- `neo4j/import_unified_capability_to_techdirection_patch_v1.cypher`
- `neo4j/verify_capability_to_techdirection_v1.cypher`

---

## 3. 已导入的 Capability -> TechDirection 关系
### 光学检测 / 机器视觉
- 单光子探测 -> 单光子探测技术
- 皮秒级时间分辨 -> 皮秒级时间分辨技术

### 光通信 / 光模块
- 片上光电集成芯片技术 -> 片上光电集成技术
- 晶体外延技术 -> 晶体外延工艺技术
- 通信光交换芯片 -> 通信光交换芯片技术

### 激光加工 / 光学装备
- 超快激光精密焊接技术 -> 超快激光精密加工技术
- 精密驱动技术 -> 精密驱动与微振动控制技术
- 空间微振动控制技术 -> 精密驱动与微振动控制技术

---

## 4. 当前图谱新增的三跳链能力
现在已经可以沿着下面的路径组织解释：

### 路径1：Capability -> TechDirection
解释“这个企业原始能力背后属于什么技术路线”。

### 路径2：TechDirection -> ENABLES_STAGE -> ChainStage
解释“这个技术路线主要支撑哪些产业链环节”。

### 路径3：Enterprise -> HAS_KEY_CAPABILITY -> KeyCapability
解释“企业当前对外呈现为哪些可交付能力”。

这意味着，后续可以把推荐理由从“关键词像”升级为：
- 企业具备某类能力
- 该能力背后依托某个技术方向
- 该技术方向支撑某个产业链环节
- 因此推荐逻辑更可解释

---

## 5. 当前仍未补的链路
1. Capability 与 KeyCapability 并非全部一一齐备
2. KeyCapability 与 TechDirection 之间还没有显式关系
3. Enterprise 还没有直接挂接 TechDirection

因此当前更像是：
- 企业视角已能走到能力层
- 技术视角已能走到环节层
- 但中间还有继续补强空间

---

## 6. 下一步建议
1. 考虑建立 `KeyCapability -> SUPPORTED_BY -> TechDirection`
2. 再决定是否需要 `Enterprise -> USES_TECH_DIRECTION -> TechDirection`
3. 用现有三跳链设计一版可解释推荐查询模板

---

## 7. 一句话结论

> 统一图谱现在已经从“企业-能力-环节”结构，进一步长出了“技术路线”这一层，可开始支持更强的解释链。
