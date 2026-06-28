// 演示查询模板
// 用于领导演示 / 产品演示 / 方案评审
// 建议先设置参数：
// :param keyword => '机器视觉';
// :param limit => 20;

// ========================================
// 0. 按需求关键词找企业
// 适用：找“谁有类似需求 / 谁可能需要服务”
// ========================================
MATCH (e:Enterprise)-[:HAS_DEMAND]->(d:DemandTag)
WHERE d.name CONTAINS $keyword
RETURN d.name AS demand,
       collect(DISTINCT e.name)[0..coalesce($limit, 20)] AS enterprises,
       count(DISTINCT e) AS enterprise_count
ORDER BY enterprise_count DESC, demand;

// ========================================
// 1. 按行业关键词找企业
// 适用：找某行业/赛道下的企业样本
// ========================================
MATCH (e:Enterprise)-[:SERVES_INDUSTRY]->(i:Industry)
WHERE i.name CONTAINS $keyword
RETURN i.name AS industry,
       collect(DISTINCT e.name)[0..coalesce($limit, 20)] AS enterprises,
       count(DISTINCT e) AS enterprise_count
ORDER BY enterprise_count DESC, industry;

// ========================================
// 2. 按应用场景关键词找企业
// 适用：从业务场景入口定位企业
// ========================================
MATCH (e:Enterprise)-[:APPLIES_TO_SCENARIO]->(s:Scenario)
WHERE s.name CONTAINS $keyword
RETURN s.name AS scenario,
       collect(DISTINCT e.name)[0..coalesce($limit, 20)] AS enterprises,
       count(DISTINCT e) AS enterprise_count
ORDER BY enterprise_count DESC, scenario;

// ========================================
// 3. 按能力关键词找企业
// 适用：从“企业能做什么”来筛选对象
// ========================================
MATCH (e:Enterprise)-[:HAS_CAPABILITY]->(c:Capability)
WHERE c.name CONTAINS $keyword
RETURN c.name AS capability,
       collect(DISTINCT e.name)[0..coalesce($limit, 20)] AS enterprises,
       count(DISTINCT e) AS enterprise_count
ORDER BY enterprise_count DESC, capability;

// ========================================
// 4. 按产品关键词找企业（可选补充）
// 适用：从产品供给角度找企业
// ========================================
MATCH (e:Enterprise)-[:PROVIDES_PRODUCT]->(p:Product)
WHERE p.name CONTAINS $keyword
RETURN p.name AS product,
       collect(DISTINCT e.name)[0..coalesce($limit, 20)] AS enterprises,
       count(DISTINCT e) AS enterprise_count
ORDER BY enterprise_count DESC, product;

// ========================================
// 5. 多入口联合命中：同一企业在多个维度命中关键词
// 适用：演示“同一个关键词能在图谱中穿透多个维度”
// ========================================
MATCH (e:Enterprise)
OPTIONAL MATCH (e)-[:SERVES_INDUSTRY]->(i:Industry)
  WHERE i.name CONTAINS $keyword
OPTIONAL MATCH (e)-[:APPLIES_TO_SCENARIO]->(s:Scenario)
  WHERE s.name CONTAINS $keyword
OPTIONAL MATCH (e)-[:HAS_CAPABILITY]->(c:Capability)
  WHERE c.name CONTAINS $keyword
OPTIONAL MATCH (e)-[:PROVIDES_PRODUCT]->(p:Product)
  WHERE p.name CONTAINS $keyword
OPTIONAL MATCH (e)-[:HAS_DEMAND]->(d:DemandTag)
  WHERE d.name CONTAINS $keyword
WITH e,
     size(collect(DISTINCT i)) AS industry_hits,
     size(collect(DISTINCT s)) AS scenario_hits,
     size(collect(DISTINCT c)) AS capability_hits,
     size(collect(DISTINCT p)) AS product_hits,
     size(collect(DISTINCT d)) AS demand_hits
WITH e,
     industry_hits, scenario_hits, capability_hits, product_hits, demand_hits,
     (industry_hits + scenario_hits + capability_hits + product_hits + demand_hits) AS total_hits
WHERE total_hits > 0
RETURN e.name AS enterprise,
       industry_hits,
       scenario_hits,
       capability_hits,
       product_hits,
       demand_hits,
       total_hits
ORDER BY total_hits DESC, enterprise
LIMIT coalesce($limit, 20);

// ========================================
// 6. 某关键词下的重点企业跳转清单
// 适用：为下一步企业画像查询准备企业名单
// ========================================
MATCH (e:Enterprise)-[r]->(n)
WHERE coalesce(n.name, '') CONTAINS $keyword
RETURN DISTINCT e.name AS enterprise,
       collect(DISTINCT type(r))[0..10] AS matched_dimensions
ORDER BY size(matched_dimensions) DESC, enterprise
LIMIT coalesce($limit, 20);
