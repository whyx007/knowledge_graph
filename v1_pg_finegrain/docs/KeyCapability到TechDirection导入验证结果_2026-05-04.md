# KeyCapability -> TechDirection 导入验证结果（2026-05-04）

## 1. 本次结论
`KeyCapability -> SUPPORTED_BY -> TechDirection` 已完成第一版真实导入验证。

当前结果：
- SUPPORTED_BY 关系数：7

说明：
- KeyCapability 层已经不再孤立
- 它现在可以明确挂到更底层的技术路线层
- 统一图谱中的“技术路线 -> 关键能力 -> 企业能力呈现”链条开始闭环

---

## 2. 本次导入文件
### 关系数据
- `data/mappings/unified_rel_keycapability_to_techdirection_v1.csv`

### 导入/验证脚本
- `neo4j/import_unified_keycapability_to_techdirection_patch_v1.cypher`
- `neo4j/verify_keycapability_to_techdirection_v1.cypher`

---

## 3. 已导入的 KeyCapability -> TechDirection 关系
### 光学检测 / 机器视觉
- 成像方案设计能力 -> 单光子探测技术
- 成像方案设计能力 -> 皮秒级时间分辨技术

### 光通信 / 光模块
- 高速模块设计能力 -> 片上光电集成技术
- 高速模块设计能力 -> 晶体外延工艺技术
- 高速模块设计能力 -> 通信光交换芯片技术

### 激光加工 / 光学装备
- 激光工艺适配能力 -> 超快激光精密加工技术
- 高精度加工控制能力 -> 精密驱动与微振动控制技术

---

## 4. 当前统一图谱新增的解释链闭环
当前至少已经具备以下几段链路：

1. `Capability -> DERIVES_FROM -> TechDirection`
2. `KeyCapability -> SUPPORTED_BY -> TechDirection`
3. `TechDirection -> ENABLES_STAGE -> ChainStage`
4. `Enterprise -> HAS_KEY_CAPABILITY -> KeyCapability`

这意味着后续可以组织出更完整的解释路径，例如：
- 某企业具备“高精度加工控制能力”
- 该能力由“精密驱动与微振动控制技术”支撑
- 该技术主要支撑“振镜/加工头/执行单元”等产业链环节
- 因而企业在该环节具备更强的可解释优势

---

## 5. 当前仍未补的点
1. `Enterprise -> USES_TECH_DIRECTION` 尚未建立
2. 并非所有 KeyCapability 都已挂上 TechDirection
3. 光学检测方向目前更多是成像类技术，算法类 TechDirection 仍偏少
4. 激光加工方向还可以继续补工艺包/光路匹配等技术主题

---

## 6. 下一步建议
1. 基于现有链路写一版“可解释推荐查询模板”
2. 再决定是否需要 `Enterprise -> USES_TECH_DIRECTION`
3. 继续扩充算法类 / 工艺包类 / 光路类 TechDirection

---

## 7. 一句话结论

> 统一图谱现在已经不是简单的企业标签网络，而是开始具备“技术路线—关键能力—产业环节—企业能力”的解释链闭环。
