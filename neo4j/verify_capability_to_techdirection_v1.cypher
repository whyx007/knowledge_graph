// Capability -> TechDirection verify v1

MATCH ()-[r:DERIVES_FROM]->()
RETURN count(r) AS derives_from_count;

MATCH (c:Capability)-[:DERIVES_FROM]->(t:TechDirection)
RETURN c.name AS capability,
       t.name AS tech_direction
ORDER BY tech_direction, capability;
