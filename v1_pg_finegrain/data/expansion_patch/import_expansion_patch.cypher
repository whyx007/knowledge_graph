// expansion patch: 光显示 / 光计算 / 光融合（量子光学新原理）
LOAD CSV WITH HEADERS FROM 'file:///expansion_subtracks.csv' AS row
MERGE (d:IndustryDomain {id: row.domain_id})
  ON CREATE SET d.name = row.domain_name
MERGE (s:SubTrack {id: row.sub_track_id})
SET s.name = row.sub_track_name,
    s.description = row.sub_track_description
MERGE (d)-[:HAS_SUB_TRACK]->(s);

LOAD CSV WITH HEADERS FROM 'file:///expansion_chain_stages.csv' AS row
MERGE (s:SubTrack {id: row.sub_track_id})
MERGE (c:ChainStage {id: row.stage_id})
SET c.name = row.stage_name,
    c.stage_order = toInteger(row.stage_order),
    c.stage_level = row.stage_level,
    c.stage_category = row.stage_category,
    c.sub_track_id = row.sub_track_id;

LOAD CSV WITH HEADERS FROM 'file:///expansion_key_capabilities.csv' AS row
MERGE (s:SubTrack {id: row.sub_track_id})
MERGE (k:KeyCapability {id: row.capability_id})
SET k.name = row.capability_name,
    k.description = row.description,
    k.sub_track_id = row.sub_track_id;

LOAD CSV WITH HEADERS FROM 'file:///expansion_application_scenarios.csv' AS row
MERGE (s:SubTrack {id: row.sub_track_id})
MERGE (a:ApplicationScenario {id: row.scenario_id})
SET a.name = row.scenario_name,
    a.description = row.description,
    a.sub_track_id = row.sub_track_id;

LOAD CSV WITH HEADERS FROM 'file:///expansion_rel_subtrack_to_stage.csv' AS row
MATCH (a:SubTrack {id: row.start_id})
MATCH (b:ChainStage {id: row.end_id})
MERGE (a)-[r:HAS_STAGE]->(b)
SET r.confidence = toFloat(row.confidence), r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///expansion_rel_stage_to_stage.csv' AS row
MATCH (a:ChainStage {id: row.start_id})
MATCH (b:ChainStage {id: row.end_id})
MERGE (a)-[r:UPSTREAM_OF]->(b)
SET r.confidence = toFloat(row.confidence), r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///expansion_rel_stage_to_keycapability.csv' AS row
MATCH (a:ChainStage {id: row.start_id})
MATCH (b:KeyCapability {id: row.end_id})
MERGE (a)-[r:REQUIRES_CAPABILITY]->(b)
SET r.confidence = toFloat(row.confidence), r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///expansion_rel_appscenario_to_stage.csv' AS row
MATCH (a:ApplicationScenario {id: row.start_id})
MATCH (b:ChainStage {id: row.end_id})
MERGE (a)-[r:DRIVES_STAGE]->(b)
SET r.confidence = toFloat(row.confidence), r.source = row.source;
