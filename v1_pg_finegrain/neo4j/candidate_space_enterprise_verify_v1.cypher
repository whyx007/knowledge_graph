// Candidate Space enterprise verify v1

MATCH (e:Enterprise)-[:FOCUSES_ON_SUB_TRACK]->(s:SubTrack {id: 'SUB_SPACE_001'})
RETURN count(DISTINCT e) AS enterprise_count;

MATCH (e:Enterprise)-[:FOCUSES_ON_SUB_TRACK]->(s:SubTrack {id: 'SUB_SPACE_001'})
OPTIONAL MATCH (e)-[:LOCATED_IN_STAGE]->(st:ChainStage)
OPTIONAL MATCH (e)-[:HAS_KEY_CAPABILITY]->(k:KeyCapability)
RETURN e.name AS enterprise,
       collect(DISTINCT st.name) AS stages,
       collect(DISTINCT k.name) AS key_capabilities
ORDER BY enterprise;
