// KeyCapability -> TechDirection verify v1

MATCH ()-[r:SUPPORTED_BY]->()
RETURN count(r) AS supported_by_count;

MATCH (k:KeyCapability)-[:SUPPORTED_BY]->(t:TechDirection)
RETURN k.name AS key_capability,
       collect(DISTINCT t.name) AS supporting_tech_directions
ORDER BY key_capability;
