// Candidate Space verify v1

MATCH (s:SubTrack {id: 'SUB_SPACE_001'}) RETURN count(s) AS subtrack_count;
MATCH (c:ChainStage) WHERE c.id STARTS WITH 'STG_SPACE_' RETURN count(c) AS stage_count;
MATCH (k:KeyCapability) WHERE k.id STARTS WITH 'KCAP_SPACE_' RETURN count(k) AS keycap_count;
MATCH (a:ApplicationScenario) WHERE a.id STARTS WITH 'ASCN_SPACE_' RETURN count(a) AS appscenario_count;
MATCH (t:TechDirection) WHERE t.id STARTS WITH 'TD_SPACE_' RETURN count(t) AS techdirection_count;

MATCH (:SubTrack {id: 'SUB_SPACE_001'})-[r:HAS_STAGE]->(:ChainStage) RETURN count(r) AS has_stage_count;
MATCH ()-[r:UPSTREAM_OF]->() WHERE startNode(r).id STARTS WITH 'STG_SPACE_' RETURN count(r) AS upstream_of_count;
MATCH ()-[r:REQUIRES_CAPABILITY]->() WHERE startNode(r).id STARTS WITH 'STG_SPACE_' RETURN count(r) AS requires_capability_count;
MATCH ()-[r:DRIVES_STAGE]->() WHERE startNode(r).id STARTS WITH 'ASCN_SPACE_' RETURN count(r) AS drives_stage_count;
MATCH ()-[r:ENABLES_STAGE]->() WHERE startNode(r).id STARTS WITH 'TD_SPACE_' RETURN count(r) AS enables_stage_count;

MATCH (t:TechDirection)-[:ENABLES_STAGE]->(st:ChainStage)
WHERE t.id STARTS WITH 'TD_SPACE_'
RETURN t.name AS tech_direction,
       collect(DISTINCT st.name) AS enabled_stages
ORDER BY tech_direction;
