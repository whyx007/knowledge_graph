// Capability -> TechDirection import patch v1
LOAD CSV WITH HEADERS FROM 'file:///unified_rel_capability_to_techdirection_v1.csv' AS row
MATCH (c:Capability {id: row.start_id})
MATCH (t:TechDirection {id: row.end_id})
MERGE (c)-[r:DERIVES_FROM]->(t)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;
