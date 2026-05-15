// TechDirection verify v1

MATCH (t:TechDirection)
RETURN count(t) AS tech_direction_count;

MATCH ()-[r:ENABLES_STAGE]->()
RETURN count(r) AS enables_stage_count;

MATCH (t:TechDirection)-[:ENABLES_STAGE]->(st:ChainStage)
RETURN t.name AS tech_direction,
       collect(DISTINCT st.name) AS enabled_stages
ORDER BY tech_direction;
