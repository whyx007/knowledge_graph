// Candidate Space enterprise patch v1

LOAD CSV WITH HEADERS FROM 'file:///candidate_space_rel_enterprise_to_subtrack.csv' AS row
MATCH (e:Enterprise {id: row.start_id})
MATCH (s:SubTrack {id: row.end_id})
MERGE (e)-[r:FOCUSES_ON_SUB_TRACK]->(s)
SET r.confidence = toFloat(row.confidence), r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///candidate_space_rel_enterprise_to_stage.csv' AS row
MATCH (e:Enterprise {id: row.start_id})
MATCH (st:ChainStage {id: row.end_id})
MERGE (e)-[r:LOCATED_IN_STAGE]->(st)
SET r.confidence = toFloat(row.confidence), r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///candidate_space_rel_enterprise_to_keycapability.csv' AS row
MATCH (e:Enterprise {id: row.start_id})
MATCH (k:KeyCapability {id: row.end_id})
MERGE (e)-[r:HAS_KEY_CAPABILITY]->(k)
SET r.confidence = toFloat(row.confidence), r.source = row.source;
