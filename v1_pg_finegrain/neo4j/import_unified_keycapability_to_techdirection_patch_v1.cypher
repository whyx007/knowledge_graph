// KeyCapability -> TechDirection import patch v1
LOAD CSV WITH HEADERS FROM 'file:///unified_rel_keycapability_to_techdirection_v1.csv' AS row
MATCH (k:KeyCapability {id: row.start_id})
MATCH (t:TechDirection {id: row.end_id})
MERGE (k)-[r:SUPPORTED_BY]->(t)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;
