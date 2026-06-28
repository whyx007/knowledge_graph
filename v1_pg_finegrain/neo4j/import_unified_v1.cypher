// Unified graph import v1
// 说明：
// 1) 先确保已执行 neo4j/schema.cypher 与 neo4j/schema_unified_v1.cypher
// 2) 旧企业图谱节点/关系已导入，当前脚本只补统一图谱增量节点与关系
// 3) 文件路径基于 Neo4j import 目录，可按实际部署修改

// ========================================
// A. 统一图谱节点导入
// ========================================

LOAD CSV WITH HEADERS FROM 'file:///unified_subtracks.csv' AS row
MERGE (d:IndustryDomain {id: row.domain_id})
  ON CREATE SET d.name = row.domain_name
MERGE (s:SubTrack {id: row.sub_track_id})
SET s.name = row.sub_track_name,
    s.description = row.sub_track_description
MERGE (d)-[:HAS_SUB_TRACK]->(s);

LOAD CSV WITH HEADERS FROM 'file:///unified_chain_stages.csv' AS row
MERGE (s:SubTrack {id: row.sub_track_id})
MERGE (c:ChainStage {id: row.stage_id})
SET c.name = row.stage_name,
    c.stage_order = toInteger(row.stage_order),
    c.stage_level = row.stage_level,
    c.stage_category = row.stage_category,
    c.sub_track_id = row.sub_track_id;

LOAD CSV WITH HEADERS FROM 'file:///unified_key_capabilities.csv' AS row
MERGE (s:SubTrack {id: row.sub_track_id})
MERGE (k:KeyCapability {id: row.capability_id})
SET k.name = row.capability_name,
    k.description = row.description,
    k.sub_track_id = row.sub_track_id;

LOAD CSV WITH HEADERS FROM 'file:///unified_application_scenarios.csv' AS row
MERGE (s:SubTrack {id: row.sub_track_id})
MERGE (a:ApplicationScenario {id: row.scenario_id})
SET a.name = row.scenario_name,
    a.description = row.description,
    a.sub_track_id = row.sub_track_id;

// ========================================
// B. 统一图谱结构关系导入
// ========================================

LOAD CSV WITH HEADERS FROM 'file:///unified_rel_subtrack_to_stage.csv' AS row
MATCH (a:SubTrack {id: row.start_id})
MATCH (b:ChainStage {id: row.end_id})
MERGE (a)-[r:HAS_STAGE]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///unified_rel_stage_to_stage.csv' AS row
MATCH (a:ChainStage {id: row.start_id})
MATCH (b:ChainStage {id: row.end_id})
MERGE (a)-[r:UPSTREAM_OF]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///unified_rel_stage_to_keycapability.csv' AS row
MATCH (a:ChainStage {id: row.start_id})
MATCH (b:KeyCapability {id: row.end_id})
MERGE (a)-[r:REQUIRES_CAPABILITY]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///unified_rel_appscenario_to_stage.csv' AS row
MATCH (a:ApplicationScenario {id: row.start_id})
MATCH (b:ChainStage {id: row.end_id})
MERGE (a)-[r:DRIVES_STAGE]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;

// ========================================
// C. 企业挂接关系导入
// ========================================

LOAD CSV WITH HEADERS FROM 'file:///unified_rel_enterprise_to_subtrack.csv' AS row
MATCH (a:Enterprise {id: row.start_id})
MATCH (b:SubTrack {id: row.end_id})
MERGE (a)-[r:FOCUSES_ON_SUB_TRACK]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///unified_rel_enterprise_to_stage.csv' AS row
MATCH (a:Enterprise {id: row.start_id})
MATCH (b:ChainStage {id: row.end_id})
MERGE (a)-[r:LOCATED_IN_STAGE]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///unified_rel_enterprise_to_keycapability.csv' AS row
MATCH (a:Enterprise {id: row.start_id})
MATCH (b:KeyCapability {id: row.end_id})
MERGE (a)-[r:HAS_KEY_CAPABILITY]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;

// ========================================
// D. 预留：旧图谱到统一图谱映射层导入
// ========================================
// 取消注释前，请先准备下列 CSV：
// - unified_rel_capability_to_keycapability.csv
// - unified_rel_scenario_to_appscenario.csv

/*
LOAD CSV WITH HEADERS FROM 'file:///unified_rel_capability_to_keycapability.csv' AS row
MATCH (a:Capability {id: row.start_id})
MATCH (b:KeyCapability {id: row.end_id})
MERGE (a)-[r:MAPPED_TO]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///unified_rel_scenario_to_appscenario.csv' AS row
MATCH (a:Scenario {id: row.start_id})
MATCH (b:ApplicationScenario {id: row.end_id})
MERGE (a)-[r:MAPPED_TO]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;
*/

// ========================================
// E. 导入后快速检查
// ========================================
// MATCH (n:SubTrack) RETURN count(n);
// MATCH (n:ChainStage) RETURN count(n);
// MATCH (n:KeyCapability) RETURN count(n);
// MATCH (n:ApplicationScenario) RETURN count(n);
// MATCH ()-[r:HAS_STAGE]->() RETURN count(r);
// MATCH ()-[r:UPSTREAM_OF]->() RETURN count(r);
// MATCH ()-[r:REQUIRES_CAPABILITY]->() RETURN count(r);
// MATCH ()-[r:DRIVES_STAGE]->() RETURN count(r);
