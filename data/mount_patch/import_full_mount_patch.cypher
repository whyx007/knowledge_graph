// Full mount patch from confirmed enterprise mapping tables
LOAD CSV WITH HEADERS FROM 'file:///mount_rel_enterprise_to_subtrack_full.csv' AS row
MATCH (a:Enterprise {id: row.start_id})
MATCH (b:SubTrack {id: row.end_id})
MERGE (a)-[r:FOCUSES_ON_SUB_TRACK]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///mount_rel_enterprise_to_stage_full.csv' AS row
MATCH (a:Enterprise {id: row.start_id})
MATCH (b:ChainStage {id: row.end_id})
MERGE (a)-[r:LOCATED_IN_STAGE]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///mount_rel_enterprise_to_keycapability_full.csv' AS row
MATCH (a:Enterprise {id: row.start_id})
MATCH (b:KeyCapability {id: row.end_id})
MERGE (a)-[r:HAS_KEY_CAPABILITY]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;
