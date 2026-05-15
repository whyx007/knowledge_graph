MATCH (e:Enterprise)-[:FOCUSES_ON_SUB_TRACK]->(s:SubTrack)
RETURN s.name AS sub_track, count(DISTINCT e) AS enterprise_count
ORDER BY enterprise_count DESC, sub_track;

MATCH (e:Enterprise {name: '中科慧远视觉技术（洛阳）有限公司'})
OPTIONAL MATCH (e)-[:FOCUSES_ON_SUB_TRACK]->(s:SubTrack)
OPTIONAL MATCH (e)-[:LOCATED_IN_STAGE]->(st:ChainStage)
OPTIONAL MATCH (e)-[:HAS_KEY_CAPABILITY]->(k:KeyCapability)
RETURN e.name AS enterprise,
       collect(DISTINCT s.name) AS sub_tracks,
       collect(DISTINCT st.name) AS stages,
       collect(DISTINCT k.name) AS key_capabilities;
