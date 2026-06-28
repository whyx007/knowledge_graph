# Neo4j 产业链挂接关系表说明

## 1. 文件清单
本目录下已生成第一版可导入 Neo4j 的关系表：

- `neo4j_enterprise_to_subtrack.csv`
- `neo4j_enterprise_to_stage.csv`
- `neo4j_enterprise_to_capability.csv`

这些文件对应三类关系：
- `Enterprise -> FOCUSES_ON_SUB_TRACK -> SubTrack`
- `Enterprise -> LOCATED_IN_STAGE -> ChainStage`
- `Enterprise -> HAS_CAPABILITY -> KeyCapability`

---

## 2. 当前适用范围
当前只包含：
- 已确认纳入三条样板产业链的企业
- 第一版已确认的主子赛道、主环节、关键能力映射

暂不包含：
- 不适用企业
- 被排除的外围配套企业
- 尚未进入正式标准口径的扩展赛道

---

## 3. 导入前提
后续如果要真正导入 Neo4j，需要先保证图谱中已有以下节点：
- `Enterprise`
- `SubTrack`
- `ChainStage`
- `KeyCapability`

并且名称口径需与当前 CSV 保持一致。

建议后续优先为这些节点补充稳定 ID，再将关系表升级为 ID 版，而不仅是名称版。

---

## 4. 当前建议用法
### 第一阶段：验证关系正确性
先用这三张表做人审或样例导入，检查：
- 企业是否挂到了合理子赛道
- 主环节是否准确
- 关键能力是否过粗/过细

### 第二阶段：生成正式 Neo4j import 文件
后续可进一步转成标准导入格式，如：
- start_id
- end_id
- relation_type
- confidence
- source

### 第三阶段：接入查询模板
导入后可直接补以下查询：
- 按子赛道看企业
- 按产业链环节找企业
- 查看企业在产业链中的位置
- 从能力反查企业与环节

---

## 5. 下一步建议
建议下一步继续做两件事：
1. 给 `SubTrack / ChainStage / KeyCapability` 补统一 ID 清单
2. 把这三张关系表改造成正式 Neo4j import 格式

这样就能从“映射表”进入“可导入图谱数据”阶段。
