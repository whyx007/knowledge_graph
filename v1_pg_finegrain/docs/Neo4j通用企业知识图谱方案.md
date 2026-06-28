# Neo4j 通用企业知识图谱方案

## 1. 目标
采用**通用、可复用**的方法，把企业类 Excel/CSV 数据转换为 Neo4j 可导入的知识图谱数据，而不是为单个表硬编码一次性脚本。

这套方案适用于：
- 当前 `企业信息暂存.xlsx`
- 后续结构相近的企业库、被投企业表、服务台账
- 未来增加字段后的扩展版本

---

## 2. 方法原则

### 2.1 通用优先
不要把字段名写死在代码里。
用“**配置驱动**”方式处理：
- 哪个字段是企业名称
- 哪些字段映射成节点
- 哪些字段映射成关系
- 哪些字段只是企业属性

都放到配置文件中。

### 2.2 先标准化，再导入 Neo4j
流程固定为四层：
1. 原始 Excel / CSV
2. 标准化中间表（nodes / relationships）
3. Neo4j CSV 导入文件
4. Neo4j 图数据库

### 2.3 企业为中心
第一版图谱先围绕 `Enterprise` 作为中心节点展开，其他实体通过关系挂上去。

---

## 3. 推荐图谱模型

### 3.1 节点标签
- `Enterprise`：企业
- `Product`：产品
- `Capability`：技术/能力
- `Industry`：行业
- `Scenario`：应用场景
- `Customer`：客户
- `Supplier`：供应商
- `DemandTag`：需求标签

### 3.2 关系类型
- `PROVIDES_PRODUCT`
- `HAS_CAPABILITY`
- `SERVES_INDUSTRY`
- `APPLIES_TO_SCENARIO`
- `HAS_CUSTOMER`
- `HAS_SUPPLIER`
- `HAS_DEMAND`

### 3.3 企业属性
建议先挂在 `Enterprise` 节点上的属性：
- `name`
- `intro`
- `business_model`
- `certification_ip`
- `founder_team`
- `revenue_financing`
- `advantage`
- `match_level`
- `source_file`
- `row_no`

---

## 4. 通用目录建议

```text
workspace-kg-prototype/
  config/
    field_mapping.template.json
  data/
    raw/
    processed/
    neo4j/
  scripts/
    build_enterprise_graph.py
  neo4j/
    schema.cypher
    import.cypher
  docs/
    Neo4j通用企业知识图谱方案.md
```

---

## 5. 通用处理流程

### 第一步：准备原始文件
把原始企业 Excel 放入：
- `data/raw/`

当前可直接使用：
- `data/企业信息暂存.xlsx`

### 第二步：配置字段映射
在 `config/field_mapping.template.json` 中配置：
- 企业主键字段
- 企业属性字段
- 哪些字段拆成节点
- 对应节点标签和关系类型

### 第三步：运行通用脚本
脚本会输出三类文件：
1. `enterprise_nodes.csv`
2. `entity_nodes.csv`
3. `relationships.csv`

并额外输出 Neo4j 导入版：
1. `neo4j_enterprise_nodes.csv`
2. `neo4j_entity_nodes.csv`
3. `neo4j_relationships.csv`

### 第四步：执行 Neo4j schema
先创建唯一约束和索引。

### 第五步：导入 CSV
使用 `LOAD CSV` 导入到 Neo4j。

---

## 6. 为什么这套方法是“通用的”

因为代码不依赖固定中文字段名，而是依赖配置：
- 你以后换成别的企业台账，只改配置文件
- 新增一个“合作伙伴”字段，也只需要新增一条配置
- 要把“认证”从属性升级成节点，也只需要改配置和少量逻辑

这就是从“单次清洗脚本”升级为“可复用图谱构建管道”。

---

## 7. 导入 Neo4j 的两种方式

### 方式 A：LOAD CSV
适合第一版原型，最简单。

优点：
- 直观
- 易调试
- 适合小中规模数据

### 方式 B：neo4j-admin import
适合后期大批量全量导入。

当前建议先用 **LOAD CSV**。

---

## 8. 本期建议交付

### 必做
- 通用字段映射配置文件
- 通用 Python 构建脚本
- Neo4j schema 文件
- Neo4j import 文件
- 第一版 CSV 输出

### 选做
- 数据质量检查报告
- 实体标准化词典
- 场景/行业同义词归一规则

---

## 9. 下一步执行建议

你现在最应该做的是：
1. 确认 Neo4j 作为承载库
2. 固化通用映射配置
3. 跑第一版构图脚本
4. 导入 Neo4j 验证查询

一句话：
**先把企业图谱构建流程做成“配置化 + 可重复运行”的 Neo4j 数据管道。**
