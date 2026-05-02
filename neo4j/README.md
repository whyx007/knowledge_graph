# Neo4j 本地运行与导入说明

## 当前本地环境
### Neo4j Desktop
- 安装路径：`E:\Software\Neo4j`

### 本地可运行 DBMS 副本
为避免安装目录权限问题，实际运行副本放在：
- `E:\Software\Neo4jLocal\neo4j-enterprise-2026.03.1`

### Java Runtime
当前实际使用 Neo4j Desktop 自带的 Java 21 运行时：
- `E:\Software\Neo4j\resources\offline\runtime\zulu21.48.17-ca-jre21.0.10-win_x64`

## 当前导入结果
### 节点数
- Enterprise: 375
- Product: 1347
- Capability: 1340
- Industry: 1118
- Scenario: 1372
- Customer: 508
- Supplier: 805
- DemandTag: 623

### 关系数
- PROVIDES_PRODUCT: 1369
- HAS_CAPABILITY: 1357
- SERVES_INDUSTRY: 1440
- APPLIES_TO_SCENARIO: 1400
- HAS_CUSTOMER: 563
- HAS_SUPPLIER: 1051
- HAS_DEMAND: 689

## 导入文件
位于工作区：
- `data/neo4j/neo4j_enterprise_nodes.csv`
- `data/neo4j/neo4j_entity_nodes.csv`
- `data/neo4j/neo4j_relationships.csv`

并已复制到本地运行 DBMS 的 import 目录：
- `E:\Software\Neo4jLocal\neo4j-enterprise-2026.03.1\import`

## 相关脚本
- schema: `neo4j/schema.cypher`
- 关系导入（无 APOC）: `neo4j/import_relationships_no_apoc.cypher`
- 示例查询: `neo4j/sample_queries.cypher`

## 启动方式
使用当前终端临时环境变量：

```powershell
$env:JAVA_HOME='E:\Software\Neo4j\resources\offline\runtime\zulu21.48.17-ca-jre21.0.10-win_x64'
$env:PATH="$env:JAVA_HOME\bin;" + $env:PATH
$dbms='E:\Software\Neo4jLocal\neo4j-enterprise-2026.03.1'
& "$dbms\bin\neo4j.bat" console
```

说明：当前以 `console` 方式运行最稳，适合原型验证。

## 示例查询
### 1. 统计节点
```cypher
MATCH (n)
RETURN labels(n) AS labels, count(*) AS cnt
ORDER BY cnt DESC;
```

### 2. 统计关系
```cypher
MATCH ()-[r]->()
RETURN type(r) AS rel_type, count(*) AS cnt
ORDER BY cnt DESC;
```

### 3. 企业画像
```cypher
MATCH (e:Enterprise {name: $name})
OPTIONAL MATCH (e)-[:PROVIDES_PRODUCT]->(p:Product)
OPTIONAL MATCH (e)-[:SERVES_INDUSTRY]->(i:Industry)
OPTIONAL MATCH (e)-[:APPLIES_TO_SCENARIO]->(s:Scenario)
OPTIONAL MATCH (e)-[:HAS_DEMAND]->(d:DemandTag)
RETURN e.name AS enterprise,
       collect(DISTINCT p.name)[0..20] AS products,
       collect(DISTINCT i.name)[0..20] AS industries,
       collect(DISTINCT s.name)[0..20] AS scenarios,
       collect(DISTINCT d.name)[0..20] AS demands;
```

### 4. 按行业找企业
```cypher
MATCH (e:Enterprise)-[:SERVES_INDUSTRY]->(i:Industry)
WHERE i.name CONTAINS $keyword
RETURN i.name AS industry, collect(DISTINCT e.name)[0..50] AS enterprises
ORDER BY industry;
```

### 5. 按需求找企业
```cypher
MATCH (e:Enterprise)-[:HAS_DEMAND]->(d:DemandTag)
WHERE d.name CONTAINS $keyword
RETURN d.name AS demand, collect(DISTINCT e.name)[0..50] AS enterprises
ORDER BY demand;
```
