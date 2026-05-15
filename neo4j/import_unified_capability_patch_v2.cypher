// Capability -> KeyCapability v2 patch
LOAD CSV WITH HEADERS FROM 'file:///unified_rel_capability_to_keycapability_v2.csv' AS row
MATCH (a:Capability {id: row.start_id})
MATCH (b:KeyCapability {id: row.end_id})
MERGE (a)-[r:MAPPED_TO]->(b)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;
