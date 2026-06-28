// 企业画像查询模板
// 适用于当前企业知识图谱第一版
// 建议先设置参数：
// :param name => '某某企业';
// :param keyword => '机器视觉';
// :param limit => 20;

// ========================================
// 0. 企业名称模糊定位
// 用途：当企业全称不确定时，先缩小范围
// ========================================
MATCH (e:Enterprise)
WHERE e.name CONTAINS $keyword
OPTIONAL MATCH (e)-[:PROVIDES_PRODUCT]->(p:Product)
OPTIONAL MATCH (e)-[:SERVES_INDUSTRY]->(i:Industry)
OPTIONAL MATCH (e)-[:APPLIES_TO_SCENARIO]->(s:Scenario)
OPTIONAL MATCH (e)-[:HAS_DEMAND]->(d:DemandTag)
RETURN e.name AS enterprise,
       coalesce(e.intro, '') AS intro,
       size(collect(DISTINCT p)) AS product_count,
       size(collect(DISTINCT i)) AS industry_count,
       size(collect(DISTINCT s)) AS scenario_count,
       size(collect(DISTINCT d)) AS demand_count
ORDER BY product_count + industry_count + scenario_count + demand_count DESC, enterprise
LIMIT coalesce($limit, 20);

// ========================================
// 1. 单企业基础画像
// ========================================
MATCH (e:Enterprise {name: $name})
OPTIONAL MATCH (e)-[:PROVIDES_PRODUCT]->(p:Product)
OPTIONAL MATCH (e)-[:SERVES_INDUSTRY]->(i:Industry)
OPTIONAL MATCH (e)-[:APPLIES_TO_SCENARIO]->(s:Scenario)
OPTIONAL MATCH (e)-[:HAS_DEMAND]->(d:DemandTag)
RETURN e.name AS enterprise,
       coalesce(e.intro, '') AS intro,
       collect(DISTINCT p.name)[0..20] AS products,
       collect(DISTINCT i.name)[0..20] AS industries,
       collect(DISTINCT s.name)[0..20] AS scenarios,
       collect(DISTINCT d.name)[0..20] AS demands;

// ========================================
// 2. 企业综合画像（产品/能力/行业/场景/需求）
// ========================================
MATCH (e:Enterprise {name: $name})
OPTIONAL MATCH (e)-[:PROVIDES_PRODUCT]->(p:Product)
OPTIONAL MATCH (e)-[:HAS_CAPABILITY]->(c:Capability)
OPTIONAL MATCH (e)-[:SERVES_INDUSTRY]->(i:Industry)
OPTIONAL MATCH (e)-[:APPLIES_TO_SCENARIO]->(s:Scenario)
OPTIONAL MATCH (e)-[:HAS_DEMAND]->(d:DemandTag)
RETURN e.name AS enterprise,
       collect(DISTINCT p.name)[0..30] AS products,
       collect(DISTINCT c.name)[0..30] AS capabilities,
       collect(DISTINCT i.name)[0..30] AS industries,
       collect(DISTINCT s.name)[0..30] AS scenarios,
       collect(DISTINCT d.name)[0..30] AS demands;

// ========================================
// 3. 企业客户/供应商生态
// ========================================
MATCH (e:Enterprise {name: $name})
OPTIONAL MATCH (e)-[:HAS_CUSTOMER]->(c:Customer)
OPTIONAL MATCH (e)-[:HAS_SUPPLIER]->(s:Supplier)
RETURN e.name AS enterprise,
       collect(DISTINCT c.name)[0..30] AS customers,
       collect(DISTINCT s.name)[0..30] AS suppliers,
       size(collect(DISTINCT c)) AS customer_count,
       size(collect(DISTINCT s)) AS supplier_count;

// ========================================
// 4. 企业标签热度概览
// 用途：快速判断画像完备度
// ========================================
MATCH (e:Enterprise {name: $name})
OPTIONAL MATCH (e)-[:PROVIDES_PRODUCT]->(p:Product)
OPTIONAL MATCH (e)-[:HAS_CAPABILITY]->(c:Capability)
OPTIONAL MATCH (e)-[:SERVES_INDUSTRY]->(i:Industry)
OPTIONAL MATCH (e)-[:APPLIES_TO_SCENARIO]->(s:Scenario)
OPTIONAL MATCH (e)-[:HAS_DEMAND]->(d:DemandTag)
OPTIONAL MATCH (e)-[:HAS_CUSTOMER]->(cu:Customer)
OPTIONAL MATCH (e)-[:HAS_SUPPLIER]->(su:Supplier)
RETURN e.name AS enterprise,
       size(collect(DISTINCT p)) AS product_count,
       size(collect(DISTINCT c)) AS capability_count,
       size(collect(DISTINCT i)) AS industry_count,
       size(collect(DISTINCT s)) AS scenario_count,
       size(collect(DISTINCT d)) AS demand_count,
       size(collect(DISTINCT cu)) AS customer_count,
       size(collect(DISTINCT su)) AS supplier_count;

// ========================================
// 5. 企业一跳图谱展示
// 用途：Neo4j Browser 图形化演示
// ========================================
MATCH (e:Enterprise {name: $name})-[r]->(n)
RETURN e, r, n
LIMIT coalesce($limit, 30);

// ========================================
// 6. 企业 + 关键词关联项定位
// 用途：查看某企业在特定关键词下命中了哪些标签
// ========================================
MATCH (e:Enterprise {name: $name})-[r]->(n)
WHERE coalesce(n.name, '') CONTAINS $keyword
RETURN e.name AS enterprise,
       type(r) AS relation,
       labels(n) AS target_labels,
       n.name AS target_name
ORDER BY relation, target_name
LIMIT coalesce($limit, 30);
