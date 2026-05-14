LOAD CSV WITH HEADERS FROM 'file:///fusion_fix_lide_subtrack.csv' AS row
MATCH (a:Enterprise {id: row.start_id})
MATCH (b:SubTrack {id: row.end_id})
MERGE (a)-[r:FOCUSES_ON_SUB_TRACK]->(b)
SET r.confidence = toFloat(row.confidence), r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///fusion_fix_lide_stage.csv' AS row
MATCH (a:Enterprise {id: row.start_id})
MATCH (b:ChainStage {id: row.end_id})
MERGE (a)-[r:LOCATED_IN_STAGE]->(b)
SET r.confidence = toFloat(row.confidence), r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///fusion_fix_lide_keycap.csv' AS row
MATCH (a:Enterprise {id: row.start_id})
MATCH (b:KeyCapability {id: row.end_id})
MERGE (a)-[r:HAS_KEY_CAPABILITY]->(b)
SET r.confidence = toFloat(row.confidence), r.source = row.source;
